import customtkinter as ctk

class LevelEditor(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text='Level Editor').grid(padx=20, pady=20)
        ctk.CTkButton(self, text="Button").grid(pady=10)
