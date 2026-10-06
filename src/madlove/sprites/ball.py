"""The ball."""

import collections
import random

import pygame as pg

from madlove import audio, config, utils
from madlove.sprites.powerup import PowerUp


class Ball(pg.sprite.Sprite):
    def __init__(self, pos_x=240, pos_y=550, velocity=None, size=7, sticky=True):
        super().__init__()
        if velocity is None:
            velocity = (random.randint(-3, 3), -3)
        self.velocity = velocity
        self.x = pos_x
        self.y = pos_y
        self.size = size
        self.color = config.BALL_COLOR
        self.image = pg.Surface((self.size,) * 2)
        self.image.fill(config.BG_COLOR)
        self.image.set_colorkey(config.BG_COLOR)
        pg.draw.circle(self.image, self.color, (int(self.size / 2),) * 2, int(self.size / 2))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.collisions = [False] * 8
        self.last_bounces = collections.deque([], 18)
        self.last_bounce_times = collections.deque([], 3)
        self.tail = collections.deque([], 10)
        self.sticky = sticky
        self.hot = False
        self.hot_timer = 0
        self.hot_blink = 0

    def check_collision(self, rect):
        # intended to be called only after collision detected!
        self.collisions[0] = rect.collidepoint(self.rect.midtop)
        self.collisions[1] = rect.collidepoint(self.rect.topright)
        self.collisions[2] = rect.collidepoint(self.rect.midright)
        self.collisions[3] = rect.collidepoint(self.rect.bottomright)
        self.collisions[4] = rect.collidepoint(self.rect.midbottom)
        self.collisions[5] = rect.collidepoint(self.rect.bottomleft)
        self.collisions[6] = rect.collidepoint(self.rect.midleft)
        self.collisions[7] = rect.collidepoint(self.rect.topleft)

    def hit_paddle(self, paddle_rect):
        x_hit = paddle_rect.center[0]
        audio.play_sfx('hit_wall')
        # self.velocity = ((self.rect.center[0] - x_hit) * 0.09 + self.velocity[0], -abs(self.velocity[1]))
        self.velocity = (round((self.rect.centerx - x_hit) / 5), -abs(self.velocity[1]))
        self.rect.bottom = paddle_rect.y - 1

    def hit_wall(self, left_right):
        audio.play_sfx('hit_wall')
        if left_right == 0:
            self.bounce(6)
            self.rect.left = 1
        else:
            self.bounce(2)
            self.rect.right = pg.display.get_surface().get_width() - 1

    def hit_top(self):
        audio.play_sfx('hit_wall')
        self.bounce(0)
        self.rect.top = 1

    def bounce(self, direction):
        """direction can be 0 to 7, referring to the direction BEFORE bouncing, starting north going clockwise."""
        if direction == 0:
            self.velocity = (self.velocity[0], abs(self.velocity[1]))
        elif direction == 4:
            self.velocity = (self.velocity[0], -abs(self.velocity[1]))
        elif direction == 2:
            self.velocity = (-abs(self.velocity[0]), self.velocity[1])
        elif direction == 6:
            self.velocity = (abs(self.velocity[0]), self.velocity[1])
        elif direction == 1:
            self.velocity = (-abs(self.velocity[0]), abs(self.velocity[1]))
        elif direction == 3:
            self.velocity = (-abs(self.velocity[0]), -abs(self.velocity[1]))
        elif direction == 5:
            self.velocity = (abs(self.velocity[0]), -abs(self.velocity[1]))
        elif direction == 7:
            self.velocity = (abs(self.velocity[0]), abs(self.velocity[1]))

        self.update_bounces()

    def update_bounces(self):
        self.last_bounces.append(self.rect.center)
        if collections.Counter(self.last_bounces).most_common(1)[0][1] >= 6:
            self.last_bounces.clear()
            print('giving that ball a spin...')
            self.velocity = (random.randint(-4, 4), self.velocity[1])

    def hit_brick(self, brick, game_scene):
        self.check_collision(brick.rect)
        if not self.hot:
            if True in self.collisions[::2]:
                self.bounce(self.collisions[::2].index(True) * 2)
            else:
                self.bounce(self.collisions.index(True))
            brick.health -= 1
        else:
            brick.health -= 2
            game_scene.game.score += game_scene.game.combo.points()
        brick.update()
        game_scene.game.score += game_scene.game.combo.points()
        game_scene.game.combo.hit()
        if brick.health <= 0:
            brick.kill()
            game_scene.game.score += game_scene.game.combo.points('killed_brick')
            try:
                if len(game_scene.powerups) < 3:
                    new_powerup = game_scene.pu_queue.pop(game_scene.total_bricks - len(game_scene.bricks))
                    game_scene.powerups.add(PowerUp(new_powerup, pos=brick.rect.center))
                    print(f'added {new_powerup}')
            except KeyError:
                pass
        audio.play_sfx('hit_brick')

    def update(self, player, bricks, bombs, game_scene):
        if self.hot_timer > 0:
            self.hot = True
            self.hot_timer -= game_scene.game.dt
            self.hot_blink += game_scene.game.dt
            if self.hot_blink > 100:
                self.hot_blink = 0
                self.color = utils.invert_color(self.color)
            if self.hot_timer < 0:
                self.hot_timer = 0
                self.hot = False
        else:
            self.color = config.BALL_COLOR
        pg.draw.circle(self.image, self.color, (int(self.size / 2),) * 2, int(self.size / 2))
        if self.sticky:
            self.rect.x = player.rect.centerx
            self.rect.bottom = player.rect.top
            self.x = self.rect.x
            self.y = self.rect.y
            return
        self.tail.append((self.rect.centerx, self.rect.centery))
        # x and y are used for storing floats so finer movement is possible
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if self.rect.left <= 0:
            self.hit_wall(0)
        elif self.rect.right >= pg.display.get_surface().get_width():
            self.hit_wall(1)
        if self.rect.top < 0:
            self.hit_top()
        if self.rect.y > pg.display.get_surface().get_height():
            self.kill()
        if pg.sprite.collide_rect(self, player):
            self.hit_paddle(player.rect)
        collided_brick = pg.sprite.spritecollideany(self, bricks)

        if collided_brick:
            self.hit_brick(collided_brick, game_scene)

    def speed_up(self, factor=1.1):
        self.velocity = (self.velocity[0] * factor, self.velocity[1] * factor)
