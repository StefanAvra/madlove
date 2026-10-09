"""The game moves in steps of 1/60 s, so it plays the same at any frame rate: a slower screen runs more
steps per picture, up to three."""

import random

import pytest

from madlove import game as game_module
from madlove.game import MAX_STEPS, STEP_MS
from madlove.scenes import play


def pictures(game, times):
    """the steps and dt of each picture, for pictures that come these milliseconds apart"""
    return [game.catch_up(elapsed) for elapsed in times]


def test_one_step_per_picture_at_60_fps(game):
    for steps, dt in pictures(game, [16, 17, 17] * 20):  # what pg.time.Clock.tick(60) returns
        assert steps == 1
        assert dt in (16, 17)


def test_two_steps_per_picture_at_30_fps(game):
    for steps, dt in pictures(game, [33, 34, 33] * 10):
        assert steps == 2
        assert dt == pytest.approx(STEP_MS, abs=0.5)


@pytest.mark.parametrize('elapsed', [22, 25, 40, 45])
def test_sixty_steps_a_second_at_any_frame_rate(game, elapsed):
    done = pictures(game, [elapsed] * (6000 // elapsed))
    assert sum(steps for steps, _ in done) == pytest.approx(360, abs=1)
    assert sum(steps * dt for steps, dt in done) == pytest.approx(6000, abs=elapsed)


def test_a_slow_device_slows_the_game_down(game):
    for steps, dt in pictures(game, [100] * 5):
        assert steps == MAX_STEPS
        assert dt == pytest.approx(STEP_MS)
    assert game.catch_up(17) == (1, 17)  # nothing left to catch up on


class Clock:
    """stands in for pg.time.Clock: the pictures come elapsed milliseconds apart"""

    def __init__(self, elapsed):
        self.elapsed = elapsed

    def tick(self, framerate=0):
        return self.elapsed

    def get_fps(self):
        return 1000 / self.elapsed


def play_level(game, elapsed, seconds):
    """plays the first level for a while with the ball launched and the paddle still, then returns the
    balls' positions, the bricks left and the score"""
    random.seed(2019)
    game.score = 0
    game.clock = Clock(elapsed)
    game.scenes = game_module.SceneManager(game)
    scene = play.GameScene(game, 1)
    game.scenes.go_to(scene)
    for ball in scene.balls:
        ball.sticky = False
    for _ in range(round(seconds * 1000 / elapsed)):
        game.step()
    assert game.scenes.scene is scene
    return [(ball.x, ball.y) for ball in scene.balls], len(scene.bricks), game.score


def test_the_ball_hits_the_same_bricks_at_30_fps(game):
    at_60 = play_level(game, STEP_MS, 3)
    at_30 = play_level(game, 2 * STEP_MS, 3)
    assert at_30 == at_60
    assert at_60[1] < play.GameScene(game, 1).total_bricks  # it did hit some


def test_fades_take_as_many_steps_at_30_fps(game):
    for elapsed, pictures_needed in [(STEP_MS, 26), (2 * STEP_MS, 13)]:
        game.clock = Clock(elapsed)
        game.scenes = game_module.SceneManager(game)
        scene = play.GameScene(game, 1)
        game.scenes.go_to(scene)
        for _ in range(pictures_needed):
            game.step()
        assert scene.fadein_step <= 0
