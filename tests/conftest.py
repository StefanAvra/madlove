import os

# no window and no sound, also on machines that have them
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import pygame as pg  # noqa: E402
import pytest  # noqa: E402

from madlove import config  # noqa: E402


@pytest.fixture
def settings(tmp_path):
    """free play, with high scores saved in an empty folder"""
    return config.Settings(data_dir=str(tmp_path))


@pytest.fixture
def game(settings):
    """a game with an open (headless) display and its fonts loaded, before its first frame"""
    from madlove import killyourlungs

    yield killyourlungs.Game(settings)
    pg.display.quit()
