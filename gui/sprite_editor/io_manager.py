from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Any

from PIL import Image

from .core import SpriteDoc


class SpriteIOManager:
    """Handles persistence and external image import/export for sprites."""

    def __init__(self, editor: "SpriteEditor") -> None:
        self.editor = editor

    def new_doc(self) -> None:
        self.editor.doc = SpriteDoc.empty(16, 16, self.editor.default_palette, name='sprite')
        self.editor.active_frame = 0
        self.editor.last_saved_path = None
        self.editor._refresh_all()
        self.editor.metadata_panel.refresh_from_doc()

    def open_doc(self) -> None:
        path = askopenfilename(
            title='Open Sprite JSON',
            filetypes=[('Sprite JSON', '*.json'), ('All Files', '*.*')],
        )
        if not path:
            return

        with open(path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        self.editor.doc = SpriteDoc.from_json(data)
        self.editor.active_frame = 0
        self.editor.last_saved_path = Path(path)
        self.editor._refresh_all()
        self.editor.metadata_panel.refresh_from_doc()

    def save_doc(self) -> None:
        if self.editor.last_saved_path is None:
            self.save_as_doc()
            return

        data = self.editor.doc.to_json()
        text = json.dumps(data, indent=2)
        text = re.sub(
            r'\[\s*((?:-?\d+\s*,\s*)*-?\d+)\s*]',
            lambda m: "[ " + re.sub(r'\s*,\s*', ', ', m.group(1)) + " ]",
            text,
        )

        with open(self.editor.last_saved_path, 'w', encoding='utf-8') as handle:
            handle.write(text)

    def save_as_doc(self) -> None:
        path = asksaveasfilename(
            title='Save Sprite JSON',
            defaultextension='.json',
            filetypes=[('Sprite JSON', '*.json'), ('All Files', '*.*')],
        )
        if not path:
            return
        self.editor.last_saved_path = Path(path)
        self.save_doc()

    def export_png(self) -> None:
        path = asksaveasfilename(
            title='Export PNG (current frame)',
            defaultextension='.png',
            filetypes=[('PNG image', '*.png'), ('All Files', '*.*')],
        )
        if not path:
            return

        img = self.editor.canvas_view.render_frame(self.editor.active_frame, scale=1)
        img.save(path, 'PNG')
        logging.info('Exported PNG to %s', path)

    def export_gif(self) -> None:
        path = asksaveasfilename(
            title='Export GIF (animated gif)',
            defaultextension='.gif',
            filetypes=[('GIF image', '*.gif'), ('All Files', '*.*')],
        )
        if not path:
            return

        images = [self.editor.canvas_view.render_frame(i) for i in range(len(self.editor.doc.frames))]
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
        logging.info('Exported GIF to %s', path)

    def import_image(self) -> None:
        path = askopenfilename(
            title='Import sprite image',
            filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp'), ('All Files', '*.*')],
        )
        if not path:
            return

        img = Image.open(path).convert('RGBA')
        width, height = img.size
        self.editor._resize_grid(width, height)

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
        self.editor._refresh_all()

    def find_closest_color(self, rgba: tuple[Any, ...]) -> int:
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


# Late import for type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .editor import SpriteEditor
