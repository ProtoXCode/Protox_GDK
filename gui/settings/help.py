import customtkinter as ctk

class HelpView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text='Help').grid(padx=20, pady=20)
