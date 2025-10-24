import logging
import json
import re
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from .project_core import ProjectDoc


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
        """ Create a new project folder and base JSON file. """
        name = self._get_project_name()
        if len(name) == 0:
            return

        project_root = Path(__file__).parent.parent.parent / 'projects'
        root = name.replace(' ', '_').lower()
        project_dir = project_root / root

        #  --- Create project folder structure --------------------------------
        try:
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / 'sprites').mkdir()
            (project_dir / 'levels').mkdir()
        except FileExistsError:
            messagebox.showerror(
                title='Error',
                message=f'Project {name} already exists.')
            logging.error(f'Project directory "{root}" already exists')

        # --- Create and save the project.json file ---------------------------
        project_doc = ProjectDoc.new(name)
        project_file = project_dir / 'project.json'

        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_doc.to_json(), f, indent=4)

        logging.info(f'Created new project: {project_file}')
        messagebox.showinfo(
            title='Project Created',
            message=f'Project {name} created successfully.'
        )

    @staticmethod
    def _get_project_name() -> str:
        """ Asks user for a project name using standard characters. """
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
