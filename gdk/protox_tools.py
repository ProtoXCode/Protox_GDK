from typing import Any
from pathlib import Path

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont


class ProtoXToolKit:
    def __init__(self):
        """ A collection of neat tools. """
        pass

    @staticmethod
    def center_screen(window: Any, app_width: int, app_height: int) -> None:
        """ Centers the tkinter window.

            Keyword arguments:
                window          : The main window to centre.
                app_width       : The width of the app.
                app_height      : The height of the app.
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (app_width / 2))
        y_coordinate = int((screen_height / 2) - (app_height / 2))
        window.geometry('{}x{}+{}+{}'.format(
            app_width, app_height, x_coordinate, y_coordinate))

    @staticmethod
    def add_tooltip(widget: tk.Widget, text: str) -> None:
        """
        Attach a tooltip to any widget.

        Parameters:
          - widget : The widget to display tooltip for.
          - text   : The text to show in the tooltip.
        """

        # noinspection PyUnusedLocal
        def show_tip(event=None) -> None:
            if show_tip.tip_window or not text:
                return
            # noinspection PyTypeChecker
            x, y, _, _ = widget.bbox('insert')
            x += widget.winfo_rootx() + 65
            y += widget.winfo_rooty()
            show_tip.tip_window = tw = tk.Toplevel(widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f'+{x}+{y}')

            label = tk.Label(
                tw,
                text=text,
                background="#ffffe0",
                foreground="#000000",
                relief="solid",
                borderwidth=1,
                anchor='w',
                justify='left',
                font=('Lucida Console', 10)
            )
            label.pack(ipadx=5)

        # noinspection PyUnusedLocal
        def hide_tip(event=None) -> None:
            if show_tip.tip_window:
                show_tip.tip_window.destroy()
                show_tip.tip_window = None

        # Initialize tip_window attribute to avoid AttributeError
        show_tip.tip_window = None

        widget.bind('<Enter>', show_tip)
        widget.bind('<Leave>', hide_tip)

    @staticmethod
    def round_corners(image: Image.Image, radius: int) -> Image.Image:
        """ Return an image with rounded corners. """

        image = image.convert('RGBA')

        # Create a mask with rounded rectangle
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle(
            (0, 0, image.width, image.height), radius=radius, fill=255)

        # Apply the mask to the image
        rounded = image.copy()
        rounded.putalpha(mask)
        return rounded

    @staticmethod
    def image_text(
            image: str,
            text: str,
            font: tuple[str, int] = ('arial.ttf', 24),
            position: tuple[float, float] | None = None,
            fill: tuple[int, int, int, int] = (255, 255, 255, 255),
            bold: bool = False,
            italic: bool = False,
            outline: int = 0,
            outline_color: tuple[int, int, int, int] = (0, 0, 0, 255),
    ) -> Image.Image:
        """
        Draw stylized text (bold, italic, outlined) onto an image.
        Automatically tries to locate font variants (e.g. arialbd.ttf).

        Parameters:
          image:   Path to base image file
          text:    Text to render
          font:    Tuple[str, int] — ('arial.ttf', 24)
          position: Optional (x, y) position, centers if None
          fill:    RGBA text color
          bold:    Use bold variant or simulate
          italic:  Use italic variant or simulate
          outline: Stroke radius in pixels
          outline_color: RGBA for stroke

        Returns:
          PIL.Image with rendered text
        """
        img = Image.open(image).convert('RGBA')
        draw = ImageDraw.Draw(img)

        font_name, size = font
        font_path = Path(font_name)

        # --- font style selection ---
        possible_fonts = [font_name]

        stem = font_path.stem
        suffix = font_path.suffix or '.ttf'

        if bold and italic:
            possible_fonts.insert(0, f'{stem}bi{suffix}')
            possible_fonts.insert(1, f'{stem}z{suffix}')
        elif bold:
            possible_fonts.insert(0, f'{stem}bd{suffix}')
            possible_fonts.insert(1, f'{stem}-bold{suffix}')
        elif italic:
            possible_fonts.insert(0, f'{stem}i{suffix}')
            possible_fonts.insert(1, f'{stem}-italic{suffix}')

        # Try to load a working font variant
        loaded_font = None
        for f in possible_fonts:
            try:
                loaded_font = ImageFont.truetype(f, size)
                break
            except OSError:
                continue

        if not loaded_font:
            loaded_font = ImageFont.load_default()
        font = loaded_font

        # --- text size and position ---
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if position is None:
            position = ((img.width - text_w) / 2, (img.height - text_h) / 2)
        x, y = position

        # --- outline stroke ---
        if outline > 0:
            for ox in range(-outline, outline + 1):
                for oy in range(-outline, outline + 1):
                    if ox ** 2 + oy ** 2 <= outline ** 2:
                        draw.text((x + ox, y + oy), text, font=font,
                                  fill=outline_color)

        # --- simulated bold (if no variant font) ---
        if bold and not any(
                keyword in str(font).lower() for keyword in ['bold', 'bd']):
            for ox, oy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                draw.text((x + ox, y + oy), text, font=font, fill=fill)
        else:
            draw.text((x, y), text, font=font, fill=fill)

        return img
