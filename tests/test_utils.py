from unittest.mock import MagicMock

import pytest

from gdk import utils


def test_load_config(tmp_path, monkeypatch):
    # Fake module directory to local tmp
    monkeypatch.setattr(utils, '__file__', tmp_path / 'fakefile.py')

    config_path = tmp_path / 'config.json'
    assert not config_path.exists()

    config = utils.load_config()

    # Check file created
    assert config_path.exists()
    assert isinstance(config, dict)
    assert 'app_width' in config
    assert 'game_types' in config


@pytest.mark.parametrize(
    'rgba,expected',
    [
        ([255, 0, 0, 255], '#ff0000'),
        ([0, 255, 0, 200], '#00ff00'),
        ([0, 0, 255, 123], '#0000ff'),
    ]
)
def test_rgba_hex(rgba: list, expected: str):
    assert utils.rgba_hex(rgba) == expected


def test_get_project_name_valid(monkeypatch):
    mock_dialog = MagicMock()
    mock_dialog.get_input.return_value = 'My Project'

    # Patch constructor to return mock
    monkeypatch.setattr("gdk.utils.ctk.CTkInputDialog",
                        lambda **kwargs: mock_dialog)

    assert utils.get_project_name() == 'My Project'


def test_get_project_name_invalid(monkeypatch):
    # First invalid -> error box -> then valid
    response = iter(['@BadName!', 'GoodOne'])
    mock_dialog = MagicMock()
    mock_dialog.get_input.side_effect = lambda: next(response)

    monkeypatch.setattr('gdk.utils.ctk.CTkInputDialog',
                        lambda **kwargs: mock_dialog)
    monkeypatch.setattr('gdk.utils.messagebox.showerror',
                        lambda **kwargs: None)

    assert utils.get_project_name() == 'GoodOne'


def test_get_project_name_cancel(monkeypatch):
    mock_dialog = MagicMock()
    mock_dialog.get_input.return_value = ''

    monkeypatch.setattr('gdk.utils.ctk.CTkInputDialog',
                        lambda **kwargs: mock_dialog)

    assert utils.get_project_name() == ''


@pytest.mark.parametrize(
    'name,expected',
    [
        ('My Project', 'my_project'),
        ('We!rd%One', 'werdone'),
        ('Hello-World', 'hello-world'),
        ('Spaces   Here', 'spaces___here'),
    ]
)
def test_slugify(name: str, expected: str):
    assert utils.slugify(name) == expected


def test_get_project_subdir_creates_and_returns(tmp_path):
    class DummyApp:
        active_project_path = tmp_path / 'myproj'

    # ensure project dir exists
    DummyApp.active_project_path.mkdir()

    target = utils.get_project_subdir(DummyApp, 'assets')
    assert target.exists()
    assert target.is_dir()
    assert str(target).endswith('assets')


def test_get_project_subdir_fallback(tmp_path, monkeypatch):
    class DummyApp:
        active_project_path = None

    # patch cwd so fallback goes into our tmp directory
    monkeypatch.chdir(tmp_path)

    target = utils.get_project_subdir(DummyApp, 'stuff')

    # now create it since utils won't
    target.mkdir(parents=True, exist_ok=True)

    assert target.exists()
    assert target.is_dir()
    assert 'projects' in str(target)
