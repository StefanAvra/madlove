"""Test setup. Runs before any game module is imported, because several of them have
side effects at import time: `sound` starts the mixer, `controls` the joystick, and
`scores` reads and writes the high-score files."""

import os
import tempfile

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import pygame as pg  # noqa: E402
import pytest  # noqa: E402

import config  # noqa: E402

# keeps the import of `scores` away from the real high-score file
config.set_data_dir(tempfile.mkdtemp(prefix='madlove-tests-'))


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """points the high-score and upload-queue files at an empty folder"""
    for name in ('DATA_DIR', 'HIGHSCORE_FILE', 'UPLOAD_QUEUE'):
        monkeypatch.setattr(config, name, getattr(config, name))
    config.set_data_dir(str(tmp_path))
    return tmp_path


@pytest.fixture
def scores(data_dir, monkeypatch):
    """the scores module with an empty high-score list and a reset combo multiplier"""
    import scores

    monkeypatch.setattr(scores, 'highscores', [])
    monkeypatch.setattr(scores, 'upload_queue', [])
    # string names, so the module's double-underscore globals aren't name-mangled
    monkeypatch.setattr(scores, '__multiplier', 0)
    monkeypatch.setattr(scores, '__decrease_timer', 0)
    monkeypatch.setattr(scores, '__last_multi', 0)
    return scores


@pytest.fixture
def coins(monkeypatch):
    """the coins module with no credit and no lives"""
    import coins

    monkeypatch.setattr(coins, '__credit', 0)
    monkeypatch.setattr(coins, '__lives', 0)
    return coins


@pytest.fixture
def game(data_dir, monkeypatch):
    """the game module with an open (headless) display and its fonts loaded, like main() does"""
    import killyourlungs

    pg.init()
    pg.display.set_mode(config.DISPLAY, config.FLAGS, config.DEPTH)
    for size in (8, 16, 24):
        monkeypatch.setattr(killyourlungs, f'font_{size}', pg.font.Font(config.FONT, size), raising=False)
    yield killyourlungs
    pg.display.quit()
