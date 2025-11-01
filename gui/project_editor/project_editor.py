from __future__ import annotations

import customtkinter as ctk

from .project_selection import SelectionPanel
from .view_game import GameView
from .view_keybindings import KeybindingsView
from .project_manager import ProjectLoader


class ProjectEditor(ctk.CTkFrame):
    """Main container for the Project Editor with sub menu and content view."""

    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app
        self.project_manager = ProjectLoader(self)

        # --- Layout setup ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Header ---
        ctk.CTkLabel(
            self,
            text='Project Editor',
            font=('Segoe UI', 20, 'bold')
        ).grid(
            row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(10, 4))

        # --- Submenu ---
        self.submenu = SelectionPanel(self)
        self.submenu.grid(row=1, column=0, sticky='nsw', padx=8, pady=8)

        # --- Content frame ---
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=1, sticky='nsew', padx=8, pady=8)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # --- Subviews ---
        self.views = {
            'game': GameView(self.content_frame, main_app=self.main_app),
            'keybindings': KeybindingsView(self.content_frame)
        }

        self.views['game'].project_manager = self.project_manager

        for v in self.views.values():
            v.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)

        # Connect submenu button actions
        self.submenu.set_controller(self)

        # Default view
        self.show_view('game')

    def show_view(self, name: str) -> None:
        """Raise the requested subview in the content frame."""
        view = self.views.get(name)
        if not view:
            raise ValueError(f'Unknown view: {name}')
        view.tkraise()

    def project_menu(self, parent) -> ctk.CTkFrame:
        """Build the left submenu inside the main app."""
        return self.submenu.build(parent)

    def build_submenu(self, parent) -> ctk.CTkFrame:
        return self.project_manager.build(parent)
