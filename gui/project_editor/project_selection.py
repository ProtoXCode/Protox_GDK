import customtkinter as ctk


class SelectionPanel(ctk.CTkFrame):
    """Left-side navigation for the Project Editor."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.controller = None
        self.grid_columnconfigure(0, weight=1)

    def set_controller(self, controller) -> None:
        """Connect back to Project Editor for view switching."""
        self.controller = controller

    def build(self, _) -> ctk.CTkFrame:
        """(Not directly used, but keeps consistency for main app)"""
        return self

    def _switch(self, view_name: str) -> None:
        if self.controller:
            self.controller.show_view(view_name)

    def _make_button(self, text: str, command) -> None:
        ctk.CTkButton(
            self,
            text=text,
            command=command,
            anchor='w',
            fg_color='transparent'
        ).pack(fill='x', pady=4, padx=4)

    def _populate(self) -> None:
        """Add navigation buttons."""
        self._make_button('Game', lambda: self._switch('game'))
        self._make_button('Keybindings', lambda: self._switch('keybindings'))

    def grid(self, *args, **kwargs) -> None:
        # noinspection PyArgumentList
        super().grid(*args, **kwargs)
        self._populate()
