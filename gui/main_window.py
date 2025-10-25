import platform
import logging

import customtkinter as ctk
from PIL import Image

from gdk import __name__, __version__
from gdk.protox_tools import ProtoXToolKit
from gdk.config_loader import load_config
from gui.project_editor import ProjectEditor
from gui.settings import SettingsEditor
from gui.sprite_editor import SpriteEditor
from gui.level_editor import LevelEditor
from gui.splash_screen.splash_screen import SplashScreen
from gui.scene_editor import SceneEditor


class GDKMain:
    def __init__(self, root) -> None:
        """ GDK """
        self.root = root
        self.config = load_config()
        self.padding = 10
        self.menu_width = 300
        self.top_menu_height = 410
        self.started = False

        self.root.attributes('-fullscreen', self.config['fullscreen'])

        min_width = 1575  # Minimum size for the GUI
        min_height = 825

        self.app_width = max(self.config['app_width'], min_width)
        self.app_height = max(self.config['app_height'], min_height)

        if platform.system() == 'Windows':
            self.root.iconbitmap('assets/icons/icon.ico')
        elif platform.system() == 'Darwin':
            self.root.iconbitmap('assets/icons/icon.xbm')

        self.root.title(f'{__name__} (v{__version__})')
        ProtoXToolKit.center_screen(self.root, self.app_width, self.app_height)
        self.root.minsize(self.app_width, self.app_height)

        self.root.grid_rowconfigure(0, weight=0, minsize=self.top_menu_height)
        self.root.grid_rowconfigure(1, weight=1)
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
        self.top_menu.grid_rowconfigure(99, weight=1)

        self.sub_menu = ctk.CTkFrame(
            self.root, width=self.menu_width,
            height=self.app_height - self.padding * 4 - self.top_menu_height)
        self.sub_menu.grid(row=1, column=0, sticky='nsew',
                           padx=self.padding, pady=self.padding)
        self.sub_menu.rowconfigure(0, weight=1)
        self.sub_menu.columnconfigure(0, weight=1)
        self.sub_menu.grid_propagate(False)

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

        self.logo_button = ctk.CTkButton(
            self.top_menu,
            text='',
            image=self.logo_image,
            border_width=0,
            fg_color='transparent',
            hover=False,
            command=self.splash_screen
        ).grid(row=0, column=0, pady=self.padding)

        # --- Buttons ---
        btn_font = ('arial.ttf', 20)
        btn_text_color = (255, 255, 255, 255)
        btn_text_color_outline = (0, 0, 0, 255)
        btn_radius = 8
        btn_outline = 3

        btn_1_base = 'assets/images/btn_1.png'
        btn_2_base = 'assets/images/btn_2.png'
        btn_3_base = 'assets/images/btn_3.png'
        btn_4_base = 'assets/images/btn_4.png'
        btn_5_base = 'assets/images/btn_5.png'

        # Rounded + text composited
        btn_1_img_pil = ProtoXToolKit.image_text(
            image=btn_1_base, text='Projects',
            bold=True, outline=btn_outline,
            outline_color=btn_text_color_outline,
            font=btn_font, fill=btn_text_color)
        btn_1_img_pil = ProtoXToolKit.round_corners(
            btn_1_img_pil, radius=btn_radius)

        btn_2_img_pil = ProtoXToolKit.image_text(
            image=btn_2_base, text='Sprite Editor',
            bold=True, outline=btn_outline,
            outline_color=btn_text_color_outline,
            font=btn_font, fill=btn_text_color)
        btn_2_img_pil = ProtoXToolKit.round_corners(
            btn_2_img_pil, radius=btn_radius)

        btn_3_img_pil = ProtoXToolKit.image_text(
            image=btn_3_base, text='Level Editor',
            bold=True, outline=btn_outline,
            outline_color=btn_text_color_outline,
            font=btn_font, fill=btn_text_color)
        btn_3_img_pil = ProtoXToolKit.round_corners(
            btn_3_img_pil, radius=btn_radius)

        btn_4_img_pil = ProtoXToolKit.image_text(
            image=btn_4_base, text='Scene Editor',
            bold=True, outline=btn_outline,
            outline_color=btn_text_color_outline,
            font=btn_font, fill=btn_text_color)
        btn_4_img_pil = ProtoXToolKit.round_corners(
            btn_4_img_pil, radius=btn_radius)

        btn_5_img_pil = ProtoXToolKit.image_text(
            image=btn_5_base, text='Settings / Help',
            bold=True, outline=btn_outline,
            outline_color=btn_text_color_outline,
            font=btn_font, fill=btn_text_color)
        btn_5_img_pil = ProtoXToolKit.round_corners(
            btn_5_img_pil, radius=btn_radius)

        btn_1_img = ctk.CTkImage(
            light_image=btn_1_img_pil,
            dark_image=btn_1_img_pil,
            size=(200, 40))

        btn_2_img = ctk.CTkImage(
            light_image=btn_2_img_pil,
            dark_image=btn_2_img_pil,
            size=(200, 40))

        btn_3_img = ctk.CTkImage(
            light_image=btn_3_img_pil,
            dark_image=btn_3_img_pil,
            size=(200, 40))

        btn_4_img = ctk.CTkImage(
            light_image=btn_4_img_pil,
            dark_image=btn_4_img_pil,
            size=(200, 40))

        btn_5_img = ctk.CTkImage(
            light_image=btn_5_img_pil,
            dark_image=btn_5_img_pil,
            size=(200, 40))

        ctk.CTkButton(self.top_menu, text='', image=btn_1_img,
                      border_width=0, fg_color='transparent',
                      command=self.project_editor).grid(
            row=1, column=0, padx=1)

        ctk.CTkButton(self.top_menu, text='', image=btn_2_img,
                      border_width=0, fg_color='transparent',
                      command=self.sprite_editor).grid(
            row=2, column=0, padx=1)

        ctk.CTkButton(self.top_menu, text='', image=btn_3_img,
                      border_width=0, fg_color='transparent',
                      command=self.level_editor).grid(
            row=3, column=0, pady=1)

        ctk.CTkButton(self.top_menu, text='', image=btn_4_img,
                      border_width=0, fg_color='transparent',
                      command=self.scene_editor).grid(
            row=4, column=0, pady=1)

        ctk.CTkButton(self.top_menu, text='', image=btn_5_img,
                      border_width=0, fg_color='transparent',
                      command=self.settings_editor).grid(
            row=5, column=0, padx=1)

        # --- Views -----------------------------------------------------------
        self.views = {
            'project': ProjectEditor(self.window, main_app=self),
            'sprite': SpriteEditor(self.window, main_app=self),
            'level': LevelEditor(self.window, main_app=self),
            'splash': SplashScreen(self.window, main_app=self),
            'scene': SceneEditor(self.window, main_app=self),
            'settings': SettingsEditor(self.window, main_app=self)
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
        """ Displays the splash screen on start up with news in sub menu. """
        self.show_view('splash')
        splash = self.views['splash']
        if hasattr(splash, 'build_submenu'):
            self.set_submenu(splash.build_submenu)
        else:
            self.clear_sub_menu()
        if not self.started:
            if self.config['fade_in']:
                self.fade_in()
            self.started = True

    def fade_in(self, alpha: float = 0.0, ms: int = 20) -> None:
        """ Fades in the app on startup """
        if alpha < 1.0:
            self.root.attributes('-alpha', alpha)
            self.root.after(ms, self.fade_in, alpha + 0.05)
        else:
            self.root.attributes('-alpha', 1.0)

    def set_submenu(self, builder_fn) -> None:
        for child in self.sub_menu.winfo_children():
            child.destroy()
        builder_fn(self.sub_menu)

    def clear_sub_menu(self) -> None:
        """ Destroy all widgets in the sub_menu """
        for widget in self.sub_menu.winfo_children():
            widget.destroy()

    def project_editor(self) -> None:
        self.show_view('project')
        project = self.views['project']
        if hasattr(project, 'build_submenu'):
            self.set_submenu(project.build_submenu)
        else:
            self.clear_sub_menu()

    def sprite_editor(self) -> None:
        self.show_view('sprite')
        sprite = self.views['sprite']
        if hasattr(sprite, 'build_submenu'):
            self.set_submenu(sprite.build_submenu)
        else:
            self.clear_sub_menu()

    def level_editor(self) -> None:
        self.show_view('level')
        level = self.views['level']
        if hasattr(level, 'build_submenu'):
            self.set_submenu(level.build_submenu)
        else:
            self.clear_sub_menu()

    def scene_editor(self) -> None:
        self.show_view('scene')
        scene = self.views['scene']
        if hasattr(scene, 'build_submenu'):
            self.set_submenu(scene.build_submenu)
        else:
            self.clear_sub_menu()

    def settings_editor(self) -> None:
        self.show_view('settings')
        settings = self.views['settings']
        if hasattr(settings, 'build_submenu'):
            self.set_submenu(settings.build_submenu)
        else:
            self.clear_sub_menu()
