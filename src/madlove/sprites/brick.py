"""The bricks that make up the lungs."""

import functools

import pygame as pg

from madlove import config

COLORS = {'r': 'red', 'w': 'white', 'b': 'black'}  # the level maps' letters


@functools.cache
def brick_image(color):
    """the image of a brick, loaded once and shared by all bricks of that color: don't draw on it"""
    return pg.image.load(config.asset('graphics', f'brick_{color}.png')).convert()


class Brick(pg.sprite.Sprite):
    def __init__(self, x=0, y=0, health=2, brick_type='b'):
        super().__init__()
        self.image = brick_image(COLORS[brick_type])
        self.max_health = health
        self.health = health
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        """a hit brick turns black"""
        self.image = brick_image('black')
