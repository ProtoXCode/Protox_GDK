#!/usr/bin/env python3
import customtkinter as ctk

from gui.main_window import GDKMain
from gdk.logging_setup import configure_logging

configure_logging()

if __name__ == '__main__':
    root = ctk.CTk()
    app = GDKMain(root)
    root.mainloop()
