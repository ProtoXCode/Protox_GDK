import customtkinter as ctk


class ProjectEditorView(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        ctk.CTkLabel(self, text='Project Editor').pack(padx=20, pady=20)
        self.configure(fg_color='transparent')
