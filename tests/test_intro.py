"""The level intro's screen: the photo on black above the pack's logo, made from the other graphics."""

import pygame as pg
import pytest

from madlove import config
from madlove import game as game_module
from madlove.scenes import intro


@pytest.mark.parametrize('number', range(1, game_module.INTRO_IMAGES + 1))
def test_intro_image(game, number):  # noqa: ARG001 - the game opens the display
    image = intro.intro_image(number)
    assert image.get_size() == config.DISPLAY
    assert image.get_at((240, 100)) == pg.Color(0, 0, 0)  # behind the fact's text
    photo = pg.image.load(config.asset('graphics', f'level_intro_{number}.png'))
    x, y = intro.PHOTO_POS
    assert image.get_at((x + 100, y + 100)) == photo.get_at((100, 100))
    assert image.get_at((240, intro.LOGO_TOP + 2)) == config.BG_COLOR  # the same pink as everywhere
