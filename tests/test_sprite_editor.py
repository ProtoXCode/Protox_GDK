import customtkinter as ctk
import pytest

from gui.view_sprite import SpriteEditor


@pytest.fixture
def app():
    root = ctk.CTk()
    editor = SpriteEditor(root)
    yield editor
    root.destroy()


def test_new_doc_resets_frames(app):
    # start with a modified doc
    app.doc.name = "test"
    app.doc.frames.append(app.doc.frames[0])  # add a duplicate
    assert len(app.doc.frames) > 1

    # call the method
    app._new_doc()

    # verify it reset
    assert app.doc.name == "sprite"
    assert len(app.doc.frames) == 1
    assert app.active_frame == 0


def test_find_closest_color_returns_best_match(app):
    color = (255, 255, 255, 255)
    idx = app._find_closest_color(color)
    assert isinstance(idx, int)
    assert 0 <= idx < len(app.doc.palette)


def test_resize_grid_preserves_pixels(app):
    app.doc.frames[0].pixels[0][0] = 1
    app._resize_grid(32, 32)
    assert app.doc.frames[0].pixels[0][0] == 1
    assert app.doc.width == 32


def test_color_select_highlights_button(app):
    app._select_color(2)
    app.update_idletasks()
    assert app.active_color_index == 2
