import customtkinter as ctk


class OptionsPanel:
    """ The submenu displayed in the left panel when using Settings view. """

    def __init__(self, controller):
        self.controller = controller  # reference to SettingsEditor

    def build(self, parent) -> ctk.CTkFrame:
        sub_menu = ctk.CTkFrame(parent)
        sub_menu.grid(row=0, column=0, sticky='nsew', pady=8, padx=8)
        sub_menu.grid_rowconfigure(0, weight=0)
        sub_menu.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            sub_menu,
            text='Options',
            command=lambda: self.controller.show_view('options')
        ).grid(row=1, column=0, sticky='ew', pady=(20, 8), padx=20)

        ctk.CTkButton(
            sub_menu,
            text='Help',
            command=lambda: self.controller.show_view('help')
        ).grid(row=2, column=0, sticky='ew', pady=8, padx=20)

        ctk.CTkButton(
            sub_menu,
            text='About',
            command=lambda: self.controller.show_view('about')
        ).grid(row=3, column=0, sticky='ew', pady=8, padx=20)

        sub_menu.grid_rowconfigure(99, weight=1)

        return sub_menu
