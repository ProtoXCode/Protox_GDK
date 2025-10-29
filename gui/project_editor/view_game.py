from pathlib import Path

import customtkinter as ctk


class GameView(ctk.CTkFrame):
    """ Displays the currently loaded projects metadata and editable properties. """

    def __init__(self, parent, main_app=None) -> None:
        super().__init__(parent)
        self.project_path: Path | None = None
        self.main_app = main_app
        self.config = main_app.config if main_app else {}

        # Pull game types from config, with fallback
        self.game_types = self.config.get('game_types', ['Platformer', 'RPG'])

        # --- Main layout ---
        self.configure(fg_color='transparent')
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # --- Title row ---
        title_frame = ctk.CTkFrame(self, fg_color='transparent')
        title_frame.grid(row=0, column=0, sticky='ew', padx=40, pady=(30, 10))
        title_frame.grid_columnconfigure(0, weight=0)
        title_frame.grid_columnconfigure(1, weight=0)
        title_frame.grid_columnconfigure(2, weight=1)

        # Project title
        self.project_title = ctk.CTkLabel(
            title_frame,
            text='No project loaded',
            font=('Segoe UI', 24, 'bold'),
            anchor='w')
        self.project_title.grid(row=0, column=0, sticky='w')

        ctk.CTkLabel(title_frame, text='').grid(row=0, column=2, sticky='ew')

        # --- Properties frame ---
        self.properties_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.properties_frame.grid(
            row=1, column=0, columnspan=2, sticky='nw', padx=80, pady=(10, 0))
        self.properties_frame.grid_columnconfigure(0, weight=0)
        self.properties_frame.grid_columnconfigure(1, weight=1)

        font = ('Segoe UI', 14)

        def add_row(label_text: str,
                    row: int,
                    widget: ctk.CTkEntry |
                            ctk.CTkCheckBox |
                            ctk.CTkOptionMenu) -> None:
            ctk.CTkLabel(
                self.properties_frame,
                text=f'{label_text}:',
                font=font,
                anchor='e',
                width=140
            ).grid(row=row, column=0, sticky='e', padx=(20, 16), pady=8)
            widget.grid(row=row, column=1, sticky='ew', padx=(0, 20), pady=8)

        # Author
        self.author = ctk.CTkEntry(
            self.properties_frame,
            font=font,
            placeholder_text='Unknown',
            state='disabled')
        add_row('Author', 0, self.author)

        # Resolution
        self.resolution = ctk.CTkEntry(
            self.properties_frame,
            font=font,
            placeholder_text='800 x 600',
            state='disabled')
        add_row('Resolution', 1, self.resolution)

        # Fullscreen
        self.fullscreen = ctk.CTkCheckBox(
            self.properties_frame, text='', state='disabled')
        add_row('Fullscreen', 2, self.fullscreen)

        # Game Type
        self.game_type = ctk.CTkOptionMenu(
            self.properties_frame,
            values=self.game_types,
            state='disabled')
        add_row('Game Type', 3, self.game_type)

        # Gravity
        self.gravity = ctk.CTkCheckBox(
            self.properties_frame, text='', state='disabled')
        add_row('Gravity', 4, self.gravity)

        # --- Save Button ---
        self.save_button = ctk.CTkButton(
            self,
            text='Save Project',
            height=40,
            width=100,
            fg_color='darkgreen',
            state='disabled',
            command=self.save)
        self.grid_rowconfigure(2, weight=0)
        self.save_button.grid(
            row=2, column=0, sticky='sw', padx=(60, 10), pady=(10, 40))

        # --- Delete Button ---
        self.delete_button = ctk.CTkButton(
            self,
            text='Delete Project',
            height=40,
            width=100,
            fg_color='darkred',
            state='disabled',
            command=self.delete)
        self.delete_button.grid(
            row=2, column=1, sticky='se', padx=(10, 60), pady=(10, 40))

        # --- Rename button ---
        self.rename_button = ctk.CTkButton(
            title_frame,
            text='Rename',
            width=30,
            state='disabled',
            command=self.rename
        )
        self.rename_button.grid(row=0, column=1, sticky='w', padx=(10, 0))

    def rename(self) -> None:
        print('Rename')

    def load(self, project_file: dict) -> None:
        """ Gets data from the project file, updates page. """

        # Update title
        self.project_title.configure(text=project_file['project_name'])

        # Update author
        self.author.delete(0, 'end')
        self.author.insert(0, project_file['author'])

        # Update resolution
        resolution = (f'{project_file['properties']['resolution'][0]} x '
                      f'{project_file['properties']['resolution'][1]}')
        self.resolution.delete(0, 'end')
        self.resolution.insert(0, resolution)

        # Update fullscreen
        if project_file['properties']['fullscreen']:
            self.fullscreen.select()

        # Update gravity
        if project_file['properties']['gravity']:
            self.gravity.select()

        # Update game type
        self.game_type.set(project_file['properties']['game_type'])

    def save(self) -> None:
        print('Save')

    def delete(self) -> None:
        print('Delete')
