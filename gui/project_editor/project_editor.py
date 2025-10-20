from __future__ import annotations

import customtkinter as ctk

class ProjectEditor(ctk.CTkFrame):
    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app
        ctk.CTkLabel(self, text='Project Editor').grid(padx=20, pady=20)
