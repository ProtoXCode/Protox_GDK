import logging
import os
import re
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk


class ProjectLoader:
    """ The submenu displayed in the left panel when using Project view. """

    def __init__(self, controller) -> None:
        self.controller = controller

    def build(self, parent) -> ctk.CTkFrame:
        sub_menu = ctk.CTkFrame(parent)
        sub_menu.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)
        sub_menu.rowconfigure(0, weight=0)
        sub_menu.columnconfigure(0, weight=1)

        btn_font = ('Segoe UI', 18, 'bold')

        ctk.CTkButton(
            sub_menu,
            text='Create Project',
            font=btn_font,
            height=40,
            command=self.create_project,
        ).grid(row=1, column=0, sticky='ew', padx=40, pady=20)

        return sub_menu

    def create_project(self) -> None:
        name = self._get_project_name()
        if len(name) == 0:
            return

        print(f'Project name: {name}')

        project_root = Path(__file__).parent.parent.parent / 'projects'
        root = name.replace(' ', '_').lower()
        print(project_root)

        try:
            # Create project dir and subfolders:
            os.mkdir(os.path.join(project_root, root))
            os.mkdir(os.path.join(project_root, root, 'sprites'))
            os.mkdir(os.path.join(project_root, root, 'levels'))
        except OSError:
            messagebox.showerror(
                title='Error',
                message='Project already exists.'
            )
            logging.error('Project directory already exists')

    @staticmethod
    def _get_project_name() -> str | None:
        while True:
            project = ctk.CTkInputDialog(
                text='Select a project name',
                title='Create new Project'
            )

            name = project.get_input()

            # Allow letters, digits, spaces, underscores and dashes
            if re.match(r'^[\w\s-]+$', name):
                return name.strip()

            illegal_chars = sorted(set(re.sub(r'[\w\s-]', '', name)))
            messagebox.showerror(
                title='Illegal Project Name',
                message='Project name contains illegal characters:\n'
                        f'{', '.join(illegal_chars)}'
            )
