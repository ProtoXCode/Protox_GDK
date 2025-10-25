from pathlib import Path

import customtkinter as ctk


class GameView(ctk.CTkFrame):
    """ Displays the currently loaded projects metadata and editable properties. """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.project_path: Path | None = None

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

        # Rename button
        ctk.CTkButton(
            title_frame,
            text='Rename',
            width=30,
            state='disabled',
            command=self.rename
        ).grid(row=0, column=1, sticky='w', padx=(10, 0))

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
            values=['Platformer', 'RPG'],
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

    def rename(self) -> None:
        print('Rename')

    def load(self) -> None:
        print('Load')

    def save(self) -> None:
        print('Save')

    def delete(self) -> None:
        print('Delete')
