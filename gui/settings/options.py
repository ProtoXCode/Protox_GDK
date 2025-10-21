import customtkinter as ctk

class OptionsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text='Options').grid(padx=20, pady=20)
