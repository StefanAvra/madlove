"""Bullets from the shooting power-up."""

import pygame as pg

from madlove import audio
from madlove.sprites.powerup import PowerUp


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((6, 10))
        self.image.fill((255, 255, 255))
        core = pg.Surface((4, 10))
        core.fill((0, 0, 0))
        self.image.blit(core, (1, 0))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = 6
        audio.play_sfx('bullet')

    def update(self, bricks, game_scene):
        # todo: refactor - should be global function
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()
        collided_brick = pg.sprite.spritecollideany(self, bricks)
        if collided_brick:
            collided_brick.health -= 1
            collided_brick.update()
            game_scene.game.score += game_scene.game.combo.points()
            game_scene.game.combo.hit()
            if collided_brick.health <= 0:
                collided_brick.kill()
                game_scene.game.score += game_scene.game.combo.points('killed_brick')
                try:
                    if len(game_scene.powerups) < 3:
                        new_powerup = game_scene.pu_queue.pop(game_scene.total_bricks - len(game_scene.bricks))
                        game_scene.powerups.add(PowerUp(new_powerup, pos=collided_brick.rect.center))
                        print(f'added {new_powerup}')
                except KeyError:
                    pass
            self.kill()
            audio.play_sfx('hit_brick')
