import platform
import logging

import customtkinter as ctk

from gdk.protox_tools import ProtoXToolKit
from gdk.config_loader import load_config
from gui.view_sprite import SpriteEditor
from gui.view_level import LevelEditor


class GDKMain:
    def __init__(self, root) -> None:
        """ GDK """

        program_name = 'ProtoX Game Developer Kit'
        program_version = '0.1'

        self.root = root
        self.config = load_config()
        self.padding = 10
        self.menu_width = 400

        self.app_width = self.config['app_width']
        self.app_height = self.config['app_height']

        if platform.system() == 'Windows':
            self.root.iconbitmap('assets/icons/icon.ico')
        elif platform.system() == 'Darwin':
            self.root.iconbitmap('assets/icons/icon.xbm')

        self.root.title(f'{program_name} (v{program_version})')
        ProtoXToolKit.center_screen(self.root, self.app_width, self.app_height)
        self.root.minsize(self.app_width, self.app_height)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        ctk.set_appearance_mode('dark')
        ctk.set_appearance_mode('blue')

        # --- Frames --- #
        self.menu = ctk.CTkFrame(
            self.root, width=self.menu_width,
            height=self.app_height - self.padding * 2)
        self.menu.grid(row=0, column=0, sticky='nsew',
                       padx=self.padding, pady=self.padding)

        self.window = ctk.CTkFrame(
            self.root,
            width=self.app_width - self.menu_width - self.padding * 4,
            height=self.app_height - self.padding * 2)
        self.window.grid(row=0, column=1, sticky='nsew',
                         padx=self.padding, pady=self.padding)

        # --- Views --- #
        self.views = {
            'sprite': SpriteEditor(self.window),
            'level': LevelEditor(self.window)
        }

        for v in self.views.values():
            v.grid(row=0, column=0, sticky='nsew')

    def show_view(self, name: str) -> None:
        """ Raise the requested view to the top """
        view = self.views.get(name)
        if view is None:
            logging.critical(f'View {name} not found')
            raise RuntimeError(f'View {name} not found')
        view.tkraise()
