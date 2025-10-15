from __future__ import annotations

from typing import Optional

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

    def build(self, parent: ctk.CTkFrame) -> None:
        """Create the canvas area with scrollbars and mouse bindings."""
        center = ctk.CTkFrame(parent)
        center.grid(row=1, column=1, sticky="nsew",
                    padx=(0, self.editor.padding), pady=self.editor.padding)
        center.rowconfigure(0, weight=1)
        center.columnconfigure(0, weight=1)

        x_scroll = ctk.CTkScrollbar(center, orientation="horizontal")
        y_scroll = ctk.CTkScrollbar(center, orientation="vertical")
        x_scroll.grid(row=1, column=0, sticky="ew")
        y_scroll.grid(row=0, column=1, sticky="ns")

        self.canvas = ctk.CTkCanvas(
            center,
            bg="#1a1a1a",
            highlightthickness=0,
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas_img_id = self.canvas.create_image(0, 0, anchor="nw")

        x_scroll.configure(command=self.canvas.xview)
        y_scroll.configure(command=self.canvas.yview)

        def _on_mouse_wheel(event) -> None:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        def _start_pan(event) -> None:
            self.canvas.scan_mark(event.x, event.y)

        def _do_pan(event) -> None:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

        self.canvas.bind("<ButtonPress-2>", _start_pan)
        self.canvas.bind("<B2-Motion>", _do_pan)

        self.canvas.bind("<Button-1>", self.paint_at)
        self.canvas.bind("<B1-Motion>", self.paint_at)
        self.canvas.bind("<Button-3>", self.eyedrop_at)

    def set_preview_label(self, label: ctk.CTkLabel) -> None:
        self.preview_label = label

    def redraw_canvas(self, *_args) -> None:
        if not self.canvas:
            return

        if self.canvas_img_id is None:
            self.canvas_img_id = self.canvas.create_image(0, 0, anchor="nw")

        doc = self.editor.doc
        width_px = doc.width * self.cell_px
        height_px = doc.height * self.cell_px
        self.canvas.configure(width=width_px, height=height_px)
        self.canvas.delete("grid")

        base = Image.new("RGBA", (doc.width, doc.height), (0, 0, 0, 0))
        pixels = base.load()

        if self.editor.onion_skin.get() and self.editor.active_frame > 0:
            prev = doc.frames[self.editor.active_frame - 1].pixels
            for y, row in enumerate(prev):
                for x, idx in enumerate(row):
                    if idx < 0:
                        continue
                    r, g, b, a = doc.palette[idx]
                    pixels[x, y] = (r, g, b, 90)

        current = doc.frames[self.editor.active_frame].pixels
        for y, row in enumerate(current):
            for x, idx in enumerate(row):
                if idx < 0:
                    continue
                r, g, b, a = doc.palette[idx]
                pixels[x, y] = (r, g, b, a)

        if self.cell_px != 1:
            base = base.resize((doc.width * self.cell_px, doc.height * self.cell_px),
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
                tags="grid",
            )
        for x in range(doc.width + 1):
            self.canvas.create_line(
                x * self.cell_px,
                0,
                x * self.cell_px,
                height_px,
                fill=self.editor.grid_color,
                tags="grid",
            )

    def update_preview(self) -> None:
        if not self.preview_label:
            return

        img = self.render_frame(self.editor.active_frame, scale=1)
        if img.width < 1 or img.height < 1:
            return

        max_size = 256
        scale = min(4, int(max_size / max(img.width, img.height)))
        preview = img.resize(
            (int(img.width * scale), int(img.height * scale)),
            Resampling.NEAREST,
        )

        self._preview_photo = ctk.CTkImage(
            light_image=preview,
            dark_image=preview,
            size=(preview.width, preview.height),
        )
        self.preview_label.configure(image=self._preview_photo)

    def render_frame(self, index: int, scale: int = 1) -> Image.Image:
        doc = self.editor.doc
        img = Image.new("RGBA", (doc.width, doc.height), (0, 0, 0, 0))
        pixels = img.load()
        matrix = doc.frames[index].pixels
        for y in range(doc.height):
            for x in range(doc.width):
                idx = matrix[y][x]
                if idx < 0:
                    continue
                r, g, b, a = doc.palette[idx]
                pixels[x, y] = (int(r), int(g), int(b), int(a))

        if scale > 1:
            img = img.resize((doc.width * scale, doc.height * scale),
                             Resampling.NEAREST)
        return img

    def paint_at(self, event) -> None:
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
            self._flood_fill(matrix, x, y, target, self.editor.active_color_index)
        else:
            if matrix[y][x] == self.editor.active_color_index:
                return
            matrix[y][x] = self.editor.active_color_index

        self.redraw_canvas()
        self.update_preview()

    def eyedrop_at(self, event) -> None:
        x, y = self._event_to_cell(event)
        doc = self.editor.doc
        if not (0 <= x < doc.width and 0 <= y < doc.height):
            return
        idx = doc.frames[self.editor.active_frame].pixels[y][x]
        self.editor._select_color(idx)

    def zoom_changed(self, value) -> None:
        self.cell_px = int(float(value))
        self.redraw_canvas()

    def _event_to_cell(self, event) -> tuple[int, int]:
        if not self.canvas:
            return 0, 0
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        return int(cx // self.cell_px), int(cy // self.cell_px)

    @staticmethod
    def _flood_fill(matrix, x, y, target_color: int, replacement_color: int) -> None:
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


# Late import for type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .editor import SpriteEditor
