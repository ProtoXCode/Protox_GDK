import customtkinter as ctk

from .sub_menu import OptionsPanel
from .help import HelpView
from .about import AboutView
from .options import OptionsView


class SettingsEditor(ctk.CTkFrame):
    """ Main container for Settings content (right-side view). """

    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app

        # --- Layout setup ---
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Header ---
        ctk.CTkLabel(
            self,
            text='Settings Editor',
            font=('Segoe UI', 20, 'bold')
        ).grid(row=0, column=0, sticky='nw', padx=20, pady=20)

        # --- Content frame ---
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky='nsew', padx=8, pady=8)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # --- Subviews ---
        self.views = {
            'help': HelpView(self.content_frame),
            'about': AboutView(self.content_frame),
            'options': OptionsView(self.content_frame)
        }

        for v in self.views.values():
            v.grid(row=0, column=0, sticky='nsew')

        # Default view
        self.show_view('options')

    def show_view(self, name: str) -> None:
        """ Raise the requested subview in the content frame. """
        view = self.views.get(name)
        if not view:
            raise ValueError(f'Unknown view {name}')
        view.tkraise()

    def build_submenu(self, parent) -> ctk.CTkFrame:
        submenu = OptionsPanel(self)
        return submenu.build(parent)
