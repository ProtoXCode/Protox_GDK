from __future__ import annotations

from typing import Optional

import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk
from PIL.Image import Resampling


class CanvasView:
    """Encapsulates the drawing canvas and preview rendering logic."""

    def __init__(self, editor: "SpriteEditor") -> None:
        self.editor = editor
        self.cell_px = 22
        self.canvas: Optional[ctk.CTkCanvas] = None
        self.canvas_img_id: Optional[int] = None
        self._canvas_img: Optional[ImageTk.PhotoImage] = None
        self.preview_label: Optional[ctk.CTkLabel] = None
        self._preview_photo: Optional[ctk.CTkImage] = None
        self.max_size = 256

    def build(self, parent: ctk.CTkFrame) -> None:
        """ Create the canvas area with scrollbars and mouse bindings. """
        center = ctk.CTkFrame(parent)
        center.grid(row=1, column=1, sticky='nsew',
                    padx=(0, self.editor.padding), pady=self.editor.padding)
        center.rowconfigure(0, weight=1)
        center.columnconfigure(0, weight=1)

        x_scroll = ctk.CTkScrollbar(center, orientation='horizontal')
        y_scroll = ctk.CTkScrollbar(center, orientation='vertical')
        x_scroll.grid(row=1, column=0, sticky='ew')
        y_scroll.grid(row=0, column=1, sticky='ns')

        self.canvas = ctk.CTkCanvas(
            center,
            bg='#1a1a1a',
            highlightthickness=0,
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
        )
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.canvas_img_id = self.canvas.create_image(0, 0, anchor='nw')

        x_scroll.configure(command=self.canvas.xview)
        y_scroll.configure(command=self.canvas.yview)

        def _on_mouse_wheel(event) -> None:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        self.canvas.bind_all('<MouseWheel>', _on_mouse_wheel)

        def _start_pan(event) -> None:
            self.canvas.scan_mark(event.x, event.y)

        def _do_pan(event) -> None:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

        # --- Panning ---
        self.canvas.bind('<ButtonPress-2>', _start_pan)
        self.canvas.bind('<B2-Motion>', _do_pan)

        # --- Painting ---
        self.canvas.bind('<Button-1>', self.paint_at)
        self.canvas.bind('<B1-Motion>', self.paint_at)
        self.canvas.bind('<Button-3>', self.eyedrop_at)

    def set_preview_label(self, label: ctk.CTkLabel) -> None:
        self.preview_label = label

    def redraw_canvas(self, *_args) -> None:
        """
        Redraw the entire sprite grid on the canvas.

        Re-renders the active frame’s pixel matrix into the offscreen
        `PhotoImage`, optionally overlaying the previous frame as an
        onion-skin layer for animation guidance.

        Also:
          - Regenerates grid lines based on `self.cell_px`
          - Updates the canvas scrollregion to match the new image size
          - Ensures consistent redraws after zoom or paint actions
        """
        if not self.canvas:
            return

        if self.canvas_img_id is None:
            self.canvas_img_id = self.canvas.create_image(0, 0, anchor='nw')

        doc = self.editor.doc
        width_px = doc.width * self.cell_px
        height_px = doc.height * self.cell_px
        self.canvas.configure(width=width_px, height=height_px)
        self.canvas.delete('grid')

        base = self._compose_frame_with_onion_skin(doc)

        if self.cell_px != 1:
            base = base.resize(
                (doc.width * self.cell_px, doc.height * self.cell_px),
                Resampling.NEAREST)

        self._canvas_img = ImageTk.PhotoImage(base)
        self.canvas.itemconfig(self.canvas_img_id, image=self._canvas_img)
        self.canvas.configure(scrollregion=(0, 0, base.width, base.height))

        for y in range(doc.height + 1):
            self.canvas.create_line(
                0,
                y * self.cell_px,
                width_px,
                y * self.cell_px,
                fill=self.editor.grid_color,
                tags='grid',
            )
        for x in range(doc.width + 1):
            self.canvas.create_line(
                x * self.cell_px,
                0,
                x * self.cell_px,
                height_px,
                fill=self.editor.grid_color,
                tags='grid',
            )

    def update_preview(self) -> None:
        """
        Render the active frame to a small thumbnail preview.

        Scales the frame down (max 256 px in any dimension) using
        nearest-neighbor sampling for a crisp pixel-art result.

        The preview is then displayed in the right-hand 'Preview' label.
        """

        if not self.preview_label:
            return

        img = self.render_frame(self.editor.active_frame, scale=1)
        if img.width < 1 or img.height < 1:
            return

        if img.width > self.max_size or img.height > self.max_size:
            img = img.resize(
                (min(img.width, self.max_size),
                 min(img.height, self.max_size)),
                Resampling.NEAREST)

        scale = min(4, int(self.max_size / max(img.width, img.height)))
        preview = img.resize(
            (int(img.width * scale), int(img.height * scale)),
            Resampling.NEAREST)

        self._preview_photo = ctk.CTkImage(
            light_image=preview,
            dark_image=preview,
            size=(preview.width, preview.height),
        )
        self.preview_label.configure(image=self._preview_photo)

    def render_frame(self, index: int, scale: int = 1) -> Image.Image:
        doc = self.editor.doc

        img = self._frame_to_image(doc.frames[index].pixels, doc.palette)

        if scale > 1:
            img = img.resize((doc.width * scale, doc.height * scale),
                             Resampling.NEAREST)
        return img

    def paint_at(self, event) -> None:
        """
        Paint or fill pixels in response to a left-click or drag event.

        Determines the grid cell under the cursor and either:
          - Paints a single pixel (`mat[y][x] = color_index`), or
          - Performs a flood-fill if fill mode is active.

        Automatically triggers a redraw and preview update after changes.
        """
        self.editor.focus_set()
        x, y = self._event_to_cell(event)
        doc = self.editor.doc
        if not (0 <= x < doc.width and 0 <= y < doc.height):
            return
        matrix = doc.frames[self.editor.active_frame].pixels

        if self.editor.fill_mode:
            target = matrix[y][x]
            if target == self.editor.active_color_index:
                return
            self._flood_fill(matrix, x, y, target,
                             self.editor.active_color_index)
        else:
            if matrix[y][x] == self.editor.active_color_index:
                return
            matrix[y][x] = self.editor.active_color_index

        self.redraw_canvas()
        self.update_preview()

    def eyedrop_at(self, event) -> None:
        """ Selects the color from the selected pixel """
        x, y = self._event_to_cell(event)
        doc = self.editor.doc
        if not (0 <= x < doc.width and 0 <= y < doc.height):
            return
        idx = doc.frames[self.editor.active_frame].pixels[y][x]
        self.editor.select_color(idx)

    def zoom_changed(self, value) -> None:
        """ Calls a canvas redraw after zoom changes """
        self.cell_px = int(float(value))
        self.redraw_canvas()

    def _event_to_cell(self, event) -> tuple[int, int]:
        """
        Convert a canvas mouse event’s coordinates into grid cell indices.

        Accounts for scroll offsets and current zoom scale (`cell_px`).

        Returns:
            (x, y): The integer grid coordinates of the clicked cell.
        """
        if not self.canvas:
            return 0, 0
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        return int(cx // self.cell_px), int(cy // self.cell_px)

    @staticmethod
    def _flood_fill(matrix: list, x: int, y: int, target_color: int,
                    replacement_color: int) -> None:
        """
        Perform 4-directional flood fill on the current frame matrix.

        Fills contiguous regions of `target_color` starting at `(x, y)`
        with `replacement_color`. Uses an iterative stack-based approach
        to avoid recursion depth limits.

        Args:
            matrix: 2D list of palette indices.
            x, y: Starting coordinates within the grid.
            target_color: Palette index to replace.
            replacement_color: Palette index to apply.

        Note:
            Does not trigger a canvas redraw — caller must handle that.
        """
        if target_color == replacement_color:
            return
        height, width = len(matrix), len(matrix[0])
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cy < 0 or cx >= width or cy >= height:
                continue
            if matrix[cy][cx] != int(target_color):
                continue
            matrix[cy][cx] = int(replacement_color)
            stack.extend([
                (cx + 1, cy),
                (cx - 1, cy),
                (cx, cy + 1),
                (cx, cy - 1),
            ])

    @staticmethod
    def _frame_to_rgba_array(matrix: list[list[int]],
                             palette: list[list[int]]) -> np.ndarray:
        """ Convert a frame matrix and palette into an RGBA NumPy array """
        height = len(matrix)
        width = len(matrix[0]) if height else 0
        rgba = np.zeros((height, width, 4), dtype=np.uint8)

        if height == 0 or width == 0:
            return rgba

        frame_array = np.asarray(matrix, dtype=np.int32).reshape(height, width)

        if palette:
            palette_array = np.asarray(palette, dtype=np.uint8)
            mask = frame_array >= 0
            if np.any(mask):
                indices = frame_array[mask]
                colors = palette_array[indices]
                rgba[mask] = colors

        return rgba

    @classmethod
    def _frame_to_image(cls, matrix: list[list[int]],
                        palette: list[list[int]]) -> Image.Image:
        """ Convert a frame matrix and palette into a Pillow Image using NumPy """
        return Image.fromarray(
            cls._frame_to_rgba_array(matrix, palette), mode='RGBA')

    def _compose_frame_with_onion_skin(self, doc) -> Image.Image:
        """ Render the active frame and optional onion skin into a Pillow Image """
        height, width = doc.height, doc.width
        composed = np.zeros((height, width, 4), dtype=np.uint8)

        palette_array = np.asarray(
            doc.palette, dtype=np.uint8) if doc.palette else None

        if (palette_array is not None and
                self.editor.onion_skin.get() and
                self.editor.active_frame > 0):
            onion_pixels = doc.frames[self.editor.active_frame - 1].pixels
            onion_matrix = np.asarray(onion_pixels, dtype=np.int32).reshape(
                height, width)
            onion_mask = onion_matrix >= 0
            if np.any(onion_mask):
                onion_colors = palette_array[onion_matrix[onion_mask]].copy()
                onion_colors[:, 3] = 90
                composed[onion_mask] = onion_colors

        if palette_array is not None:
            active_pixels = doc.frames[self.editor.active_frame].pixels
            active_matrix = np.asarray(active_pixels, dtype=np.int32).reshape(
                height, width)
            active_mask = active_matrix >= 0
            if np.any(active_mask):
                active_colors = palette_array[active_matrix[active_mask]]
                composed[active_mask] = active_colors

        return Image.fromarray(composed, mode='RGBA')

    # Late import for type checking
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:  # pragma: no cover
        from .sprite_editor import SpriteEditor
