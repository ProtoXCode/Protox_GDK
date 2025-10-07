import platform
import logging

import customtkinter as ctk
from PIL import Image

from gdk import __name__, __version__
from gdk.protox_tools import ProtoXToolKit
from gdk.config_loader import load_config
from gui.view_sprite import SpriteEditor
from gui.view_level import LevelEditor
from gui.view_splash import SplashScreen


class GDKMain:
    def __init__(self, root) -> None:
        """ GDK """

        self.root = root
        self.config = load_config()
        self.padding = 10
        self.menu_width = 300
        self.top_menu_height = 300

        self.app_width = self.config['app_width']
        self.app_height = self.config['app_height']

        if platform.system() == 'Windows':
            self.root.iconbitmap('assets/icons/icon.ico')
        elif platform.system() == 'Darwin':
            self.root.iconbitmap('assets/icons/icon.xbm')

        self.root.title(f'{__name__} (v{__version__})')
        ProtoXToolKit.center_screen(self.root, self.app_width, self.app_height)
        self.root.minsize(self.app_width, self.app_height)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        ctk.set_appearance_mode('dark')
        ctk.set_appearance_mode('blue')

        # --- Frames ----------------------------------------------------------
        self.top_menu = ctk.CTkFrame(
            self.root, width=self.menu_width,
            height=self.top_menu_height)
        self.top_menu.grid(row=0, column=0, sticky='nsew',
                           padx=self.padding, pady=self.padding)
        self.top_menu.grid_propagate(False)

        self.window = ctk.CTkFrame(
            self.root,
            width=self.app_width - self.menu_width - self.padding * 4,
            height=self.app_height - self.padding * 2)
        self.window.grid(row=0, column=1, sticky='nsew',
                         padx=self.padding, pady=self.padding, rowspan=2)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        base_image = Image.open('assets/images/protox.png')
        rounded_image = ProtoXToolKit.round_corners(base_image, radius=15)

        # --- Menu ------------------------------------------------------------
        self.logo_image = ctk.CTkImage(
            light_image=rounded_image,
            dark_image=rounded_image,
            size=(280, 140))
        self.label_logo = ctk.CTkLabel(
            self.top_menu, image=self.logo_image, text='')
        self.label_logo.grid(
            row=0, column=0, pady=self.padding, padx=self.padding)

        ctk.CTkButton(self.top_menu, text='Sprite', width=200, height=50,
                      command=self.sprite_editor).grid(
            row=1, column=0, pady=self.padding, padx=self.padding, )

        ctk.CTkButton(self.top_menu, text='Level', width=200, height=50,
                      command=self.level_editor).grid(
            row=2, column=0, padx=self.padding, pady=self.padding)

        # --- Views -----------------------------------------------------------
        self.views = {
            'sprite': SpriteEditor(self.window),
            'level': LevelEditor(self.window),
            'splash': SplashScreen(self.window)
        }

        for v in self.views.values():
            v.grid(row=0, column=0, sticky='nsew')

        self.splash_screen()  # Set view to default on startup

    def show_view(self, name: str) -> None:
        """ Raise the requested view to the top """
        view = self.views.get(name)
        if view is None:
            logging.critical(f'View {name} not found')
            raise RuntimeError(f'View {name} not found')
        view.tkraise()

    def splash_screen(self) -> None:
        self.show_view('splash')
        self.fade_in()

    def fade_in(self, alpha=0.0, ms=20) -> None:
        """ Fades in the app on startup """
        if alpha < 1.0:
            self.root.attributes('-alpha', alpha)
            self.root.after(ms, self.fade_in, alpha + 0.05)
        else:
            self.root.attributes('-alpha', 1.0)

    # def clear_sub_menu(self) -> None:
    #     """ Destroy all widgets in the sub_menu """
    #     for widget in self.sub_menu.winfo_children():
    #         widget.destroy()

    def sprite_editor(self) -> None:
        self.show_view('sprite')
        # self.clear_sub_menu()

    def level_editor(self) -> None:
        self.show_view('level')
        # self.clear_sub_menu()
