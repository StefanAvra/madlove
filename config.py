import pygame as pg

WIDTH = 480
HEIGHT = 640
DISPLAY = (WIDTH, HEIGHT)
DEPTH = 0
GAME_TITLE = "MADLOVE"
GAME_SUBTITLE = 'THE GAME'
CAPTION = GAME_TITLE
FRAMERATE = 60
FLAGS = 0
# FLAGS = pg.FULLSCREEN

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

BACKGROUND_COLOR = "#ffb3ce"
FONT = "assets/font/PressStart2P-Regular.ttf"
TEXT_COLOR = (0, 0, 0)
MENU_COLOR_HIGHLIGHT = (255, 255, 255)
MENU_SHADOW_COLOR = (0, 0, 0)
MENU_SHADOW_OFFSET = 8
BALL_COLOR = (0, 0, 0)
DEBUG_COLOR = (255, 255, 255)
ENABLE_BOT = False
SHOW_FPS = False
SHOW_VELOCITY = False
HIGHSCORE_FILE = './scores'
FIREBASE_CRED = '/path/to/cred.json'
UPLOAD_QUEUE = './uploadqueue'
PLAYER_Y = 625
