from __future__ import annotations

from pathlib import Path
from typing import Optional, Any
from functools import partial, lru_cache
import logging

import customtkinter as ctk
from PIL import Image
from customtkinter import CTkFrame

from gdk.palette import PALETTES
from gdk.utils import rgba_hex
from .canvas_view import CanvasView
from .sprite_core import SpriteFrame, SpriteDoc
from .io_manager import SpriteIOManager
from .metadata import MetadataPanel


class SpriteEditor(ctk.CTkFrame):
    """
    A minimum-but-useful pixel editor:

     - Grid painting with a tiny palette (RGBA).
     - Multiple frames (add/duplicate/delete).
     - Save/Load JSON (`SpriteDoc` format).
     - PNG/GIF export (uses current frame + palette).
    """

    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app
        self.padding = 10
        self.grid_color = '#444444'
        self.btn_bar_width = 30
        self.cols = 4  # how many buttons per row (set for 64)
        self.btn_size = 25

        # State
        self.doc: SpriteDoc = SpriteDoc.empty(
            width=16, height=16, palette=PALETTES['ProtoX 64'], name='sprite')
        self.active_frame = 0
        self.active_color_index = 1  # Default: black
        self.onion_skin = ctk.BooleanVar(value=False)
        self.last_saved_path: Optional[Path] = None

        # Default values
        self.fill_mode = False
        self.palette_buttons: list[ctk.CTkButton] = []

        # Helper components
        self.canvas_view = CanvasView(self)
        self.metadata_panel = MetadataPanel(self)
        self.io_manager = SpriteIOManager(self)

        # Layout: left (tools) | center (canvas) | right (frames/preview)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_palette()
        self._build_canvas()
        self._build_frames_panel()
        self.refresh_all()

    # --- UI Builder ----------------------------------------------------------

    def _build_toolbar(self):
        """
        Construct the top toolbar for core sprite operations.

        Creates a horizontal button bar that provides:
          - File actions: New, Open, Save, Save As, Import, Export (PNG/GIF)
          - Utility toggle: Onion skin mode
          - Quick grid presets (8×8, 16×16, 32×32, etc.)

        The toolbar also handles dynamic layout using `grid` and
        connects each button to its respective editor command.
        """
        bar = ctk.CTkFrame(self)
        bar.grid(row=0, column=0, columnspan=3, sticky='ew',
                 padx=self.padding, pady=(self.padding, 0))
        bar.grid_columnconfigure(10, weight=1)

        ctk.CTkLabel(
            bar, text='Sprite Editor', font=('Segoe UI', 16, 'bold')).grid(
            row=0, column=0, padx=8, pady=8)

        ctk.CTkButton(bar, text='New', width=self.btn_bar_width,
                      command=self._new_doc).grid(
            row=0, column=1, padx=4, pady=4)
        ctk.CTkButton(bar, text='Open', width=self.btn_bar_width,
                      command=self._open_doc).grid(row=0, column=2, padx=4)
        ctk.CTkButton(bar, text='Save', width=self.btn_bar_width,
                      command=self._save_doc).grid(row=0, column=3, padx=4)
        ctk.CTkButton(bar, text='Save as', width=self.btn_bar_width,
                      command=self._save_as_doc).grid(row=0, column=4, padx=4)
        ctk.CTkButton(bar, text='Export PNG', width=self.btn_bar_width,
                      command=self._export_png).grid(row=0, column=5, padx=4)
        ctk.CTkButton(bar, text='Export GIF', width=self.btn_bar_width,
                      command=self._export_gif).grid(row=0, column=6, padx=4)
        ctk.CTkButton(bar, text='Import', width=self.btn_bar_width,
                      command=self._import_image).grid(row=0, column=7, padx=4)

        ctk.CTkSwitch(bar, text='Onion skin', variable=self.onion_skin,
                      command=self.canvas_view.redraw_canvas).grid(
            row=0, column=8, padx=12)

        # Size quick-picks
        size_box = ctk.CTkFrame(bar)
        size_box.grid(row=0, column=9, padx=8)
        ctk.CTkLabel(size_box, text='Grid:').grid(row=0, column=0, padx=(4, 2))
        for i, (w, h) in enumerate([(8, 8),
                                    (16, 16),
                                    (24, 24),
                                    (32, 32),
                                    (48, 48),
                                    (64, 64),
                                    (128, 128),
                                    (256, 256)]):
            cmd = partial(self.resize_grid, w, h)
            ctk.CTkButton(size_box, text=f'{w}x{h}', width=56,
                          command=cmd).grid(row=0, column=i + 1, padx=2)

    def _build_palette(self) -> None:
        """
        Build the left-side color palette and special drawing tools.

        Provides:
          - A grid of color buttons derived from the current palette
          - Special buttons for transparency and fill modes
          - A zoom slider that scales the canvas cell size

        Handles layout with compact frames and dynamically binds
        each palette button to `select_color()`.
        """
        box = ctk.CTkFrame(self)
        box.grid(row=1, column=0, sticky='nsw', padx=self.padding,
                 pady=self.padding)
        box.columnconfigure(0, weight=1)

        # --- Palette selector header ---
        header_frame = ctk.CTkFrame(box, fg_color='transparent')
        header_frame.grid(row=0, column=0, sticky='ew', padx=8, pady=(8, 4))
        header_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(header_frame, text='Palette:').grid(
            row=0, column=0, sticky='w')

        self.palette_var = ctk.StringVar(value='ProtoX 64')

        def _on_palette_change(choice: str) -> None:
            """ Switch palette and rebuild buttons safely """
            old_palette = self.doc.palette
            new_palette = PALETTES[choice]

            self._remap_palette(old_palette, new_palette)
            self._set_palette_button_config(choice)
            self.rebuild_color_buttons(
                self.palette_frame, self.cols, self.btn_size)
            self.canvas_view.redraw_canvas()
            self.canvas_view.update_preview()

        ctk.CTkOptionMenu(
            header_frame,
            variable=self.palette_var,
            values=list(PALETTES.keys()),
            command=_on_palette_change,
            width=120
        ).grid(row=0, column=1, sticky='e')

        # --- Grid of color buttons ---
        grid_frame = ctk.CTkFrame(box)
        grid_frame.grid(row=1, column=0, padx=6, pady=4)
        grid_frame.columnconfigure(tuple(range(4)), weight=1)
        self.palette_frame = grid_frame

        self.rebuild_color_buttons(grid_frame, self.cols, self.btn_size)

        # --- Special tools row ---
        width = self.cols * (self.btn_size + 6) - 6  # About the grid width
        special_frame = ctk.CTkFrame(box, width=width)
        special_frame.grid(padx=6, pady=(8, 6), sticky='ew')
        special_frame.columnconfigure(0, weight=1)

        self.transparent_button = ctk.CTkButton(
            special_frame,
            text='Transparent',
            width=80, height=22,
            fg_color='#000000',
            command=lambda: self.select_color(-1))
        self.transparent_button.grid(row=0, column=0, pady=2)

        self.fill_button = ctk.CTkButton(
            special_frame,
            text='Fill',
            width=80,
            height=22,
            fg_color='#426aad',
            command=lambda: self._enable_fill_mode())
        self.fill_button.grid(row=1, column=0, pady=2)

        # zoom slider (full-width, compact) ---
        zoom_box = ctk.CTkFrame(box, fg_color='transparent')
        zoom_box.configure(width=width)
        zoom_box.grid(row=3, column=0, padx=6, pady=(4, 6))
        zoom_box.columnconfigure(0, weight=1)

        ctk.CTkLabel(zoom_box, text='Zoom', anchor='w').grid(
            row=0, column=0, sticky='w', padx=(4, 0), pady=(2, 0))

        self.zoom = ctk.CTkSlider(
            zoom_box,
            from_=10,
            to=40,
            number_of_steps=15,
            command=self.canvas_view.zoom_changed,
            width=100,
            height=12
        )
        self.zoom.set(self.canvas_view.cell_px)
        self.zoom.grid(row=1, column=0, sticky='ew', padx=2, pady=(0, 4))

    def _set_palette_button_config(self, choice: str) -> None:
        """ Resize the color buttons """
        if choice == 'ProtoX 64':
            self.cols = 4
            self.btn_size = 25
        else:
            self.cols = 8
            self.btn_size = 20

    def rebuild_color_buttons(self, frame, cols: int, btn_size: int) -> None:
        """ Clear and rebuild color buttons when palette changes """
        for child in frame.winfo_children():
            child.destroy()

        self.palette_buttons.clear()

        for i, rgba in enumerate(self.doc.palette):
            btn = ctk.CTkButton(
                frame,
                text='',
                width=btn_size,
                height=btn_size,
                fg_color=rgba_hex(rgba),
                corner_radius=4,
                border_width=0,
                border_color='#222',
                command=lambda idx=i: self.select_color(idx)
            )
            r, c = divmod(i, cols)
            btn.grid(row=r, column=c, padx=3, pady=3)
            self.palette_buttons.append(btn)

    def _remap_palette(self, old_palette: list[list[int]],
                       new_palette: list[list[int]]) -> None:
        """
        Remap pixel indices by color similarity between two palettes.
        Ignores alpha and clamps invalid indices.
        """

        old_palette_rgb = [p[:3] for p in old_palette]
        new_palette_rgb = [p[:3] for p in new_palette]
        mapping = {}

        @lru_cache(maxsize=4096)
        def color_distance(c1, c2):
            return ((c1[0] - c2[0]) ** 2 +
                    (c1[1] - c2[1]) ** 2 +
                    (c1[2] - c2[2]) ** 2) ** 0.5

        for i, old_rgb in enumerate(old_palette_rgb):
            best_idx = 0
            best_dist = float('inf')
            for j, new_rgb in enumerate(new_palette_rgb):
                dist = color_distance(tuple(old_rgb), tuple(new_rgb))
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j
            mapping[i] = best_idx

        total = changed = 0
        for frame in self.doc.frames:
            for y, row in enumerate(frame.pixels):
                for x, val in enumerate(row):
                    if val < 0 or val >= len(old_palette):
                        continue
                    total += 1
                    new_val = mapping.get(val, 0)
                    if new_val != val:
                        changed += 1
                    row[x] = new_val

        self.doc.palette = new_palette
        self.canvas_view.redraw_canvas()
        self.canvas_view.update_preview()

        logging.info(f'Palette remapped {changed}/{total} pixels '
                     f'({len(old_palette)} -> {len(new_palette)})')

    def _build_canvas(self) -> None:
        """
        Create the central drawing canvas and configure its behavior.

        The canvas displays the active sprite frame and supports:
          - Left-click painting
          - Right-click color picking (eyedropper)
          - Middle-click panning
          - Mouse-wheel scrolling

        Includes both horizontal and vertical scrollbars, linked via
        `xscrollcommand` and `yscrollcommand`. The canvas is internally
        tied to an offscreen `PhotoImage` buffer for real-time updates.

        The scroll region dynamically adjusts to match the current grid
        size when zoomed or resized.
        """
        self.canvas_view.build(self)

    def _build_frames_panel(self) -> None:
        """
        Construct the right-side panel for frame management and playback.

        Includes:
          - A list of frame buttons for navigation
          - Actions for creating, duplicating, or deleting frames
          - A live preview of the current frame
          - Playback controls (Play once, Loop, Stop, Clear)
          - Frame timing slider and entry box (linked to FPS)

        This panel is responsible for multi-frame animation handling
        and small-scale playback previews within the editor.
        """
        right = ctk.CTkFrame(self)
        right.grid(row=1, column=2, sticky='ns',
                   padx=(0, self.padding), pady=self.padding)

        header = ctk.CTkLabel(right, text='Frames')
        header.grid(padx=8, pady=(8, 0))

        strip = ctk.CTkFrame(right)
        strip.grid(padx=8, pady=8, sticky='n')
        self.frame_buttons: list[ctk.CTkButton] = []
        self.frames_strip = strip

        # Actions
        row2 = ctk.CTkFrame(right)
        row2.grid(padx=8, pady=(0, 8))
        ctk.CTkButton(row2, text='+ New', width=70,
                      command=self._add_frame).grid(
            row=0, column=0, padx=2, pady=2)
        ctk.CTkButton(row2, text='Duplicate', width=70,
                      command=self._dup_frame).grid(
            row=0, column=1, padx=2, pady=2)
        ctk.CTkButton(row2, text='Delete', width=70,
                      command=self._delete_frame).grid(
            row=0, column=2, padx=2, pady=2)

        # Tiny preview
        ctk.CTkLabel(right, text='Preview').grid(padx=8, pady=(10, 0))
        self.preview_label = ctk.CTkLabel(right, text='')
        self.preview_label.grid(padx=8, pady=(0, 8))
        self.canvas_view.set_preview_label(self.preview_label)

        # Play controls
        play_box = ctk.CTkFrame(right)
        play_box.grid(padx=8, pady=(0, 12), sticky='ew')

        ctk.CTkButton(play_box, text='⏵ Play once', width=90,
                      command=self._play_once).grid(row=0, column=0, padx=2)
        ctk.CTkButton(play_box, text='🔁 Loop', width=70,
                      command=self._play_loop).grid(row=0, column=1, padx=2)
        ctk.CTkButton(play_box, text='⏹ Stop', width=70,
                      command=self._stop_playback).grid(
            row=0, column=2, padx=2)
        ctk.CTkButton(play_box, text='⟲ Clear', width=70,
                      command=self._clear_frame).grid(row=1, column=1, pady=2)

        # --- Timing controls ---
        speed_box = ctk.CTkFrame(right)
        speed_box.grid(padx=8, pady=(4, 8), sticky='ew')
        speed_box.columnconfigure(1, weight=1)  # make the slider expand

        # Slider on top (row 0 spans full width)
        self.frame_time_var = ctk.IntVar(value=int(1000 / self.doc.fps))
        self.frame_time_slider = ctk.CTkSlider(
            speed_box, from_=20, to=500, number_of_steps=48,
            variable=self.frame_time_var,
            command=self._on_frame_time_changed)
        self.frame_time_slider.grid(
            row=0, column=0, columnspan=2, padx=6, pady=(6, 2), sticky='ew')

        # Label + entry just below the slider
        ctk.CTkLabel(speed_box, text='Frame time (ms):').grid(
            row=1, column=0, padx=(6, 2), sticky='w')
        self.frame_time_entry = ctk.CTkEntry(
            speed_box, width=60, textvariable=self.frame_time_var)
        self.frame_time_entry.grid(
            row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='e')

    def build_submenu(self, parent) -> CTkFrame:
        """
        Build the left-side metadata panel for sprite properties.

        Displays editable metadata fields for the current sprite, including:
          - Name
          - Author
          - Animation FPS (linked to frame-time slider)
          - Loop toggle
          - Tags (comma-separated)
          - Object properties (e.g., collision, player, static, background)

        The fields automatically apply changes on modification (`trace_add`)
        and persist updates directly to the underlying `SpriteDoc`.

        Args:
            parent: The `CTkFrame` in which to embed the metadata controls.
        """
        return self.metadata_panel.build(parent)

    # --- Actions -------------------------------------------------------------

    def _on_frame_time_changed(self, value: float) -> None:
        """ Slider <---> entry synch """
        self.frame_time_var.set(int(value))

    def _play_once(self) -> None:
        """ Quick-and-dirty flip with a short delay """
        if len(self.doc.frames) <= 1:
            return
        start = self.active_frame

        def step(i=0) -> None:
            self.active_frame = (start + i) % len(self.doc.frames)
            self.canvas_view.redraw_canvas()
            self.canvas_view.update_preview()
            if i + 1 < len(self.doc.frames):
                self.after(90, step, i + 1)
            else:
                self.active_frame = start
                self.canvas_view.redraw_canvas()
                self.canvas_view.update_preview()

        step(0)

    def _play_loop(self) -> None:
        """ Continuous playback until stopped """
        if getattr(self, '_is_playing', False):
            return
        self._is_playing = True
        self._loop_step(0)

    def _loop_step(self, i: int) -> None:
        if not getattr(self, '_is_playing', False):
            return
        self.active_frame = i % len(self.doc.frames)
        self.canvas_view.redraw_canvas()
        self.canvas_view.update_preview()
        delay = max(1, self.frame_time_var.get())
        self.after(delay, self._loop_step, self.active_frame + 1)

    def _stop_playback(self) -> None:
        """ Stop looping playback """
        self._is_playing = False

    def refresh_all(self) -> None:
        self._rebuild_frames_strip()
        self.canvas_view.redraw_canvas()
        self.canvas_view.update_preview()

    def _rebuild_frames_strip(self) -> None:
        for b in self.frame_buttons:
            b.destroy()
        self.frame_buttons.clear()

        for idx, _ in enumerate(self.doc.frames):
            def switch(i=idx) -> None:
                self.active_frame = i
                self.canvas_view.redraw_canvas()
                self.canvas_view.update_preview()
                self._rebuild_frames_strip()

            label = f'[{idx + 1}]'
            btn = ctk.CTkButton(
                self.frames_strip, text=label, width=60, command=switch)
            if idx == self.active_frame:
                btn.configure(fg_color='#2255aa')
            btn.grid(padx=2, pady=2)
            self.frame_buttons.append(btn)

    def select_color(self, idx: int) -> None:
        self.active_color_index = idx
        for i, btn in enumerate(self.palette_buttons):
            if i == idx:
                btn.configure(border_color='#ffffff', border_width=0)
            else:
                btn.configure(border_color='#222', border_width=0)

    def _enable_fill_mode(self) -> None:
        """ Enable fill mode, changes color of button to reflect state """
        self.fill_mode = not self.fill_mode  # Bool flip
        if self.fill_mode:
            self.fill_button.configure(fg_color='green')
        else:
            self.fill_button.configure(fg_color='#426aad')

    def _add_frame(self) -> None:
        """ Add a new blank frame """
        blank = [[-1 for _ in range(self.doc.width)] for _ in
                 range(self.doc.height)]
        self.doc.frames.append(SpriteFrame(blank))
        self.active_frame = len(self.doc.frames) - 1
        self.refresh_all()

    def _dup_frame(self) -> None:
        """ Duplicates the selected frame """
        src = self.doc.frames[self.active_frame].pixels
        dup = [row[:] for row in src]
        self.doc.frames.append(SpriteFrame(dup))
        self.active_frame = len(self.doc.frames) - 1
        self.refresh_all()

    def _delete_frame(self) -> None:
        """ Delete the selected frame """
        if len(self.doc.frames) <= 1:
            return
        del self.doc.frames[self.active_frame]
        self.active_frame = max(0, self.active_frame - 1)
        self.refresh_all()

    def _clear_frame(self) -> None:
        self.doc.frames[self.active_frame].pixels = [
            [-1 for _ in range(self.doc.width)] for _ in
            range(self.doc.height)]
        self.refresh_all()

    def resize_grid(self, w: int, h: int) -> None:
        """ Safe resize while keeping content where it fits (top-left) """
        new_frames: list[SpriteFrame] = []
        for frame in self.doc.frames:
            new = [[-1 for _ in range(w)] for _ in range(h)]
            for y in range(min(h, self.doc.height)):
                row = frame.pixels[y]
                for x in range(min(w, self.doc.width)):
                    new[y][x] = row[x]
            new_frames.append(SpriteFrame(new))
        self.doc.width, self.doc.height = w, h
        self.doc.frames = new_frames
        self.refresh_all()

    # --- File I/O ------------------------------------------------------------

    def _new_doc(self) -> None:
        self.io_manager.new_doc()

    def _open_doc(self) -> None:
        self.io_manager.open_doc()

    def _save_doc(self) -> None:
        self.io_manager.save_doc()

    def _save_as_doc(self) -> None:
        self.io_manager.save_as_doc()

    def _export_png(self):
        self.io_manager.export_png()

    def _export_gif(self):
        self.io_manager.export_gif()

    def _render_frame(self, index: int, scale: int = 1) -> Image.Image:
        """ Render a frame to a PIL image using the palette """
        return self.canvas_view.render_frame(index, scale)

    def _import_image(self) -> None:
        self.io_manager.import_image()

    def _find_closest_color(self, rgba: tuple[Any, ...]) -> int:
        """ Find the closest color to rgba """
        return self.io_manager.find_closest_color(rgba)
