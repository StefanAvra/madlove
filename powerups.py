import pygame as pg
import os
import config


class PowerUp(pg.sprite.Sprite):
    def __init__(self, pu, pos):
        super(PowerUp, self).__init__()
        self.type = pu['pu_type']
        self.image = get_pu_image(self.type)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = 2
        self.amount = pu['amount'] if 'amount' in pu else None
        self.timer = pu['timer'] if 'timer' in pu else None

    def update(self, player, collect_all_pus):
        self.rect.y += self.speed
        if self.rect.top > config.HEIGHT:
            self.kill()
            if self.type not in ['shorter']:
                collect_all_pus = False

        if pg.sprite.collide_rect(self, player):
            self.kill()
            pu_event = pg.event.Event(pg.USEREVENT, powerup=self.type, amount=self.amount, timer=self.timer)
            pg.event.post(pu_event)


def get_pu_image(pu_type):
    if pu_type == 'pack':
        file = 'pack'
    else:
        file = 'pack'

    return pg.image.load(os.path.join('assets', 'graphics', '{}.png').format(file)).convert()


