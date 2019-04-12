import pygame as pg

WIDTH = 480
HEIGHT = 640
DISPLAY = (WIDTH, HEIGHT)
DEPTH = 0
GAME_TITLE = "KILL YOUR LUNGS"
GAME_SUBTITLE = 'THE GAME'
CAPTION = GAME_TITLE
FRAMERATE = 60
FLAGS = pg.FULLSCREEN

# pg.FULLSCREEN   create a fullscreen display
# pg.DOUBLEBUF    recommended for HWSURFACE or OPENGL
# pg.HWSURFACE    hardware accelerated, only in FULLSCREEN
# pg.OPENGL       create an OpenGL-renderable display
# pg.RESIZABLE    display window should be sizeable
# pg.NOFRAME      display window will have no border or controls

USE_JOYSTICK = True

BACKGROUND_COLOR = "#ffb3ce"
FONT = "assets/font/PressStart2P-Regular.ttf"
TEXT_COLOR = (0, 0, 0)
MENU_COLOR_HIGHLIGHT = (255, 255, 255)
MENU_SHADOW_COLOR = (0, 0, 0)
MENU_SHADOW_OFFSET = 8
BALL_COLOR = (0, 0, 0)
DEBUG_COLOR = (255, 255, 255)
ENABLE_BOT = False
SHOW_FPS = True
SHOW_VELOCITY = True
HIGHSCORE_FILE = './scores'
PLAYER_Y = 625
