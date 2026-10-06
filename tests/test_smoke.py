"""Runs the whole game headless and checks that nothing crashes.

Both runs are scripted and deterministic, so they also record a trace: every scene change, with the frame
number and the score at that moment. The trace must match the one saved in tests/golden, which catches
any change in gameplay. After an intended change, regenerate it with
`MADLOVE_UPDATE_GOLDEN=1 uv run pytest tests/test_smoke.py` and explain why in the commit message.
"""

import json
import os
import pathlib
import random

import pygame as pg
import pytest

import config

FRAME_MS = 1000 // config.FRAMERATE
PRESS_EVERY = 30  # frames between presses of Space or Enter, to get through the menus
GOLDEN_DIR = pathlib.Path(__file__).parent / 'golden'


class FakeClock:
    """replaces pg.time.Clock: returns a fixed frame time without waiting, presses keys and quits"""

    frames = 0  # quits after this many frames
    current = None  # the clock of the running game

    def __init__(self):
        self.frame = 0
        FakeClock.current = self

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
def trace(game, scores, coins, monkeypatch):
    """records [frame, scene, score] for every scene change"""
    import string_resource

    # the facts and level intros are shuffled or counted at import; pin them so the runs repeat exactly
    monkeypatch.setattr(string_resource, 'fact_order', list(range(len(string_resource.fact_order))))
    monkeypatch.setattr(string_resource, 'current_fact', 0)
    monkeypatch.setattr(game, 'current_intro', 1)
    monkeypatch.setattr(scores, 'highscores', list(scores.DEFAULT_HIGHSCORES))

    changes = []
    go_to = game.SceneManager.go_to

    def record(manager, scene):
        frame = FakeClock.current.frame if FakeClock.current else 0
        changes.append([frame, type(scene).__name__, game.score])
        go_to(manager, scene)

    monkeypatch.setattr(game.SceneManager, 'go_to', record)
    return changes


def run_game(game, monkeypatch, frames, bot):
    monkeypatch.setattr(config, 'ENABLE_BOT', bot)
    monkeypatch.setattr(config, 'FREE_MODE', True)
    monkeypatch.setattr(FakeClock, 'frames', frames)
    monkeypatch.setattr(FakeClock, 'current', None)
    monkeypatch.setattr(pg.time, 'Clock', FakeClock)
    monkeypatch.setattr(game, 'score', 0)
    random.seed(2019)
    game.main()  # returns when it gets the QUIT event


def check_golden(name, trace):
    path = GOLDEN_DIR / f'{name}.json'
    if os.environ.get('MADLOVE_UPDATE_GOLDEN'):
        path.parent.mkdir(exist_ok=True)
        path.write_text('[\n' + ',\n'.join(json.dumps(change) for change in trace) + '\n]\n')
    assert trace == json.loads(path.read_text()), f'the game played differently than {path}'


def visited(trace):
    return {scene for _, scene, _ in trace}


def test_bot_plays_without_crashing(game, trace, monkeypatch):
    run_game(game, monkeypatch, frames=5000, bot=True)
    assert 'GameScene' in visited(trace)
    assert game.score > 0
    check_golden('bot', trace + [[FakeClock.current.frame, 'end', game.score]])


def test_full_game_cycle_without_crashing(game, trace, monkeypatch):
    # nobody moves the paddle, so every life is lost quickly and the game goes through
    # continue, game over, name entry, high scores and credits, back to the title screen
    run_game(game, monkeypatch, frames=4000, bot=False)
    for scene in ('IntroScene', 'GameScene', 'LostLifeScene', 'ContinueScene', 'GameOver', 'HighscoreScene'):
        assert scene in visited(trace), f'{scene} was never reached: {visited(trace)}'
    assert [scene for _, scene, _ in trace].count('TitleScene') >= 2, 'never got back to the title screen'
    check_golden('idle', trace + [[FakeClock.current.frame, 'end', game.score]])
