from __future__ import annotations

import re
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any
from tkinter.filedialog import askopenfilename, asksaveasfilename
from functools import partial

import customtkinter as ctk
from PIL import Image, ImageTk
from PIL.Image import Resampling

from gdk.palette import default_palette


# --- Data model --------------------------------------------------------------

@dataclass
class SpriteFrame:
    # 2D matrix: int palette index or -1 for transparent
    pixels: list[list[int]]


@dataclass
class SpriteDoc:
    width: int
    height: int
    palette: list[list[int]]
    frames: list[SpriteFrame]
    name: str = 'unnamed'
    fps: int = 10
    loop: bool = True
    author: str = 'unknown'
    tags: list[str] = None
    properties: dict[str, Any] = None

    @staticmethod
    def empty(width: int, height: int, palette: list[list[int]],
              name: str = 'unnamed') -> 'SpriteDoc':
        blank = [[-1 for _ in range(width)] for _ in range(height)]
        return SpriteDoc(width=width, height=height, palette=palette,
                         frames=[SpriteFrame(blank)], name=name, tags=[],
                         properties={
                             'collision': False,
                             'static': False,
                             'background': False,
                             'player': False
                         })

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'loop': self.loop,
            'author': self.author,
            'tags': self.tags,
            'palette': self.palette,
            'frames': [f.pixels for f in self.frames],
            'properties': self.properties or {}
        }

    @staticmethod
    def from_json(d: dict) -> 'SpriteDoc':
        return SpriteDoc(
            name=d.get('name', 'unnamed'),
            width=int(d['width']),
            height=int(d['height']),
            fps=int(d.get('fps', 10)),
            loop=bool(d.get('loop', True)),
            author=d.get('author', 'unknown'),
            tags=d.get('tags', []),
            palette=[list(map(int, rgba)) for rgba in d['palette']],
            frames=[SpriteFrame(
                [[int(v) for v in row] for row in m]) for m in d['frames']],
            properties=d.get('properties', {
                'collision': False,
                'static': False,
                'background': False,
                'player': False
            })
        )


# --- Editor widget -----------------------------------------------------------


class SpriteEditor(ctk.CTkFrame):
    """
    A minimum-but-useful pixel editor:

     - Grid painting with a tiny palette (RGBA).
     - Multiple frames (add/duplicate/delete).
     - Save/Load JSON (`SpriteDoc` format).
     - PNG export (uses current frame + palette).
    """

    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app
        self.padding = 10
        self.cell_px = 22  # Canvas pixels per cell
        self.grid_color = '#444444'
        self.btn_bar_width = 30

        self.meta_name: Optional[ctk.CTkEntry] = None
        self.meta_author: Optional[ctk.CTkEntry] = None
        self.meta_fps: Optional[ctk.CTkEntry] = None
        self.meta_loop: Optional[ctk.BooleanVar] = None
        self.meta_tags: Optional[ctk.CTkEntry] = None

        # Default palette (Amiga-ish)
        self.default_palette = default_palette

        # State
        self.doc: SpriteDoc = SpriteDoc.empty(
            width=16, height=16, palette=self.default_palette, name='sprite')
        self.active_frame = 0
        self.active_color_index = 1  # Default: black
        self.onion_skin = ctk.BooleanVar(value=False)
        self.last_saved_path: Optional[Path] = None
        self._suspend_autoapply = False

        # Default values
        self.fill_mode = False
        self.prop_collision = None
        self.prop_static = None
        self.prop_background = None
        self.prop_player = None

        # Layout: left (tools) | center (canvas) | right (frames/preview)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_palette()
        self._build_canvas()
        self._build_frames_panel()
        self._refresh_all()

    # --- UI Builder ----------------------------------------------------------

    def _build_toolbar(self):
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
                      command=self._redraw_canvas).grid(
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
            cmd = partial(self._resize_grid, w, h)
            ctk.CTkButton(size_box, text=f'{w}x{h}', width=56,
                          command=cmd).grid(row=0, column=i + 1, padx=2)

    def _build_palette(self) -> None:
        box = ctk.CTkFrame(self)
        box.grid(row=1, column=0, sticky='nsw', padx=self.padding,
                 pady=self.padding)
        box.columnconfigure(0, weight=1)

        ctk.CTkLabel(box, text='Palette').grid(padx=8, pady=(8, 4))

        self.palette_buttons: list[ctk.CTkButton] = []

        # --- grid of color buttons ---
        grid_frame = ctk.CTkFrame(box)
        grid_frame.grid(row=1, column=0, padx=6, pady=4)
        grid_frame.columnconfigure(tuple(range(4)), weight=1)

        cols = 4  # how many buttons per row
        btn_size = 25

        for i, rgba in enumerate(self.doc.palette):
            btn = ctk.CTkButton(
                grid_frame,
                text='',
                width=btn_size,
                height=btn_size,
                fg_color=_rgba_hex(rgba),
                corner_radius=4,
                border_width=2,
                border_color='#222',
                command=lambda colour=i: self._select_color(color)
            )
            r, c = divmod(i, cols)
            btn.grid(row=r, column=c, padx=3, pady=3)
            self.palette_buttons.append(btn)

        # --- special tools row ---
        width = cols * (btn_size + 6) - 6  # About the grid width
        special_frame = ctk.CTkFrame(box)
        special_frame.configure(width=width)
        special_frame.grid(padx=6, pady=(8, 6), sticky='ew')
        special_frame.columnconfigure(0, weight=1)

        for idx, (label, color, cmd) in enumerate([
            ('Transparent', '#000000', lambda: self._select_color(-1)),
            ('Fill', '#333333', lambda: self._enable_fill_mode())]):
            ctk.CTkButton(
                special_frame,
                text=label,
                width=80,
                height=22,
                fg_color=color,
                command=cmd
            ).grid(row=idx, column=0, pady=2)

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
            command=self._zoom_changed,
            width=100,
            height=12
        )
        self.zoom.set(self.cell_px)
        self.zoom.grid(row=1, column=0, sticky='ew', padx=2, pady=(0, 4))

    def _build_canvas(self) -> None:
        center = ctk.CTkFrame(self)
        center.grid(row=1, column=1, sticky='nsew',
                    padx=(0, self.padding), pady=self.padding)
        center.rowconfigure(0, weight=1)
        center.columnconfigure(0, weight=1)

        # --- add scrollbars ---
        x_scroll = ctk.CTkScrollbar(center, orientation='horizontal')
        y_scroll = ctk.CTkScrollbar(center, orientation='vertical')
        x_scroll.grid(row=1, column=0, sticky='ew')
        y_scroll.grid(row=0, column=1, sticky='ns')

        # --- scrollable canvas ---
        self.canvas = ctk.CTkCanvas(
            center, bg='#1a1a1a', highlightthickness=0,
            xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.canvas_img_id = self.canvas.create_image(0, 0, anchor='nw')

        # connect scrollbars
        x_scroll.configure(command=self.canvas.xview)
        y_scroll.configure(command=self.canvas.yview)

        def _on_mouse_wheel(event) -> None:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all('<MouseWheel>', _on_mouse_wheel)

        def _start_pan(event) -> None:
            self.canvas.scan_mark(event.x, event.y)

        def _do_pan(event) -> None:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

        self.canvas.bind('<ButtonPress-2>', _start_pan)
        self.canvas.bind('<B2-Motion>', _do_pan)

        # --- painting/eyedropper ---
        self.canvas.bind('<Button-1>', self._paint_at)
        self.canvas.bind('<B1-Motion>', self._paint_at)
        self.canvas.bind('<Button-3>', self._eyedrop_at)

    def _build_frames_panel(self) -> None:
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

    def build_submenu(self, parent) -> None:
        """Build the left-hand sidebar for sprite metadata."""
        meta = ctk.CTkFrame(parent)
        meta.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        meta.columnconfigure(1, weight=1)  # allow the right side to stretch

        # --- Title ---
        ctk.CTkLabel(
            meta, text="Sprite Metadata", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(4, 8))

        # --- Name ---
        ctk.CTkLabel(meta, text="Name:").grid(
            row=1, column=0, sticky="w", pady=2)
        self.meta_name = ctk.CTkEntry(meta)
        self.meta_name.insert(0, self.doc.name)
        self.meta_name.grid(row=1, column=1, sticky="ew", pady=2)

        # --- Author ---
        ctk.CTkLabel(meta, text="Author:").grid(
            row=2, column=0, sticky="w", pady=2)
        self.meta_author = ctk.CTkEntry(meta)
        self.meta_author.insert(0, self.doc.author)
        self.meta_author.grid(row=2, column=1, sticky="ew", pady=2)

        # --- FPS ---
        ctk.CTkLabel(meta, text="Animation FPS:").grid(
            row=3, column=0, sticky="w", pady=2)
        self.meta_fps = ctk.CTkEntry(meta, width=80, justify="center")
        self.meta_fps.insert(0, self.doc.fps)
        self.meta_fps.grid(row=3, column=1, sticky="ew", pady=2)

        # keep the slider -> FPS sync
        def _synch_from_slider(*_):
            try:
                fps = round(1000 / max(1, self.frame_time_var.get()))
                self.meta_fps.delete(0, "end")
                self.meta_fps.insert(0, str(fps))
            except Exception as e:
                logging.error(e)

        self.frame_time_var.trace_add("write", _synch_from_slider)

        # --- Loop toggle ---
        ctk.CTkLabel(meta, text="Loop:").grid(
            row=4, column=0, sticky="w", pady=2)
        self.meta_loop = ctk.BooleanVar(value=self.doc.loop)
        ctk.CTkCheckBox(meta, text="", variable=self.meta_loop).grid(
            row=4, column=1, sticky="w", pady=2)

        # --- Tags ---
        ctk.CTkLabel(meta, text="Tags:").grid(
            row=5, column=0, sticky="w", pady=2)
        self.meta_tags = ctk.CTkEntry(meta)
        self.meta_tags.insert(0, ", ".join(self.doc.tags or []))
        self.meta_tags.grid(row=5, column=1, sticky="ew", pady=2)

        # --- Properties ---
        ctk.CTkLabel(meta, text="Properties:").grid(
            row=6, column=0, sticky="nw", pady=(6, 2))
        flags_box = ctk.CTkFrame(meta, fg_color="transparent")
        flags_box.grid(row=6, column=1, sticky="w", pady=(6, 2))

        self.prop_collision = ctk.BooleanVar(
            value=self.doc.properties.get("collision", False))
        self.prop_static = ctk.BooleanVar(
            value=self.doc.properties.get("static", False))
        self.prop_background = ctk.BooleanVar(
            value=self.doc.properties.get("background", False))
        self.prop_player = ctk.BooleanVar(
            value=self.doc.properties.get("player", False))

        ctk.CTkCheckBox(flags_box, text="Collision",
                        variable=self.prop_collision).grid(sticky="w")
        ctk.CTkCheckBox(flags_box, text="Static Asset",
                        variable=self.prop_static).grid(sticky="w")
        ctk.CTkCheckBox(flags_box, text="Background",
                        variable=self.prop_background).grid(sticky="w")
        ctk.CTkCheckBox(flags_box, text="Player Character",
                        variable=self.prop_player).grid(sticky="w")

        def _bind_autoapply(widget, event_type="<FocusOut>"):
            """Bind automatic metadata save to widget change or focus loss."""
            if hasattr(widget, "bind"):  # only bind real widgets
                widget.bind(event_type, lambda event: self._apply_metadata())

        # only bind entry widgets
        for entry in (
                self.meta_name,
                self.meta_author,
                self.meta_fps,
                self.meta_tags):
            _bind_autoapply(entry)

        # trace BooleanVars instead
        for var in (
                self.meta_loop,
                self.prop_collision,
                self.prop_static,
                self.prop_background,
                self.prop_player):
            # three-arg lambda to match trace_add signature
            var.trace_add(
                "write", lambda var_name, index, mode: self._apply_metadata())

    def _apply_metadata(self) -> None:
        """ Synch UI -> SpriteDoc """
        if getattr(self, '_suspend_autoapply', False):
            return

        self.doc.name = self.meta_name.get().strip()
        self.doc.author = self.meta_author.get().strip()
        self.doc.fps = int(self.meta_fps.get())
        self.doc.loop = self.meta_loop.get()

        tags_raw = self.meta_tags.get().strip()
        self.doc.tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

        self.doc.properties = {
            'collision': self.prop_collision.get(),
            'static': self.prop_static.get(),
            'background': self.prop_background.get(),
            'player': self.prop_player.get()}

        self._show_saved_status()

    def _show_saved_status(self) -> None:
        if getattr(self, '_suspend_autoapply', False):
            return

        if hasattr(self, '_save_label'):
            self._save_label.destroy()

        self._save_label = ctk.CTkLabel(
            self.main_app.sub_menu, text='✓ Saved', text_color='green')

        self._save_label.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor='se')
        # noinspection PyTypeChecker
        self.after(1500, lambda: self._save_label.destroy())

    # --- Actions -------------------------------------------------------------

    def _bind_autoapply(self, widget, event_type='<FocusOut>') -> None:
        """ Bind automatic metadata save to widget change of focus loss. """
        widget.bind(event_type, lambda event: self._apply_metadata())

    def _on_frame_time_changed(self, value: float) -> None:
        """ Slider <---> entry synch """
        self.frame_time_var.set(int(value))

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
        self._redraw_canvas()
        self._update_preview()
        delay = max(1, self.frame_time_var.get())
        self.after(delay, self._loop_step, self.active_frame + 1)

    def _stop_playback(self) -> None:
        """ Stop looping playback """
        self._is_playing = False

    def _refresh_all(self) -> None:
        self._rebuild_frames_strip()
        self._redraw_canvas()
        self._update_preview()

    def _rebuild_frames_strip(self) -> None:
        for b in self.frame_buttons:
            b.destroy()
        self.frame_buttons.clear()

        for idx, _ in enumerate(self.doc.frames):
            def switch(i=idx) -> None:
                self.active_frame = i
                self._redraw_canvas()
                self._update_preview()
                self._rebuild_frames_strip()

            label = f'[{idx + 1}]'
            btn = ctk.CTkButton(
                self.frames_strip, text=label, width=60, command=switch)
            if idx == self.active_frame:
                btn.configure(fg_color='#2255aa')
            btn.grid(padx=2, pady=2)
            self.frame_buttons.append(btn)

    def _redraw_canvas(self, *_) -> None:
        if not hasattr(self, 'canvas_img_id'):
            self.canvas_img_id = self.canvas.create_image(0, 0, anchor='nw')
        w = self.doc.width * self.cell_px
        h = self.doc.height * self.cell_px
        self.canvas.configure(width=w, height=h)
        self.canvas.delete('grid')

        # Draw onion (previous frame) faint
        if self.onion_skin.get() and self.active_frame > 0:
            prev = self.doc.frames[self.active_frame - 1].pixels
            self._draw_matrix(prev, alpha=90)

        # Draw current frame
        matrix = self.doc.frames[self.active_frame].pixels
        self._draw_matrix(matrix, alpha=255)

        # Grid overlay
        for y in range(self.doc.height + 1):
            self.canvas.create_line(
                0, y * self.cell_px, w, y * self.cell_px,
                fill=self.grid_color, tags='grid'
            )
        for x in range(self.doc.width + 1):
            self.canvas.create_line(
                x * self.cell_px, 0, x * self.cell_px, h,
                fill=self.grid_color, tags='grid'
            )

        self.canvas.configure(scrollregion=(0, 0, w, h))

    def _draw_matrix(self, matrix: list[list[int]], alpha: int) -> None:
        h, w = len(matrix), len(matrix[0])

        # render current (and optional onion skin) into ONE image
        base = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        px = base.load()

        # onion skin (previous frame) faint
        if self.onion_skin.get() and self.active_frame > 0 and alpha == 255:
            prev = self.doc.frames[self.active_frame - 1].pixels
            for y in range(h):
                prow = prev[y]
                for x, idx in enumerate(prow):
                    if idx < 0:
                        continue
                    r, g, b, a = self.doc.palette[idx]
                    px[x, y] = (r, g, b, 90)  # ghost alpha

        # current frame
        for y in range(h):
            row = matrix[y]
            for x, idx in enumerate(row):
                if idx < 0:
                    continue
                r, g, b, a = self.doc.palette[idx]
                px[x, y] = (r, g, b, a)

        # scale for zoom
        if self.cell_px != 1:
            base = base.resize((w * self.cell_px, h * self.cell_px),
                               Resampling.NEAREST)

        # store & reuse PhotoImage
        self._canvas_img = ImageTk.PhotoImage(base)
        self.canvas.itemconfig(self.canvas_img_id, image=self._canvas_img)

        # update scroll bounds
        self.canvas.configure(scrollregion=(0, 0, base.width, base.height))

    def _update_preview(self) -> None:
        """ Render current frame to a small PIL image and thumbnail it """
        img = self._render_frame(self.active_frame, scale=1)
        if img.width < 1 or img.height < 1:
            return

        max_size = 256  # max width or height in pixels (scaled)
        scale = min(4, int(max_size / max(img.width, img.height)))
        preview = img.resize(
            (int(img.width * scale), int(img.height * scale)),
            Resampling.NEAREST)

        self._preview_photo = ctk.CTkImage(
            light_image=preview,
            dark_image=preview,
            size=(preview.width, preview.height))

        self.preview_label.configure(image=self._preview_photo)

    def _event_to_cell(self, event) -> tuple[int, int]:
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        x = int(cx // self.cell_px)
        y = int(cy // self.cell_px)
        return x, y

    def _paint_at(self, event) -> None:
        self.focus_set()
        x, y = self._event_to_cell(event)
        if not (0 <= x < self.doc.width and 0 <= y < self.doc.height):
            return
        mat = self.doc.frames[self.active_frame].pixels

        if self.fill_mode:
            target = mat[y][x]
            if target == self.active_color_index:
                return
            self._flood_fill(mat, x, y, target, self.active_color_index)
        else:
            if mat[y][x] == self.active_color_index:
                return
            mat[y][x] = self.active_color_index

        self._redraw_canvas()
        self._update_preview()

    def _eyedrop_at(self, event) -> None:
        x, y = self._event_to_cell(event)
        if not (0 <= x < self.doc.width and 0 <= y < self.doc.height):
            return
        idx = self.doc.frames[self.active_frame].pixels[y][x]
        self._select_color(idx)

    def _select_color(self, idx: int) -> None:
        self.active_color_index = idx
        for i, btn in enumerate(self.palette_buttons):
            if i == idx:
                btn.configure(border_color='#ffffff', border_width=3)
            else:
                btn.configure(border_color='#222', border_width=2)

    def _enable_fill_mode(self) -> None:
        self.fill_mode = not self.fill_mode
        print(f"Fill mode {'on' if self.fill_mode else 'off'}")
        # TODO: make button selection visible

    @staticmethod
    def _flood_fill(mat, x, y, target_color, replacement_color) -> None:
        """Recursive fill (4-directional)."""
        if target_color == replacement_color:
            return
        h, w = len(mat), len(mat[0])
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cy < 0 or cx >= w or cy >= h:
                continue
            if mat[cy][cx] != target_color:
                continue
            mat[cy][cx] = replacement_color
            stack.extend(
                [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])

    def _zoom_changed(self, value) -> None:
        self.cell_px = int(float(value))
        self._redraw_canvas()

    def _add_frame(self) -> None:
        blank = [[-1 for _ in range(self.doc.width)] for _ in
                 range(self.doc.height)]
        self.doc.frames.append(SpriteFrame(blank))
        self.active_frame = len(self.doc.frames) - 1
        self._refresh_all()

    def _dup_frame(self) -> None:
        src = self.doc.frames[self.active_frame].pixels
        dup = [row[:] for row in src]
        self.doc.frames.append(SpriteFrame(dup))
        self.active_frame = len(self.doc.frames) - 1
        self._refresh_all()

    def _delete_frame(self) -> None:
        if len(self.doc.frames) <= 1:
            return
        del self.doc.frames[self.active_frame]
        self.active_frame = max(0, self.active_frame - 1)
        self._refresh_all()

    def _clear_frame(self) -> None:
        self.doc.frames[self.active_frame].pixels = [
            [-1 for _ in range(self.doc.width)] for _ in
            range(self.doc.height)]
        self._refresh_all()

    def _resize_grid(self, w: int, h: int) -> None:
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
        self._refresh_all()

    # --- File I/O ------------------------------------------------------------

    def _new_doc(self) -> None:
        self.doc = SpriteDoc.empty(16, 16, self.default_palette, name='sprite')
        self.active_frame = 0
        self.last_saved_path = None
        self._refresh_all()

    def _open_doc(self) -> None:
        path = askopenfilename(
            title='Open Sprite JSON',
            filetypes=[('Sprite JSON', '*.json'), ('All Files', '*.*')])
        if not path:
            return

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.doc = SpriteDoc.from_json(data)
        self.active_frame = 0
        self.last_saved_path = Path(path)
        self._refresh_all()

        # --- suspend trace/autoapply while updating UI ---
        self._suspend_autoapply = True
        try:
            if self.meta_name:
                self.meta_name.delete(0, 'end')
                self.meta_name.insert(0, self.doc.name)
            if self.meta_author:
                self.meta_author.delete(0, 'end')
                self.meta_author.insert(0, self.doc.author)
            if self.meta_fps:
                self.meta_fps.delete(0, 'end')
                self.meta_fps.insert(0, self.doc.fps)
            if self.meta_tags:
                self.meta_tags.delete(0, 'end')
                self.meta_tags.insert(0, ', '.join(self.doc.tags or []))
            if self.meta_loop:
                self.meta_loop.set(self.doc.loop)

            # now update the property checkboxes as well
            if hasattr(self.doc, 'properties'):
                props = self.doc.properties
                self.prop_collision.set(props.get('collision', False))
                self.prop_static.set(props.get('static', False))
                self.prop_background.set(props.get('background', False))
                self.prop_player.set(props.get('player', False))
        finally:
            self._suspend_autoapply = False

    def _save_doc(self) -> None:
        if self.last_saved_path is None:
            self._save_as_doc()
            return

        data = self.doc.to_json()
        text = json.dumps(data, indent=2)

        # --- Compactify small arrays (Like palette colors) ---
        # Convert [\n 0,\n 0,\n 0,\n 244] -> [ 0, 0, 0, 255 ]
        text = re.sub(
            r'\[\s*((?:-?\d+\s*,\s*)*-?\d+)\s*]',
            lambda m: "[ " + re.sub(r'\s*,\s*', ', ', m.group(1)) + " ]",
            text)

        with open(self.last_saved_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def _save_as_doc(self) -> None:
        path = asksaveasfilename(
            title='Save Sprite JSON', defaultextension='.json',
            filetypes=[('Sprite JSON', '*.json'), ('All Files', '*.*')])

        if not path:
            return

        self.last_saved_path = Path(path)
        self._save_doc()

    def _export_png(self):
        path = asksaveasfilename(
            title='Export PNG (current frame)',
            defaultextension='.png',
            filetypes=[('PNG image', '*.png'), ('All Files', '*.*')])

        if not path:
            return

        img = self._render_frame(self.active_frame, scale=1)
        img.save(path, 'PNG')

        logging.info(f'Exported PNG to {path}')

    def _export_gif(self):
        path = asksaveasfilename(
            title='Export GIF (animated gif)',
            defaultextension='.gif',
            filetypes=[('GIF image', '*.gif'), ('All Files', '*.*')])

        if not path:
            return

        images = [self._render_frame(i) for i in range(len(self.doc.frames))]
        frame_duration = max(1, self.frame_time_var.get())

        images[0].save(
            path,
            save_all=True,
            append_images=images[1:],
            duration=frame_duration,
            loop=0 if self.doc.loop else 1,
            disposal=2,
            transparency=0)

        logging.info(f'Exported GIF to {path}')

    def _render_frame(self, index: int, scale: int = 1) -> Image.Image:
        """ Render a frame to a PIL image using the palette """
        w, h = self.doc.width, self.doc.height
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        px = img.load()
        mat = self.doc.frames[index].pixels
        for y in range(h):
            for x in range(w):
                idx = mat[y][x]
                if idx < 0:
                    continue
                r, g, b, a = self.doc.palette[idx]
                px[x, y] = (int(r), int(g), int(b), int(a))
        if scale > 1:
            img = img.resize((w * scale, h * scale), Resampling.NEAREST)
        return img

    def _import_image(self) -> None:
        path = askopenfilename(
            title='Import sprite image',
            filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp'),
                       ('All Files', '*.*')])
        if not path:
            return

        img = Image.open(path).convert('RGBA')
        w, h = img.size
        self._resize_grid(w, h)

        px = img.load()
        matrix = [[-1 for _ in range(w)] for _ in range(h)]

        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a < 32:  # transparent
                    matrix[y][x] = -1
                    continue
                matrix[y][x] = self._find_closest_color((r, g, b, a))

        self.doc.frames[self.active_frame].pixels = matrix
        self._refresh_all()

    def _find_closest_color(self, rgba: tuple[Any, ...]) -> int:
        """ Find the closest color to rgba """
        r1, g1, b1, a1 = rgba
        best_idx = 0
        best_dist = float('inf')
        for i, (r2, g2, b2, a2) in enumerate(self.doc.palette):
            dr, dg, db = r1 - r2, g1 - g2, b1 - b2
            dist = dr * dr + dg * dg + db * db
            if dist < best_dist:
                best_idx = i
                best_dist = dist
        return best_idx

    # --- Tiny one-shot animation preview (just flips frames once) ------------

    def _play_once(self) -> None:
        """ Quick-and-dirty flip with a short delay """
        if len(self.doc.frames) <= 1:
            return
        start = self.active_frame

        def step(i=0) -> None:
            self.active_frame = (start + i) % len(self.doc.frames)
            self._redraw_canvas()
            self._update_preview()
            if i + 1 < len(self.doc.frames):
                self.after(90, step, i + 1)
            else:
                self.active_frame = start
                self._redraw_canvas()
                self._update_preview()

        step(0)


# --- Helpers -----------------------------------------------------------------


def _rgba_hex(rgba: list[int]) -> str:
    """ CTk buttons accept #RRGGBB; we ignore alpha for the button swatch """
    r, g, b, a = rgba
    return f'#{r:02x}{g:02x}{b:02x}'
