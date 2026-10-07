"""The browser version stops while its page is hidden or has lost focus, and comes back in the smoke break."""

import asyncio
from types import SimpleNamespace

import pygame as pg
import pytest

from madlove import audio
from madlove import game as game_module
from madlove.scenes import menu, play, title

AWAY = 0.2  # seconds the page stays away


@pytest.fixture
def page(game, monkeypatch):
    """stands in for the page's window.madlove_page"""
    page = SimpleNamespace(active=True)
    game.page = page
    monkeypatch.setattr(game_module, 'PAUSED_POLL', 0.01)
    return page


@pytest.fixture
def steps(game, monkeypatch):
    """counts the game's frames"""
    steps = []
    step = game.step
    monkeypatch.setattr(game, 'step', lambda: steps.append(game.scenes.scene) or step())
    return steps


@pytest.fixture
def sound(monkeypatch):
    calls = []
    monkeypatch.setattr(audio, 'pause_all', lambda: calls.append('pause'))
    monkeypatch.setattr(audio, 'unpause_all', lambda: calls.append('unpause'))
    return calls


async def frames(count):
    for _ in range(count):
        await asyncio.sleep(0)


def run(game, script):
    """runs the game alongside the script, then quits it"""

    async def main():
        task = asyncio.create_task(game.run())
        await frames(3)
        await script()
        pg.event.post(pg.event.Event(pg.QUIT))
        await task

    asyncio.run(main())


def go_away(page, steps, before=None):
    """the script: the page goes away for a while and comes back. it notes the frames run while away"""

    async def script():
        if before:
            before()
            await frames(3)
        page.active = False
        await frames(3)
        script.steps_when_gone = len(steps)
        await asyncio.sleep(AWAY)
        script.steps_while_away = len(steps) - script.steps_when_gone
        page.active = True
        await frames(3)

    return script


def test_stops_while_away(game, page, steps, sound):
    script = go_away(page, steps)
    run(game, script)
    assert script.steps_while_away == 0
    assert sound == ['pause', 'unpause']
    assert len(steps) > script.steps_when_gone  # and runs again after


def test_level_comes_back_in_the_smoke_break(game, page, steps, sound):
    level = {}

    def start_level():
        level['scene'] = play.GameScene(game, 1)
        game.scenes.go_to(level['scene'])

    run(game, go_away(page, steps, start_level))
    scene = game.scenes.scene
    assert isinstance(scene, menu.OverlayMenuScene)
    assert scene.menu_type == 'pause'
    assert scene.paused_scene is level['scene']


def test_title_stays(game, page, steps, sound):
    run(game, go_away(page, steps))
    assert isinstance(game.scenes.scene, title.TitleScene)


def test_time_away_does_not_count(game, page, steps, sound):
    run(game, go_away(page, steps))
    assert game.dt < AWAY * 1000 / 2


def test_always_active_outside_the_browser(game):
    assert game.page is None
    assert game.active()
