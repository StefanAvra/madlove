"""The bricks that make up the lungs."""

import pygame as pg

from madlove import config


class Brick(pg.sprite.Sprite):
    def __init__(self, x=0, y=0, health=2, brick_type='b'):
        types = {'r': 'red', 'w': 'white', 'b': 'black'}
        super().__init__()
        self.image = pg.image.load(config.asset('graphics', f'brick_{types[brick_type]}.png')).convert()
        self.dark = pg.image.load(config.asset('graphics', 'brick_{}.png'.format(types['b']))).convert()
        self.max_health = health
        self.health = health
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        darken_factor = 255
        self.dark.set_alpha(darken_factor)

        self.image.blit(self.dark, (0, 0))
