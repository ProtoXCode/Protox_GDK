from typing import Any

import tkinter as tk
from PIL import Image, ImageDraw


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
        """Return an image with rounded corners."""

        image = image.convert("RGBA")

        # Create a mask with rounded rectangle
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle(
            (0, 0, image.width, image.height), radius=radius, fill=255)

        # Apply the mask to the image
        rounded = image.copy()
        rounded.putalpha(mask)
        return rounded
