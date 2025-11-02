import logging
import json
import re
import os
from tkinter import messagebox
from pathlib import Path

import customtkinter as ctk


def load_config() -> dict:
    """ Load the config file, creates a new default one if it doesn't exist """

    config_file = os.path.join(os.path.dirname(__file__), 'config.json')

    try:
        with open(config_file, encoding='utf-8', mode='r') as json_data:
            config = json.load(json_data)

    except FileNotFoundError:
        config = {'app_width': 1575,
                  'app_height': 825,
                  'fullscreen': False,
                  'fade_in': True,
                  'game_types': [
                      'Platformer',
                      'RPG',
                      'Fighter',
                      'Shooter'
                  ]}
        with open(config_file, encoding='utf-8', mode='w') as json_data:
            json.dump(config, json_data, indent=4)
        logging.info('Default config file created')

    return config


def rgba_hex(rgba: list[int]) -> str:
    """ CTk buttons accept #RRGGBB; we ignore alpha for the button swatch """
    r, g, b, a = rgba
    return f'#{r:02x}{g:02x}{b:02x}'


def get_project_name() -> str:
    """ Asks user for a project name using standard characters. """
    while True:
        project = ctk.CTkInputDialog(
            text='Select a project name',
            title='Create new Project'
        )

        name = project.get_input()

        if not name:
            return ''

        # Allow letters, digits, spaces, underscores and dashes
        if re.match(r'^[\w\s-]+$', name):
            return name.strip()

        illegal_chars = sorted(set(re.sub(r'[\w\s-]', '', name)))
        messagebox.showerror(
            title='Illegal Project Name',
            message='Project name contains illegal characters:\n'
                    f'{', '.join(illegal_chars)}'
        )


def slugify(name: str) -> str:
    """ Folder safe name (spaces to _, lowercase; keep letters/digits/_/- """
    return re.sub(r'[^a-z0-9_-]', '', name.replace(' ', '_').lower())


def get_project_subdir(main_app, sub: str) -> Path:
    try:
        base = main_app.active_project_path
        if base:
            target = base / sub
            target.mkdir(exist_ok=True)
            return target
    except Exception as e:
        logging.error(f'Error getting subdir for {sub}: {e}')
    return Path.cwd() / 'projects' / sub


def normalize_path(path: str | Path) -> str:
    """ Return a consistent, forward-slash path string. """
    try:
        return Path(path).resolve().as_posix()
    except Exception:
        return str(path).replace('\\', '/')
