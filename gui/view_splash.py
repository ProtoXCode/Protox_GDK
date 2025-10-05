import customtkinter as ctk
from PIL import Image

from gdk.protox_tools import ProtoXToolKit

class SplashScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        base_image = Image.open('assets/images/splash.png')
        rounded_image = ProtoXToolKit.round_corners(base_image, radius=40)

        self.splash_image = ctk.CTkImage(
            light_image=rounded_image,
            dark_image=rounded_image,
            size=(750, 750)
        )

        self.splash_image_label = ctk.CTkLabel(
            self, image=self.splash_image, text='')
        self.splash_image_label.grid(row=0, column=0, sticky='')
