import re
from tkinter import messagebox

import customtkinter as ctk


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
