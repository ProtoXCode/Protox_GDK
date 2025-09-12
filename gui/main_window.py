import customtkinter as ctk

from gdk.protox_tools import ProtoXToolKit


class GDKMain:
    def __init__(self, root) -> None:
        """
        GDK
        """

        program_name = 'ProtoX Game Developer Kit'
        program_version = '0.1'

        app_width = 1500 # TODO: Move to config!
        app_height = 800

        self.root = root
        self.root.title(f'{program_name} (v{program_version})')
        ProtoXToolKit.center_screen(root, app_width, app_height)
        ctk.set_appearance_mode('dark')
        ctk.set_appearance_mode('blue')
