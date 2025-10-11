import customtkinter as ctk
import pytest

from gui.main_window import GDKMain


@pytest.fixture
def app():
    root = ctk.CTk()
    app = GDKMain(root)
    yield app
    app.root.destroy()


def test_app_title(app):
    assert app.root.title().startswith('ProtoX Game Developer Kit')


def test_frames_created(app):
    assert app.top_menu.winfo_exists()
    assert app.sub_menu.winfo_exists()
    assert app.window.winfo_exists()


def test_views_exist(app):
    assert 'sprite' in app.views
    assert 'level' in app.views
    assert 'splash' in app.views
    assert 'scene' in app.views


def test_invalid_view(app):
    with pytest.raises(RuntimeError):
        app.show_view('not_a_real_view')
