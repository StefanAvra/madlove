import pygame as pg
import config

joystick = None


UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
START = 4
ACTION = 5

pressed = [False] * 6

if config.USE_JOYSTICK:
    pg.joystick.init()
    if pg.joystick.get_count():
        joystick = pg.joystick.Joystick(0)
        joystick.init()


INSERT_COIN = 4
DEBUG_HUD = pg.K_f
ADD_BALL = pg.K_b
ACTIVATE_BOT = pg.K_COMMA
MUTE_MUSIC = pg.K_m


def get_buttons():
    global pressed
    for key in (UP, DOWN, LEFT, RIGHT, START, ACTION):
        pressed[key] = False

    if joystick is not None:
        updown = joystick.get_axis(1)
        leftright = joystick.get_axis(0)
        start = joystick.get_button(0)
        action = joystick.get_button(1)

        if updown > 0:
            pressed[UP] = True
        if updown < 0:
            pressed[DOWN] = True
        if leftright > 0:
            pressed[RIGHT] = True
        if leftright < 0:
            pressed[LEFT] = True
        if start:
            pressed[START] = True
        if action:
            pressed[ACTION] = True

    else:
        pressed_keyboard = pg.key.get_pressed()
        pressed[UP], pressed[LEFT], pressed[RIGHT], pressed[DOWN] = [pressed_keyboard[key] for key in (pg.K_UP, pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN)]

    # print(pressed)

    return pressed


