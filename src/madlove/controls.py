"""Joystick and keyboard input. The joystick is opened by init(), not at import.

In the browser, the on-screen control panel acts as a second joystick: a VirtualStick that posts the same
events as the cabinet's stick and buttons, so every scene handles it without changes.
"""

import pygame as pg

from madlove import config

joystick = None
virtual = None  # the on-screen controls in the browser


UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
START = 4
ACTION = 5

pressed = [False] * 6

INSERT_COIN = 4
DEBUG_HUD = pg.K_f
ADD_BALL = pg.K_b
ACTIVATE_BOT = pg.K_COMMA
MUTE_MUSIC = pg.K_m

# the cabinet's buttons, as joystick button numbers
START_BUTTON = 0
ACTION_BUTTON = 1


class VirtualStick:
    """the on-screen stick and buttons, posing as the cabinet's joystick.

    source is read every frame: x and y are -1, 0 or 1 (-1 is left or up, as on a joystick), start and
    action are True while held. In the browser it's the page's window.madlove_input object."""

    def __init__(self, source):
        self.source = source
        self.axes = [0, 0]
        self.buttons = [False, False]

    def get_axis(self, axis):
        return self.axes[axis]

    def get_button(self, button):
        return self.buttons[button]

    def poll(self):
        """reads the source and posts joystick events for everything that changed since the last call"""
        axes = [int(self.source.x), int(self.source.y)]
        buttons = [bool(self.source.start), bool(self.source.action)]
        for axis, (old, new) in enumerate(zip(self.axes, axes, strict=True)):
            if new != old:
                pg.event.post(pg.event.Event(pg.JOYAXISMOTION, joy=0, instance_id=0, axis=axis, value=float(new)))
        for button, (old, new) in enumerate(zip(self.buttons, buttons, strict=True)):
            if new != old:
                event_type = pg.JOYBUTTONDOWN if new else pg.JOYBUTTONUP
                pg.event.post(pg.event.Event(event_type, joy=0, instance_id=0, button=button))
        self.axes, self.buttons = axes, buttons


def init():
    """opens the first joystick, if there is one, and in the browser connects the on-screen controls"""
    global joystick, virtual
    if config.USE_JOYSTICK:
        pg.joystick.init()
        if pg.joystick.get_count():
            joystick = pg.joystick.Joystick(0)
            joystick.init()
    if config.WEB:
        from platform import window  # pygbag adds the browser's window object to this module

        virtual = VirtualStick(window.madlove_input)  # set up by web/static/madlove.js


def poll():
    """posts the events of the on-screen controls. call it once per frame, before reading the events"""
    if virtual is not None:
        virtual.poll()


def get_buttons():
    """which directions and buttons are held, from the keyboard and any joystick"""
    global pressed
    pressed_keyboard = pg.key.get_pressed()
    keys = (pg.K_UP, pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN)
    pressed[UP], pressed[LEFT], pressed[RIGHT], pressed[DOWN] = [pressed_keyboard[key] for key in keys]
    pressed[START] = pressed[ACTION] = False

    for stick in (joystick, virtual):
        if stick is None:
            continue
        updown = stick.get_axis(1)
        leftright = stick.get_axis(0)
        # negative is up, as in the menus and the name entry
        if updown < 0:
            pressed[UP] = True
        if updown > 0:
            pressed[DOWN] = True
        if leftright > 0:
            pressed[RIGHT] = True
        if leftright < 0:
            pressed[LEFT] = True
        if stick.get_button(START_BUTTON):
            pressed[START] = True
        if stick.get_button(ACTION_BUTTON):
            pressed[ACTION] = True

    return pressed
