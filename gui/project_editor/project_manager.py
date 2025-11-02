import logging
import json
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from .project_core import ProjectDoc
from .view_game import GameView
from gdk.utils import get_project_name, slugify


class ProjectLoader:
    """ The submenu displayed in the left panel when using Project view. """

    def __init__(self, controller) -> None:
        self.controller = controller
        self.projects_buttons: list[ctk.CTkButton] = []

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

        # --- Container for dynamic project buttons ---------------------------

        self.projects_frame = ctk.CTkFrame(sub_menu)
        self.projects_frame.grid(
            row=2, column=0, sticky='nsew', padx=4, pady=4)
        self.projects_frame.columnconfigure(0, weight=1)
        sub_menu.rowconfigure(2, weight=1)

        # Initial scan
        self.scan_projects()

        return sub_menu

    def create_project(self) -> None:
        """ Create a new project folder and base JSON file. """
        name = get_project_name()
        if len(name) == 0:
            return

        project_root = Path(__file__).parent.parent.parent / 'projects'
        root = slugify(name)
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

        self.scan_projects()

    def scan_projects(self) -> None:
        """ Scan the projects folder and create project buttons. """
        project_root = Path(__file__).parent.parent.parent / 'projects'
        if not project_root.exists():
            project_root.mkdir()

        for btn in self.projects_buttons:
            btn.destroy()
        self.projects_buttons.clear()

        row = 0
        for path in project_root.iterdir():
            project_file = path / 'project.json'
            if not project_file.exists():
                continue

            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                project_name = data.get('project_name', path.name)
            except Exception as e:
                project_name = f'{path.name} (invalid)'
                logging.critical(f'[WARN] Could not read {project_file}: {e}')

            btn = ctk.CTkButton(
                self.projects_frame,
                text=project_name,
                height=36,
                command=lambda p=path: self.load_project(p)
            )
            btn.grid(row=row, column=0, sticky='ew', padx=8, pady=8)
            self.projects_buttons.append(btn)
            row += 1

    def load_project(self, project_path: Path) -> None:
        """ Called when clicking a project button, loads and enables buttons. """
        project_file = project_path / 'project.json'
        if not project_file.exists():
            messagebox.showerror(
                title='Error',
                message=f'Missing project.json in selected project folder.')
            return

        game_view: GameView = self.controller.views['game']

        # Enable controls
        for widget in (
                game_view.save_button,
                game_view.delete_button,
                game_view.rename_button,
                game_view.author,
                game_view.resolution,
                game_view.fullscreen,
                game_view.game_type,
                game_view.gravity
        ):
            widget.configure(state='normal')

        with open(project_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Populate data
        game_view.load(project_file=data, project_path=project_path)

        # Set default file path
        self.controller.main_app.active_project_path = project_path

        try:
            io_manager = self.controller.views['sprite'].io_manager
            io_manager._last_open_dir = None
            io_manager._last_save_dir = None
            io_manager._last_import_dir = None
            io_manager._last_export_dir = None
        except Exception as e:
            logging.debug(f'Failed to load sprite:\n{e}')

        project_name = data.get('project_name', project_path.name)
        logging.info(f'Loaded project: {project_name}')
