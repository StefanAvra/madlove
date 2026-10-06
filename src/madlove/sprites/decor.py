"""Sprites for the title screen and the smoke break."""

import pygame as pg

from madlove import audio, config


class Arrow(pg.sprite.Sprite):
    def __init__(self, second=False):
        super().__init__()
        self.image = pg.image.load(config.asset('graphics', 'arrow.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centery = 0 - self.rect.height
        self.done = False
        self.second_run = second
        self.active = False

    def update(self, *args):
        if self.rect.top < (80 if self.second_run else 640):
            self.rect.centery += 18
        else:
            self.done = True


class Title(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load(config.asset('graphics', 'title.png')).convert_alpha()
        self.image_clean = pg.image.load(config.asset('graphics', 'title.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (240, 220)
        self.animate = False
        self.shine = pg.Surface((20, self.rect.height))
        self.shine.fill((255, 255, 255))
        self.shine_pos = -20
        self.shine_timer = 0

    def update(self, dt):
        if not self.shine_timer == 0:
            self.shine_timer -= dt
            if self.shine_timer < 0:
                self.shine_timer = 0
        else:
            if self.animate:
                if self.shine_pos == 0:
                    audio.play_sfx('intro2')
                if self.shine_pos > self.rect.width:
                    self.animate = False
                self.image.blit(self.image_clean, (0, 0))
                self.image.blit(self.shine, (self.shine_pos, 0), special_flags=pg.BLEND_ADD)
                self.shine_pos += 20

    def restart_animation(self, timer=0):
        self.shine_timer = timer
        self.animate = True
        self.shine_pos = -20


class Ashtray(pg.sprite.Sprite):
    # 208 x 162
    def __init__(self):
        super().__init__()
        self.images = []
        self.sheet = SpriteSheet('ashtray', (208, 162), 14, True)
        for sprite in self.sheet.sprites:
            self.images.append(sprite)
        self.img_idx = 0
        self.image = self.images[self.img_idx]

    def update(self):
        if self.img_idx < len(self.images) - 1:
            self.img_idx += 1
        else:
            self.img_idx = 0
        self.image = self.images[self.img_idx]


class SpriteSheet:
    def __init__(self, filename, size, image_count, alpha=False):
        if alpha:
            self.sheet = pg.image.load(config.asset('graphics', f'{filename}.png')).convert_alpha()
        else:
            self.sheet = pg.image.load(config.asset('graphics', f'{filename}.png')).convert()
        self.sprites = []
        for x in range(image_count):
            self.sprites.append(self.load_image(size, (size[0] * x, 0)))

    def load_image(self, size, pos):
        image = pg.Surface(size).convert_alpha()
        image.fill(config.BG_COLOR)
        rect = image.get_rect()
        rect.x = pos[0]
        rect.y = pos[1]
        image.blit(self.sheet, (0, 0), rect)
        return image
