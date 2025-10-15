import customtkinter as ctk


class LevelEditor(ctk.CTkFrame):
    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app
        ctk.CTkLabel(self, text='Level Editor').grid(padx=20, pady=20)
        ctk.CTkButton(self, text="Button").grid(pady=10)
