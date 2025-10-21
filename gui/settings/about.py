import customtkinter as ctk


class AboutView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text='About').grid(padx=20, pady=20)
