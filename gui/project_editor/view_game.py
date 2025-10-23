import customtkinter as ctk


class GameView(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        ctk.CTkLabel(self, text='Game Settings').pack(padx=20, pady=20)
