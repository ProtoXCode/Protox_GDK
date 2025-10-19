from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Optional

import customtkinter as ctk


class MetadataPanel:
    """Manages the sprite metadata sidebar and synchronisation."""

    def __init__(self, editor: 'SpriteEditor') -> None:
        self.editor = editor
        self.meta_name: Optional[ctk.CTkEntry] = None
        self.meta_author: Optional[ctk.CTkEntry] = None
        self.meta_fps: Optional[ctk.CTkEntry] = None
        self.meta_loop: Optional[ctk.BooleanVar] = None
        self.meta_tags: Optional[ctk.CTkEntry] = None
        self.prop_collision: Optional[ctk.BooleanVar] = None
        self.prop_static: Optional[ctk.BooleanVar] = None
        self.prop_background: Optional[ctk.BooleanVar] = None
        self.prop_player: Optional[ctk.BooleanVar] = None
        self._save_label: Optional[ctk.CTkLabel] = None
        self._suspend_autoapply = False

    def build(self, parent) -> ctk.CTkFrame:
        meta = ctk.CTkFrame(parent)
        meta.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)

        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        meta.rowconfigure(0, weight=1)
        meta.columnconfigure(1, weight=1)
        meta.rowconfigure('all', weight=0)

        ctk.CTkLabel(
            meta,
            text='Sprite Metadata',
            font=('Segoe UI', 14, 'bold'),
        ).grid(row=0, column=0, columnspan=2, pady=(4, 8))

        doc = self.editor.doc

        ctk.CTkLabel(meta, text='Name:').grid(
            row=1, column=0, sticky='w', pady=2)
        self.meta_name = ctk.CTkEntry(meta)
        self.meta_name.insert(0, doc.name)
        self.meta_name.grid(row=1, column=1, sticky='ew', pady=2)

        ctk.CTkLabel(meta, text='Author:').grid(
            row=2, column=0, sticky='w', pady=2)
        self.meta_author = ctk.CTkEntry(meta)
        self.meta_author.insert(0, doc.author)
        self.meta_author.grid(row=2, column=1, sticky='ew', pady=2)

        ctk.CTkLabel(meta, text='Animation FPS:').grid(
            row=3, column=0, sticky='w', pady=2)
        self.meta_fps = ctk.CTkEntry(meta, width=80, justify='center')
        self.meta_fps.insert(0, doc.fps)
        self.meta_fps.grid(row=3, column=1, sticky='ew', pady=2)

        ctk.CTkLabel(meta, text='Loop:').grid(
            row=4, column=0, sticky='w', pady=2)
        self.meta_loop = ctk.BooleanVar(value=doc.loop)
        ctk.CTkCheckBox(meta, text='', variable=self.meta_loop).grid(
            row=4, column=1, sticky='w', pady=2)

        ctk.CTkLabel(meta, text='Tags:').grid(
            row=5, column=0, sticky='w', pady=2)
        self.meta_tags = ctk.CTkEntry(meta)
        self.meta_tags.insert(0, ', '.join(doc.tags or []))
        self.meta_tags.grid(row=5, column=1, sticky='ew', pady=2)

        ctk.CTkLabel(meta, text='Properties:').grid(
            row=6, column=0, sticky='nw', pady=(6, 2))
        flags_box = ctk.CTkFrame(meta, fg_color='transparent')
        flags_box.grid(row=6, column=1, sticky='w', pady=(6, 2))

        props = doc.properties or {}
        self.prop_collision = ctk.BooleanVar(
            value=props.get('collision', False))
        self.prop_static = ctk.BooleanVar(value=props.get('static', False))
        self.prop_background = ctk.BooleanVar(
            value=props.get('background', False))
        self.prop_player = ctk.BooleanVar(value=props.get('player', False))

        ctk.CTkCheckBox(flags_box, text='Collision',
                        variable=self.prop_collision).grid(sticky='w')
        ctk.CTkCheckBox(flags_box, text='Static Asset',
                        variable=self.prop_static).grid(sticky='w')
        ctk.CTkCheckBox(flags_box, text='Background',
                        variable=self.prop_background).grid(sticky='w')
        ctk.CTkCheckBox(flags_box, text='Player Character',
                        variable=self.prop_player).grid(sticky='w')

        for entry in (self.meta_name, self.meta_author, self.meta_fps,
                      self.meta_tags):
            self._bind_autoapply(entry)

        for var in (
                self.meta_loop,
                self.prop_collision,
                self.prop_static,
                self.prop_background,
                self.prop_player,
        ):
            if var is not None:
                var.trace_add('write', self._on_var_changed)

        self.editor.frame_time_var.trace_add('write', self._sync_from_slider)

        return meta

    def apply_metadata(self) -> None:
        if self._suspend_autoapply:
            return

        doc = self.editor.doc
        if self.meta_name:
            doc.name = self.meta_name.get().strip()
        if self.meta_author:
            doc.author = self.meta_author.get().strip()
        if self.meta_fps:
            try:
                doc.fps = int(self.meta_fps.get())
            except ValueError:
                logging.warning('Invalid FPS value provided in metadata panel')
        if self.meta_loop:
            doc.loop = self.meta_loop.get()
        if self.meta_tags:
            tags_raw = self.meta_tags.get().strip()
            doc.tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

        doc.properties = {
            'collision': self.prop_collision.get() if self.prop_collision else False,
            'static': self.prop_static.get() if self.prop_static else False,
            'background': self.prop_background.get() if self.prop_background else False,
            'player': self.prop_player.get() if self.prop_player else False,
        }

        self.show_saved_status()

    def show_saved_status(self) -> None:
        """
        Displays a small saved message in green in the lower right corner.
        """
        if self._suspend_autoapply:
            return
        if self._save_label:
            self._save_label.destroy()
            self._save_label = None
        if not getattr(self.editor, 'main_app', None):
            return
        self._save_label = ctk.CTkLabel(
            self.editor.main_app.sub_menu, text='✓ Saved', text_color='green'
        )
        self._save_label.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor='se')

        # noinspection PyTypeChecker
        def _remove_label() -> None:
            if self._save_label:
                self._save_label.destroy()
                self._save_label = None

        self.editor.after(1500, _remove_label)  # type: ignore[arg-type]

    def refresh_from_doc(self) -> None:
        doc = self.editor.doc
        with self.suspend_autoapply():
            if self.meta_name:
                self.meta_name.delete(0, 'end')
                self.meta_name.insert(0, doc.name)
            if self.meta_author:
                self.meta_author.delete(0, 'end')
                self.meta_author.insert(0, doc.author)
            if self.meta_fps:
                self.meta_fps.delete(0, 'end')
                self.meta_fps.insert(0, doc.fps)
            if self.meta_tags:
                self.meta_tags.delete(0, 'end')
                self.meta_tags.insert(0, ', '.join(doc.tags or []))
            if self.meta_loop:
                self.meta_loop.set(doc.loop)
            if self.prop_collision:
                self.prop_collision.set(doc.properties.get('collision', False))
            if self.prop_static:
                self.prop_static.set(doc.properties.get('static', False))
            if self.prop_background:
                self.prop_background.set(
                    doc.properties.get('background', False))
            if self.prop_player:
                self.prop_player.set(doc.properties.get('player', False))

    def _bind_autoapply(self, widget, event_type: str = '<FocusOut>') -> None:
        if hasattr(widget, 'bind'):
            widget.bind(event_type, lambda _event: self.apply_metadata())

    def _on_var_changed(self, *_args) -> None:
        self.apply_metadata()

    def _sync_from_slider(self, *_args) -> None:
        try:
            fps = round(1000 / max(1, self.editor.frame_time_var.get()))
            if self.meta_fps:
                self.meta_fps.delete(0, 'end')
                self.meta_fps.insert(0, str(fps))
        except Exception as e:
            logging.error(e)

    @contextmanager
    def suspend_autoapply(self):
        previous = self._suspend_autoapply
        self._suspend_autoapply = True
        try:
            yield
        finally:
            self._suspend_autoapply = previous


# Late import for typing only
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sprite_editor import SpriteEditor
