import tkinter as tk
from typing import Any


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
        def _show_tip(event=None) -> None:
            if _show_tip.tip_window or not text:
                return
            x, y, _, _ = widget.bbox('insert')
            x += widget.winfo_rootx() + 65
            y += widget.winfo_rooty()
            _show_tip.tip_window = tw = tk.Toplevel(widget)
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
        def _hide_tip(event=None) -> None:
            if _show_tip.tip_window:
                _show_tip.tip_window.destroy()
                _show_tip.tip_window = None

        # Initialize tip_window attribute to avoid AttributeError
        _show_tip.tip_window = None

        widget.bind('<Enter>', _show_tip)
        widget.bind('<Leave>', _hide_tip)
