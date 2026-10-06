import os
import sys

import pygame as pg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')


def asset(*parts):
    """returns the absolute path of a file in the assets folder"""
    return os.path.join(ASSETS_DIR, *parts)


def default_data_dir():
    """per-user folder for high scores, following each platform's convention"""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
        return os.path.join(base, 'MadLove')
    if sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Application Support/MadLove')
    base = os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share')
    return os.path.join(base, 'madlove')


def set_data_dir(path):
    """stores high scores and the upload queue in path, creating it if needed"""
    global DATA_DIR, HIGHSCORE_FILE, UPLOAD_QUEUE
    os.makedirs(path, exist_ok=True)
    DATA_DIR = path
    HIGHSCORE_FILE = os.path.join(path, 'scores')
    UPLOAD_QUEUE = os.path.join(path, 'uploadqueue')


WIDTH = 480
HEIGHT = 640
DISPLAY = (WIDTH, HEIGHT)
DEPTH = 0
GAME_TITLE = "MADLOVE"
GAME_SUBTITLE = 'THE GAME'
CAPTION = GAME_TITLE
FRAMERATE = 60
# SCALED renders through an opaque (alpha-free) display surface on every platform, which
# the drawing code relies on, and scales the picture to fit the screen in fullscreen
FLAGS = pg.SCALED

# pg.FULLSCREEN   create a fullscreen display
# pg.DOUBLEBUF    recommended for HWSURFACE or OPENGL
# pg.HWSURFACE    hardware accelerated, only in FULLSCREEN
# pg.OPENGL       create an OpenGL-renderable display
# pg.RESIZABLE    display window should be sizeable
# pg.NOFRAME      display window will have no border or controls

USE_JOYSTICK = True

FREE_MODE = True
LOCATION = 'virtual'
CABINET_ID = 0
OFFLINE_MODE = True

BACKGROUND_COLOR = "#ffb3ce"
FONT = asset('font', 'PressStart2P-Regular.ttf')
TEXT_COLOR = (0, 0, 0)
MENU_COLOR_HIGHLIGHT = (255, 255, 255)
MENU_SHADOW_COLOR = (0, 0, 0)
MENU_SHADOW_OFFSET = 8
BALL_COLOR = (0, 0, 0)
DEBUG_COLOR = (255, 255, 255)
ENABLE_BOT = False
SHOW_FPS = False
SHOW_VELOCITY = False
DATA_DIR = default_data_dir()
HIGHSCORE_FILE = os.path.join(DATA_DIR, 'scores')
UPLOAD_QUEUE = os.path.join(DATA_DIR, 'uploadqueue')
FIREBASE_CRED = '/path/to/cred.json'
PLAYER_Y = 625
