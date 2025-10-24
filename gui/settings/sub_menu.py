import customtkinter as ctk


class OptionsPanel:
    """ The submenu displayed in the left panel when using Settings view. """

    def __init__(self, controller) -> None:
        self.controller = controller  # reference to SettingsEditor

    def build(self, parent) -> ctk.CTkFrame:
        sub_menu = ctk.CTkFrame(parent)
        sub_menu.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)
        sub_menu.grid_rowconfigure(0, weight=0)
        sub_menu.grid_columnconfigure(0, weight=1)

        btn_font = ('Segoe UI', 18, 'bold')

        ctk.CTkButton(
            sub_menu,
            text='Options',
            font=btn_font,
            height=40,
            command=lambda: self.controller.show_view('options')
        ).grid(row=1, column=0, sticky='ew', pady=(20, 8), padx=40)

        ctk.CTkButton(
            sub_menu,
            text='Help',
            font=btn_font,
            height=40,
            command=lambda: self.controller.show_view('help')
        ).grid(row=2, column=0, sticky='ew', pady=8, padx=40)

        ctk.CTkButton(
            sub_menu,
            text='About',
            font=btn_font,
            height=40,
            command=lambda: self.controller.show_view('about')
        ).grid(row=3, column=0, sticky='ew', pady=8, padx=40)

        sub_menu.grid_rowconfigure(99, weight=1)

        return sub_menu
