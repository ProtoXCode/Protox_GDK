import customtkinter as ctk

from .help_selection import SelectionPanel
from .help_project_editor import ProjectEditorView
from .help_sprite_editor import SpriteEditorView
from .help_level_editor import LevelEditorView
from .help_scene_editor import SceneEditorView


class HelpView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        # --- Layout setup ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Header ---
        ctk.CTkLabel(
            self,
            text='Help',
            font=('Segoe UI', 20, 'bold')
        ).grid(
            row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(10, 4))

        # --- Submenu ---
        self.submenu = SelectionPanel(self)
        self.submenu.grid(row=1, column=0, sticky='nsw', padx=8, pady=8)

        # --- Content frame ---
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=1, sticky='nsew', padx=8, pady=8)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

        # --- Subviews ---
        self.views = {
            'project_editor': ProjectEditorView(self.content_frame),
            'sprite_editor': SpriteEditorView(self.content_frame),
            'level_editor': LevelEditorView(self.content_frame),
            'scene_editor': SceneEditorView(self.content_frame)
        }

        for v in self.views.values():
            v.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)

        # Connect submenu button actions
        self.submenu.set_controller(self)

        # Default view
        self.show_view('project_editor')

    def show_view(self, name: str) -> None:
        """Raise the requested subview in the content frame."""
        view = self.views.get(name)
        if not view:
            raise ValueError(f'Unknown view: {name}')
        view.tkraise()

    def project_menu(self, parent) -> ctk.CTkFrame:
        """Build the left submenu inside the main app."""
        return self.submenu.build(parent)
