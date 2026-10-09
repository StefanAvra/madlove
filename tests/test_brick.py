"""The bricks share their images, and a hit brick turns black."""

import pygame as pg

from madlove.sprites import brick
from madlove.sprites.brick import Brick


def test_bricks_of_a_color_share_one_image(game, monkeypatch):  # noqa: ARG001 - the game opens the display
    brick.brick_image.cache_clear()
    loads = []
    load = pg.image.load
    monkeypatch.setattr(pg.image, 'load', lambda *args: loads.append(args) or load(*args))
    bricks = [Brick(brick_type='r') for _ in range(50)] + [Brick(brick_type='w') for _ in range(50)]
    assert len(loads) == 2
    assert bricks[0].image is bricks[49].image
    assert bricks[0].image is not bricks[50].image


def test_a_hit_brick_turns_black_alone(game):  # noqa: ARG001
    hit, other = Brick(brick_type='r'), Brick(brick_type='r')
    red = other.image.get_at((5, 3))
    hit.update()
    assert hit.image is brick.brick_image('black')
    assert other.image.get_at((5, 3)) == red
