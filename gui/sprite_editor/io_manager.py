from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Any

from PIL import Image

from .core import SpriteDoc
from gdk.palette import PALETTES


class SpriteIOManager:
    """Handles persistence and external image import/export for sprites."""

    def __init__(self, editor: "SpriteEditor") -> None:
        self.editor = editor

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
        """ Open a saved sprite JSON and restore its palette and metadata """
        path = askopenfilename(
            title='Open Sprite JSON',
            filetypes=[('Sprite JSON', '*.json'), ('All Files', '*.*')],
        )
        if not path:
            return

        with open(path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        # Palette restore
        palette_name = data.get('palette_name', 'ProtoX 64')
        palette = PALETTES.get(palette_name, PALETTES['ProtoX 64'])
        self.editor.doc.palette = palette
        self.editor.palette_var.set(palette_name)

        # Sync UI
        self.editor.active_frame = 0
        self.editor.last_saved_path = Path(path)
        self.editor.rebuild_color_buttons(self.editor.palette_frame, 4, 25)
        self.editor.refresh_all()
        self.editor.metadata_panel.refresh_from_doc()

        logging.info(f'Loaded sprite: {path}')

    def save_doc(self) -> None:
        """ Save the current sprite to disk (or trigger Save As) """
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

        logging.info(f'Saved sprite: {self.editor.last_saved_path}')

    def save_as_doc(self) -> None:
        """ Save the sprite with a new file name """
        path = asksaveasfilename(
            title='Save Sprite JSON',
            defaultextension='.json',
            filetypes=[('Sprite JSON', '*.json'), ('All Files', '*.*')],
        )
        if not path:
            return
        self.editor.last_saved_path = Path(path)
        self.save_doc()

    # --- Export operations ---------------------------------------------------

    def export_png(self) -> None:
        """ Export the current frame as a PNG image """
        path = asksaveasfilename(
            title='Export PNG (current frame)',
            defaultextension='.png',
            filetypes=[('PNG image', '*.png'), ('All Files', '*.*')],
        )
        if not path:
            return

        img = self.editor.canvas_view.render_frame(
            self.editor.active_frame, scale=1)
        img.save(path, 'PNG')
        logging.info(f'Exported PNG to: {path}')

    def export_gif(self) -> None:
        """ Export the current frame as a GIF image """
        path = asksaveasfilename(
            title='Export GIF (animated gif)',
            defaultextension='.gif',
            filetypes=[('GIF image', '*.gif'), ('All Files', '*.*')],
        )
        if not path:
            return

        images = [self.editor.canvas_view.render_frame(i) for i in
                  range(len(self.editor.doc.frames))]
        frame_duration = max(1, self.editor.frame_time_var.get())

        images[0].save(
            path,
            save_all=True,
            append_images=images[1:],
            duration=frame_duration,
            loop=0 if self.editor.doc.loop else 1,
            disposal=2,
            transparency=0,
        )
        logging.info(f'Exported GIF to: {path}')

    # --- Import image --------------------------------------------------------

    def import_image(self) -> None:
        """
        Import an external image file and quantize it to the current palette
        """
        path = askopenfilename(
            title='Import sprite image',
            filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp'),
                       ('All Files', '*.*')],
        )
        if not path:
            return

        img = Image.open(path).convert('RGBA')
        width, height = img.size
        self.editor.resize_grid(width, height)

        pixels = img.load()
        matrix = [[-1 for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a < 32:
                    matrix[y][x] = -1
                    continue
                matrix[y][x] = self.find_closest_color((r, g, b, a))

        self.editor.doc.frames[self.editor.active_frame].pixels = matrix
        self.editor.refresh_all()

        logging.info(f'Imported image into current frame: {path}')

    # --- Color quantization --------------------------------------------------

    def find_closest_color(self, rgba: tuple[Any, ...]) -> int:
        """ Find the nearest color index in the active palette """
        r1, g1, b1, _a1 = rgba
        best_idx = 0
        best_dist = float('inf')
        for i, (r2, g2, b2, _a2) in enumerate(self.editor.doc.palette):
            dr, dg, db = r1 - r2, g1 - g2, b1 - b2
            dist = dr * dr + dg * dg + db * db
            if dist < best_dist:
                best_idx = i
                best_dist = dist
        return best_idx


# Late import for typing only
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .editor import SpriteEditor
