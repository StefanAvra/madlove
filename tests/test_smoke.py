"""Runs the whole game headless, with the bot playing, and checks that nothing crashes."""

import collections
import random

import pygame as pg
import pytest

import config

FRAME_MS = 1000 // config.FRAMERATE
PRESS_EVERY = 30  # frames between presses of Space or Enter, to get through the menus


class FakeClock:
    """replaces pg.time.Clock: returns a fixed frame time without waiting, presses keys and quits"""

    frames = 0  # quits after this many frames

    def __init__(self):
        self.frame = 0

    def tick(self, framerate=0):
        self.frame += 1
        if self.frame % PRESS_EVERY == 0:
            key = pg.K_RETURN if self.frame % (2 * PRESS_EVERY) == 0 else pg.K_SPACE
            for event_type in (pg.KEYDOWN, pg.KEYUP):
                pg.event.post(pg.event.Event(event_type, key=key, mod=0, unicode='', scancode=0))
        if self.frame >= self.frames:
            pg.event.post(pg.event.Event(pg.QUIT))
        return FRAME_MS

    def get_fps(self):
        return float(config.FRAMERATE)


@pytest.fixture
def visited_scenes(game, monkeypatch):
    visited = collections.Counter()
    go_to = game.SceneManager.go_to

    def record(manager, scene):
        visited[type(scene).__name__] += 1
        go_to(manager, scene)

    monkeypatch.setattr(game.SceneManager, 'go_to', record)
    return visited


def run_game(game, monkeypatch, frames, bot):
    random.seed(2019)
    monkeypatch.setattr(config, 'ENABLE_BOT', bot)
    monkeypatch.setattr(config, 'FREE_MODE', True)
    monkeypatch.setattr(FakeClock, 'frames', frames)
    monkeypatch.setattr(pg.time, 'Clock', FakeClock)
    monkeypatch.setattr(game, 'score', 0)
    game.main()  # returns when it gets the QUIT event


def test_bot_plays_without_crashing(game, visited_scenes, monkeypatch):
    run_game(game, monkeypatch, frames=5000, bot=True)
    assert visited_scenes['GameScene']
    assert game.score > 0


def test_full_game_cycle_without_crashing(game, visited_scenes, monkeypatch):
    # nobody moves the paddle, so every life is lost quickly and the game goes through
    # continue, game over, name entry, high scores and credits, back to the title screen
    run_game(game, monkeypatch, frames=4000, bot=False)
    for scene in ('IntroScene', 'GameScene', 'LostLifeScene', 'ContinueScene', 'GameOver', 'HighscoreScene'):
        assert visited_scenes[scene], f'{scene} was never reached: {dict(visited_scenes)}'
    assert visited_scenes['TitleScene'] >= 2, 'never got back to the title screen'
