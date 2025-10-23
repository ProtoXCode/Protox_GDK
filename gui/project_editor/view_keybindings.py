import customtkinter as ctk


class KeybindingsView(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        ctk.CTkLabel(self, text='Keybindings').pack(padx=20, pady=20)
