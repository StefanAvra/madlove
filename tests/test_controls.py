from types import SimpleNamespace

import pygame as pg
import pytest

from madlove import controls


@pytest.fixture
def source():
    """stands in for the page's window.madlove_input"""
    return SimpleNamespace(x=0, y=0, start=False, action=False)


@pytest.fixture
def stick(game, source, monkeypatch):
    stick = controls.VirtualStick(source)
    monkeypatch.setattr(controls, 'virtual', stick)
    pg.event.clear()
    return stick


def posted():
    return [(event.type, event.dict) for event in pg.event.get((pg.JOYAXISMOTION, pg.JOYBUTTONDOWN, pg.JOYBUTTONUP))]


def test_posts_nothing_without_a_change(stick):
    controls.poll()
    assert posted() == []


def test_posts_axis_motion(stick, source):
    source.x, source.y = 1, -1
    controls.poll()
    assert posted() == [
        (pg.JOYAXISMOTION, {'joy': 0, 'instance_id': 0, 'axis': 0, 'value': 1.0}),
        (pg.JOYAXISMOTION, {'joy': 0, 'instance_id': 0, 'axis': 1, 'value': -1.0}),
    ]
    controls.poll()
    assert posted() == []
    source.y = 0
    controls.poll()
    assert posted() == [(pg.JOYAXISMOTION, {'joy': 0, 'instance_id': 0, 'axis': 1, 'value': 0.0})]


def test_posts_button_down_and_up(stick, source):
    source.action = True
    controls.poll()
    assert posted() == [(pg.JOYBUTTONDOWN, {'joy': 0, 'instance_id': 0, 'button': controls.ACTION_BUTTON})]
    source.action = False
    source.start = True
    controls.poll()
    assert posted() == [
        (pg.JOYBUTTONDOWN, {'joy': 0, 'instance_id': 0, 'button': controls.START_BUTTON}),
        (pg.JOYBUTTONUP, {'joy': 0, 'instance_id': 0, 'button': controls.ACTION_BUTTON}),
    ]


@pytest.mark.parametrize(
    'x, y, held',
    [
        (0, -1, controls.UP),
        (0, 1, controls.DOWN),
        (-1, 0, controls.LEFT),
        (1, 0, controls.RIGHT),
    ],
)
def test_get_buttons_reads_the_stick(stick, source, x, y, held):
    # negative y is up, as in the menus and the name entry
    source.x, source.y = x, y
    controls.poll()
    pressed = controls.get_buttons()
    assert [index for index, on in enumerate(pressed) if on] == [held]


def test_get_buttons_reads_the_buttons(stick, source):
    source.start = source.action = True
    controls.poll()
    pressed = controls.get_buttons()
    assert pressed[controls.START] and pressed[controls.ACTION]


def test_get_buttons_without_a_stick(game):
    assert not any(controls.get_buttons())
