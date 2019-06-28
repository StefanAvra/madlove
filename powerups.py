import pygame as pg
import os
import config


class PowerUp(pg.sprite.Sprite):
    def __init__(self, pu_type, pos, cigs=1):
        super(PowerUp, self).__init__()
        self.type = pu_type
        self.image = get_pu_image(pu_type)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = 3
        self.cigs = cigs if pu_type == 'pack' else None

    def update(self, player_rect):
        self.rect.y -= self.speed
        if self.rect.top > config.HEIGHT():
            self.kill()

        if pg.sprite.collide_rect(self.rect, player_rect):
            self.kill()
            pu_event = pg.event.Event(pg.USEREVENT, powerup=self.type, cigs=self.cigs)
            pg.event.post(pu_event)


def get_pu_image(pu_type):
    if pu_type == 'pack':
        file = 'pack'
    else:
        file = 'pack'

    return pg.image.load(os.path.join('assets', 'graphics', '{}.png').format(file)).convert()


