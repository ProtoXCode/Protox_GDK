from __future__ import annotations

import json
import logging
import re
import threading
from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Any

import customtkinter as ctk
from PIL import Image

from .sprite_core import SpriteDoc
from gdk.palette import PALETTES
from gdk.utils import normalize_path


class SpriteIOManager:
    """Handles persistence and external image import/export for sprites."""

    def __init__(self, editor: 'SpriteEditor') -> None:
        self.editor = editor

        # Remember last used directories between calls
        self._last_open_dir: Path | None = None
        self._last_save_dir: Path | None = None
        self._last_import_dir: Path | None = None
        self._last_export_dir: Path | None = None
        self._last_project_root: Path | None = None

    # --- Directory resolution ------------------------------------------------

    def _resolve_dir(self, last_dir: Path | None) -> Path:
        """Return the best starting directory for a dialog."""

        controller = getattr(self.editor, 'controller', None)
        main_app = (getattr(controller, 'main_app', None) or
                    getattr(self.editor, 'main_app', None))
        active_root = None

        if main_app and getattr(main_app, 'active_project_path', None):
            active_root = main_app.active_project_path

        # If project changed since last call -> nuke remebered dirs
        if active_root is not None and active_root != self._last_project_root:
            self._last_project_root = active_root
            self._last_open_dir = None
            self._last_save_dir = None
            self._last_import_dir = None
            self._last_export_dir = None
            last_dir = None

        # Use last dir if valid
        if last_dir and last_dir.exists():
            return last_dir

        # Else default to current project's sprites/
        if active_root is not None:
            sprite_dir = active_root / 'sprites'
            sprite_dir.mkdir(exist_ok=True)
            return sprite_dir

        # Fallback
        return Path.cwd() / 'projects'

    # --- Core document operations --------------------------------------------

    def new_doc(self) -> None:
        current_palette_name = self.editor.palette_var.get()
        self.editor.doc = SpriteDoc.empty(
            width=16,
            height=16,
            palette=PALETTES['ProtoX 64'],
            name='sprite'
        )
        self.editor.active_frame = 0
        self.editor.last_saved_path = None
        self.editor.refresh_all()
        self.editor.metadata_panel.refresh_from_doc()
        self.editor.palette_var.set(current_palette_name)

    def open_doc(self) -> None:
        """ Open a saved sprite JSON and restore its palette and metadata. """
        path = askopenfilename(
            title='Open Sprite JSON',
            filetypes=[('Sprite JSON', '*.json'), ('All Files', '*.*')],
            initialdir=self._resolve_dir(self._last_open_dir)
        )
        if not path:
            return

        self._last_open_dir = Path(path).parent

        with open(path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        # Palette restore
        palette_name = data.get('palette_name', 'ProtoX 64')
        palette = PALETTES.get(palette_name, PALETTES['ProtoX 64'])
        self.editor.doc.palette = palette
        self.editor.palette_var.set(palette_name)

        # Sync UI
        self.editor.doc = SpriteDoc.from_json(data)
        self.editor.active_frame = 0
        self.editor.last_saved_path = Path(path)
        self.editor.rebuild_color_buttons(self.editor.palette_frame, 4, 25)
        self.editor.refresh_all()
        self.editor.metadata_panel.refresh_from_doc()

        logging.info(f'Loaded sprite: {path}')

    def save_doc(self) -> None:
        """Save the current sprite to disk (or trigger Save As)."""
        if self.editor.last_saved_path is None:
            self.save_as_doc()
            return

        # Inject palette name before save
        data = self.editor.doc.to_json()
        data['palette_name'] = self.editor.palette_var.get()

        # Compact numeric formatting for lists
        text = json.dumps(data, indent=2)
        text = re.sub(
            r'\[\s*((?:-?\d+\s*,\s*)*-?\d+)\s*]',
            lambda m: "[ " + re.sub(r'\s*,\s*', ', ', m.group(1)) + " ]",
            text
        )

        with open(self.editor.last_saved_path, 'w',
                  encoding='utf-8') as handle:
            handle.write(text)

        logging.info(
            f'Saved sprite: {normalize_path(self.editor.last_saved_path)}')

    def save_as_doc(self) -> None:
        """Save the sprite with a new file name."""
        path = asksaveasfilename(
            title='Save Sprite JSON',
            defaultextension='.json',
            filetypes=[('Sprite JSON', '*.json'), ('All Files', '*.*')],
            initialdir=self._resolve_dir(self._last_save_dir)
        )
        if not path:
            return

        path = Path(path)
        self._last_save_dir = path.parent
        self.editor.last_saved_path = path

        self.save_doc()

    # --- Export operations ------------------------------------------------

    def export_png(self) -> None:
        """Export the current frame as a PNG image."""
        path = asksaveasfilename(
            title='Export PNG (current frame)',
            defaultextension='.png',
            filetypes=[('PNG image', '*.png'), ('All Files', '*.*')],
            initialdir=self._resolve_dir(self._last_export_dir)
        )
        if not path:
            return

        self._last_export_dir = Path(path).parent

        img = self.editor.canvas_view.render_frame(
            self.editor.active_frame, scale=1)
        img.save(path, 'PNG')
        logging.info(f'Exported PNG to: {normalize_path(path)}')

    def export_gif(self) -> None:
        """Export the current frame as a GIF image."""
        path = asksaveasfilename(
            title='Export GIF (animated gif)',
            defaultextension='.gif',
            filetypes=[('GIF image', '*.gif'), ('All Files', '*.*')],
            initialdir=self._resolve_dir(self._last_export_dir)
        )
        if not path:
            return

        self._last_export_dir = Path(path).parent

        images = [self.editor.canvas_view.render_frame(i)
                  for i in range(len(self.editor.doc.frames))]
        frame_duration = max(1, self.editor.frame_time_var.get())

        images[0].save(
            path,
            save_all=True,
            append_images=images[1:],
            duration=frame_duration,
            loop=0 if self.editor.doc.loop else 1,
            disposal=2,
            transparency=0
        )
        logging.info(f'Exported GIF to: {normalize_path(path)}')

    # --- Import image --------------------------------------------------------

    def import_image(self) -> None:
        """Import an external image file and quantize it to the current palette (threaded)."""
        path = askopenfilename(
            title='Import sprite image',
            filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp'),
                       ('All Files', '*.*')],
            initialdir=self._resolve_dir(self._last_import_dir)
        )
        if not path:
            return

        self._last_import_dir = Path(path).parent

        busy_label = ctk.CTkLabel(self.editor, text='  Importing...  ',
                                  text_color='orange')
        busy_label.place(relx=0.5, rely=0.5, anchor='center')
        self.editor.configure(cursor='watch')
        self.editor.update_idletasks()

        def worker():
            try:
                img = Image.open(path).convert('RGBA')
                width, height = img.size
                pixels = img.load()
                matrix = [[-1 for _ in range(width)] for _ in range(height)]

                for y in range(height):
                    for x in range(width):
                        r, g, b, a = pixels[x, y]
                        if a < 32:
                            matrix[y][x] = -1
                            continue
                        matrix[y][x] = self.find_closest_color((r, g, b, a))

                # 🟢 Apply result safely in main thread
                def apply_result():
                    self.editor.resize_grid(width, height)
                    self.editor.doc.frames[
                        self.editor.active_frame].pixels = matrix
                    self.editor.refresh_all()
                    busy_label.destroy()
                    self.editor.configure(cursor='')

                self.editor.after(0, apply_result)  # type: ignore[arg-type]

            except Exception as e:
                logging.exception(e)
                self.editor.after(0, lambda: busy_label.configure(
                    text=f'Error: {e}',
                    text_color='red'))  # type: ignore[arg-type]
            finally:
                self.editor.after(0, lambda: self.editor.configure(
                    cursor=''))  # type: ignore[arg-type]

        threading.Thread(target=worker, daemon=True).start()
        logging.info(
            f'Imported image into current frame: {normalize_path(path)}')

    # --- Color quantization --------------------------------------------------

    def find_closest_color(self, rgba: tuple[Any, ...]) -> int:
        """Find the nearest color index in the active palette."""
        r1, g1, b1, a1 = rgba
        if a1 < 32:
            return -1  # transparent

        best_idx = 0
        best_dist = float('inf')

        for i, (r2, g2, b2, _a2) in enumerate(self.editor.doc.palette):
            dr = r1 - r2
            dg = g1 - g2
            db = b1 - b2
            dist = (dr * 0.3) ** 2 + (dg * 0.59) ** 2 + (db * 0.11) ** 2
            if dist < best_dist:
                best_dist = dist
                best_idx = i
        return best_idx


# Late import for typing only
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sprite_editor import SpriteEditor
