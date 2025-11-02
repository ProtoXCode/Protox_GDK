import re
import json
import logging
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from gdk.utils import load_config


class OptionsView(ctk.CTkFrame):
    """ Program options and customizations. """

    def __init__(self, parent):
        super().__init__(parent)
        self.data: dict = {}
        self.config_file = Path(
            __file__).parent.parent.parent / 'gdk' / 'config.json'

        # --- Main layout ---
        self.configure(fg_color='transparent')
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # --- Option frame ---
        self.option_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.option_frame.grid(row=0, column=0, sticky='nw', padx=20, pady=20)
        self.option_frame.grid_columnconfigure(0, weight=0)
        self.option_frame.grid_columnconfigure(1, weight=0)

        frame = ctk.CTkFrame(self.option_frame, fg_color='transparent')
        frame.grid(row=0, column=0, columnspan=2, sticky='nw', padx=8, pady=8)

        font = ('Segoe UI', 14)

        # Title
        ctk.CTkLabel(
            frame,
            text='Program Options',
            font=('Segoe UI', 24, 'bold'),
            anchor='w'
        ).grid(row=0, column=0, sticky='w', padx=8, pady=8)

        def add_row(label_text: str,
                    row: int,
                    widget: ctk.CTkEntry |
                            ctk.CTkCheckBox |
                            ctk.CTkOptionMenu |
                            ctk.CTkLabel) -> None:
            ctk.CTkLabel(
                self.option_frame,
                text=f'{label_text}:',
                font=font,
                anchor='e',
                width=140
            ).grid(row=row, column=0, sticky='e', padx=(20, 16), pady=8)
            widget.grid(row=row, column=1, sticky='w',
                        padx=(0, 20), pady=8)

        # Resolution
        self.resolution = ctk.CTkEntry(
            self.option_frame,
            font=font,
            width=100,
            placeholder_text='1575 x 825')
        add_row('Resolution', 1, self.resolution)

        # Fullscreen
        self.fullscreen = ctk.CTkCheckBox(
            self.option_frame, text='')
        add_row('Start in fullscreen', 2, self.fullscreen)

        # Fade-in
        self.fade_in = ctk.CTkCheckBox(
            self.option_frame, text='')
        add_row('Fade-in on startup', 3, self.fade_in)

        # Config file
        self.file_path = ctk.CTkLabel(
            self.option_frame,
            text=str(self.config_file),
            font=font,
            anchor='w')
        add_row('File path', 4, self.file_path)

        self.load_data()

        self.save_button = ctk.CTkButton(
            self.option_frame,
            text='Save',
            command=lambda: self.save_data(self.config_file)
        ).grid(row=10, column=0, sticky='se', padx=(20, 16), pady=8)

    def load_data(self) -> None:
        """ Loads the configuration data from the config file. """
        self.data = load_config()

        resolution = f"{self.data['app_width']} x {self.data['app_height']}"
        self.resolution.delete(0, 'end')
        self.resolution.insert(0, resolution)

        if self.data['fullscreen']:
            self.fullscreen.select()

        if self.data['fade_in']:
            self.fade_in.select()

    def save_data(self, config_file: Path) -> None:
        """ Saves the configuration data from the UI to the config file. """
        if not re.match(r'^\d+\s*x\s*\d+$', self.resolution.get()):
            messagebox.showerror(
                title='Invalid resolution',
                message=f'Improper formatting: {self.resolution.get()}\n'
                        f'Accepts formats like: 1600 x 900')
            return
        resolution = self.resolution.get().split('x')
        self.data['app_width'] = int(resolution[0].strip())
        self.data['app_height'] = int(resolution[1].strip())
        self.data['fullscreen'] = bool(self.fullscreen.get())
        self.data['fade_in'] = bool(self.fade_in.get())

        try:
            with open(config_file, 'w', encoding='utf-8') as json_data:
                json.dump(self.data, json_data, indent=4)
            logging.info('Config file updated.')
            messagebox.showinfo(
                title='Config updated',
                message='Config file successfully updated.')
        except Exception as e:
            logging.error(
                f'Failed to update config file: {self.config_file}\n{e}')
            messagebox.showerror(
                title='Error',
                message=f'Failed to update config file: {self.config_file}\n{e}')
