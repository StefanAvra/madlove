import pygame as pg
import pytest

from madlove import audio
from madlove import game as game_module
from madlove.__main__ import parse_args, settings_from_args
from madlove.scenes import credits, highscores, play, title


def press(scene, key):
    scene.handle_events([pg.event.Event(pg.KEYDOWN, key=key, mod=0, unicode='', scancode=0)])


@pytest.mark.parametrize('debug', [False, True])
def test_game_keys_need_debug(game, debug):
    game.settings.debug = debug
    scene = play.GameScene(game, 1)
    balls = len(scene.balls)
    music = audio.music_busy()
    press(scene, pg.K_b)
    press(scene, pg.K_COMMA)
    press(scene, pg.K_f)
    press(scene, pg.K_n)
    press(scene, pg.K_m)
    assert (len(scene.balls) == balls + 1) == debug
    assert (audio.music_busy() != music) == debug
    assert game.settings.bot == debug
    assert game.settings.show_fps == debug
    assert (len(scene.bricks) == 0) == debug


@pytest.mark.parametrize('key, scene_class', [(pg.K_c, credits.CreditsScene), (pg.K_h, highscores.HighscoreScene)])
@pytest.mark.parametrize('debug', [False, True])
def test_title_keys_need_debug(game, debug, key, scene_class):
    game.settings.debug = debug
    game.scenes = game_module.SceneManager(game)
    press(game.scenes.scene, key)
    expected = scene_class if debug else title.TitleScene
    assert isinstance(game.scenes.scene, expected)


def test_debug_flag():
    assert not settings_from_args(parse_args([])).debug
    assert settings_from_args(parse_args(['--debug'])).debug
