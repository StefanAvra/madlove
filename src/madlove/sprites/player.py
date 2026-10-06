"""The paddle, a cigarette."""

import pygame as pg

from madlove import config


class Player(pg.sprite.Sprite):
    def __init__(self, x=200, p_type='m', speed=7):
        super().__init__()
        self.type = p_type
        self.speed = speed
        self.image = pg.image.load(config.asset('graphics', f'paddle_{self.type}.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = config.PLAYER_Y
        self.max_x = pg.display.get_surface().get_width()
        self.lengths = ['s', 'm', 'l', 'xl']

    def update(self, left, right, up):
        if up:
            pass
        if left:
            self.rect.x -= self.speed
            if self.rect.x < 0:
                self.rect.x = 0
        if right:
            self.rect.x += self.speed
            if self.rect.x + self.rect.width > self.max_x:
                self.rect.x = self.max_x - self.rect.width

    def update_length(self, p_type):
        self.type = p_type
        temp_rect = self.rect
        self.image = pg.image.load(config.asset('graphics', f'paddle_{self.type}.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = temp_rect.centerx
        self.rect.y = config.PLAYER_Y

    def longer(self):
        current_length = self.lengths.index(self.type)
        if current_length < len(self.lengths) - 1:
            self.update_length(self.lengths[current_length + 1])

    def shorter(self):
        current_length = self.lengths.index(self.type)
        if current_length > 0:
            self.update_length(self.lengths[current_length - 1])
