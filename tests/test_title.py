import pygame as pg
import pytest

from madlove import game as game_module
from madlove.scenes import menu, title


def press(scene, key):
    scene.handle_events([pg.event.Event(pg.KEYDOWN, key=key, mod=0, unicode='', scancode=0)])


@pytest.mark.parametrize('can_quit', [True, False])
def test_escape_opens_the_exit_menu_only_when_the_game_can_quit(game, can_quit):
    game.settings.can_quit = can_quit
    game.scenes = game_module.SceneManager(game)
    press(game.scenes.scene, pg.K_ESCAPE)
    if can_quit:
        assert isinstance(game.scenes.scene, menu.OverlayMenuScene)
    else:
        assert isinstance(game.scenes.scene, title.TitleScene)
