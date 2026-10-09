"""Playing a level."""

import random

import pygame as pg

from madlove import audio, config, hud, levels, utils
from madlove import controls as ctrls
from madlove import strings as str_r
from madlove.scenes import base, level_end, lives, menu
from madlove.sprites.ball import Ball
from madlove.sprites.brick import Brick
from madlove.sprites.bullet import Bullet
from madlove.sprites.player import Player

stages = [
    'HEALTHY',
    'IA1',
    'IA2',
    'IA3',
    'IB',
    'IIA',
    'IIB',
    'IIIA',
    'IIIB',
    'IIIC',
    'IVA',
    'IVA',
    'IVB',
    'IVB',
    'IVB',
    'IVB',
]


class GameScene(base.Scene):
    def __init__(self, game, level_no):
        super().__init__(game)
        self.bg = pg.Surface((32, 32))
        self.bg.convert()
        self.bg.fill(config.BG_COLOR)
        self.current_stage = 0
        self.player = Player()
        self.balls = pg.sprite.Group()
        self.bricks = pg.sprite.Group()
        self.bombs = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.level_data = levels.Level(level_no)
        self.notif_stack = []
        self.notification = None
        self.timer = 0
        self.hud_highlight_clock = 0
        self.hud_highlight_combo = 0
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave_to = False
        self.draw_credit = False
        self.credit_text = str_r.get_str('credit')
        self.credit = self.game.wallet.credit
        self.credit_text_timer = 0
        self.heartattack_mode = None
        self.heart_fade = 0
        self.heart_color = pg.Color(255, 255, 255, 0)
        self.heart_fade_inv = 1
        self.heart_beat = 0
        self.killing_timer = 0
        self.pu_queue = self.level_data.powerups.copy()
        self.shooting_period = 0
        self.shooting_active = False
        self.shooting_timer = 0
        self.bonus_timer = self.level_data.bonus_time * 1000
        self.collected_all_pus = True
        self.no_continue = True
        self.lost_life = False
        self.game.combo.reset()

        tile_offset_y = 10
        for line in self.level_data.bricks:
            tile_offset_x = 2
            for tile in line:
                if tile in 'bwr':
                    brick = Brick(tile_offset_x, tile_offset_y, brick_type=tile)
                    self.bricks.add(brick)
                tile_offset_x += levels.TILE[0] + levels.TILE_PADDING
            tile_offset_y += levels.TILE[1] + levels.TILE_PADDING
        self.total_bricks = len(self.bricks)
        self.all_sprites = pg.sprite.Group()
        self.all_sprites.add(self.player, self.balls, self.bricks, self.bombs)
        audio.load_music('bgm')
        audio.set_music_volume(0.8)
        self.reset_round()

    def render(self, screen):
        screen.fill(config.BG_COLOR)

        if self.heartattack_mode is not None:
            render_heartattack(self, screen)

        hud.render_hud(
            self.game,
            screen,
            str(self.game.score),
            stages[self.current_stage],
            str(self.game.wallet.lives),
            self.timer,
            self.hud_highlight_combo,
        )

        if self.notification is not None:
            text = hud.text(self.game.font_16, self.notification.msg, self.notification.color)
            pos = text.get_rect()
            pos.center = (screen.get_width() / 2, 550)
            screen.blit(text, pos)

        self.all_sprites.draw(screen)

        if self.game.settings.show_velocity:
            # first ball only
            velocity = self.balls.sprites()[0].velocity
            velocity = self.game.font_8.render(
                str((round(velocity[0], 2), round(velocity[1], 2))), True, config.DEBUG_COLOR
            )
            screen.blit(velocity, (40, 0))

        # if self.draw_credit:
        #     hud.render_credit(self, screen)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1)

    def update(self):
        self.timer += self.game.dt
        self.bonus_timer -= self.game.dt

        up, left, right, down = [ctrls.get_buttons()[key] for key in (ctrls.UP, ctrls.LEFT, ctrls.RIGHT, ctrls.DOWN)]

        if self.game.settings.bot:
            left, right = self.game.bot.play(self.player, self.balls)
        if not self.heartattack_mode == 'killing':
            for ball in self.balls:
                ball.update(self.player, self.bricks, self.bombs, self)
            self.player.update(left, right, up)
            self.powerups.update(self.player, self)

        else:
            self.killing_timer += self.game.dt
            if self.killing_timer >= 3000 and not self.fade_leave_to:
                self.fadeout_step = 255
                self.fade_leave_to = 'finished'

        if self.fade_leave_to == 'finished' and self.fadeout_step <= 0:
            self.manager.go_to(level_end.FinishedLevelScene(self.game, self))

        if not self.balls.has(self.balls):
            self.manager.go_to(lives.LostLifeScene(self.game, self))
        if not self.bricks.has(self.bricks) and not self.fade_leave_to:
            self.fadeout_step = 255
            self.fade_leave_to = 'finished'

        self.all_sprites.add(self.powerups)

        if self.shooting_active:
            self.shooting_period -= self.game.dt
            self.shooting_timer += self.game.dt
            if self.shooting_period < 0:
                self.shooting_active = False
                self.shooting_period = 0
            if self.shooting_timer >= 130:
                self.shooting_timer = 0
                bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                self.bullets.add(bullet)
                self.all_sprites.add(self.bullets)
        self.bullets.update(self.bricks, self)

        past_stage = self.current_stage
        self.current_stage = int(utils.interp(len(self.bricks), [0, self.total_bricks], [len(stages) - 1, 0]))
        if stages[past_stage] != stages[self.current_stage]:
            if stages[past_stage] == stages[0]:
                self.notif_stack.append(Message("got cancer!", 'cancer'))
                print(f'{len(self.bricks)} left')

        if self.total_bricks * 0.1 >= len(self.bricks):
            if self.heartattack_mode is None:
                pu_event = pg.event.Event(pg.USEREVENT, powerup='heartattack')
                pg.event.post(pu_event)

        if len(self.notif_stack) > 0 and self.notification is None:
            self.notification = self.notif_stack.pop(0)
            if self.notification.std_sfx == 'normal':
                audio.play_sfx('message')
            elif self.notification.std_sfx == 'cancer':
                audio.play_sfx('cancer')

        if self.notification is not None:
            if self.notification.timer <= 0:
                self.notification = None
            else:
                self.notification.update(self.game.dt)

        self.game.combo.update(self.game.dt)

        if self.game.combo.is_combo():
            new_combo = self.game.combo.new_combo()
            if new_combo in [25, 50, 100]:
                self.notif_stack.append(Message(str_r.get_combo_msg(new_combo)))

            self.hud_highlight_clock += self.game.dt
            if self.hud_highlight_clock >= 50:
                self.hud_highlight_clock = 0
                self.hud_highlight_combo += 1  # 1 for black, 2 for white combo text
                if self.hud_highlight_combo > 2:
                    self.hud_highlight_combo = 1
        else:
            self.hud_highlight_combo = 0

        if self.credit < self.game.wallet.credit:
            self.credit = self.game.wallet.credit
            self.notif_stack.append(Message(self.credit_text.format(self.game.wallet.credit), sfx=False))

        if self.draw_credit:
            self.credit_text_timer += self.game.dt
            if self.credit_text_timer >= 2000:
                self.draw_credit = False
                self.credit_text_timer = 0

    def reset_round(self):
        audio.play_music(-1)

        self.balls.add(Ball(velocity=(random.randint(-2, 2), -3)))
        self.all_sprites.add(self.balls)
        self.player.rect.centerx = pg.display.get_surface().get_rect().centerx

    def spread_metastasis(self, amount=1):
        try:
            new_ball_pos = self.balls.sprites()[0].rect
        except IndexError:
            new_ball_pos = (random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT * 0.5))
        for _ in range(amount):
            self.balls.add(
                Ball(velocity=(random.randint(-3, 3), -3), pos_x=new_ball_pos[0], pos_y=new_ball_pos[1], sticky=False)
            )
            self.all_sprites.add(self.balls)
            print(new_ball_pos)

    def handle_debug_key(self, key):
        """the keys for testing, which only work with --debug"""
        if key == pg.K_o:
            for ball in self.balls:
                ball.speed_up(0.9)
        if key == pg.K_p:
            for ball in self.balls:
                ball.speed_up(1.1)
        if key == pg.K_b:
            self.balls.add(Ball())
            self.all_sprites.add(self.balls)
        if key == pg.K_COMMA:
            self.game.settings.bot = not self.game.settings.bot
        if key == pg.K_f:
            self.game.settings.show_fps = not self.game.settings.show_fps
            self.game.settings.show_velocity = not self.game.settings.show_velocity
        if key == pg.K_n:
            self.bricks.empty()
        if key == pg.K_h:
            pu_event = pg.event.Event(pg.USEREVENT, powerup='shoot', timer=5000)
            pg.event.post(pu_event)
        if key == pg.K_m:
            if audio.music_busy():
                audio.stop_music()
            else:
                audio.play_music(-1)

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button == 0:
                    self.manager.go_to(menu.OverlayMenuScene(self.game, self, 'pause'))
                if e.button == 1:
                    if True not in [ball.sticky for ball in self.balls]:
                        if self.heartattack_mode == 'ready':
                            self.heartattack_mode = 'killing'
                            self.heart_color = (255, 255, 255)
                            audio.stop_music()
                            audio.play_sfx('heartattack')

                            self.notif_stack.append(Message(str_r.get_str('heart_killing'), False))
                    for ball in self.balls:
                        ball.sticky = False

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(menu.OverlayMenuScene(self.game, self, 'pause'))
                if self.game.settings.debug:
                    self.handle_debug_key(e.key)
                if e.key == pg.K_SPACE:
                    if True not in [ball.sticky for ball in self.balls]:
                        if self.heartattack_mode == 'ready':
                            self.heartattack_mode = 'killing'
                            self.heart_color = (255, 255, 255)
                            audio.stop_music()
                            audio.play_sfx('heartattack')

                            self.notif_stack.append(Message(str_r.get_str('heart_killing'), False))
                    for ball in self.balls:
                        ball.sticky = False

            if e.type == pg.USEREVENT:
                s = ''
                if e.powerup == 'pack':
                    self.game.score += self.game.combo.points('powerup')
                    if e.amount > 1:
                        s = 's'
                    self.game.wallet.add_life(e.amount)
                if e.powerup == 'heartattack':
                    self.game.score += self.game.combo.points('powerup')
                    self.heartattack_mode = 'ready'
                if e.powerup == 'hotball':
                    self.game.score += self.game.combo.points('powerup')
                    self.balls.sprites()[0].hot_timer += e.timer
                if e.powerup == 'shorter':
                    self.player.shorter()
                if e.powerup == 'longer':
                    self.player.longer()
                    self.game.score += self.game.combo.points('powerup')
                if e.powerup == 'shoot':
                    self.game.score += self.game.combo.points('powerup')
                    self.shooting_active = True
                    self.shooting_period = e.timer
                if e.powerup == 'metastasis':
                    self.game.score += self.game.combo.points('powerup')
                    self.spread_metastasis(e.amount)

                self.notif_stack.append(Message(str_r.get_str(f'pu_{e.powerup}').format(s), 'normal'))
                if e.powerup == 'heartattack':
                    self.notif_stack.append(Message(str_r.get_str('push_to_kill'), None))


class Message:
    def __init__(self, msg, sfx='normal'):
        self.timer = 1000
        self.color = config.TEXT_COLOR
        self.msg = msg.upper()
        self.highlight_clock = 0
        self.std_sfx = sfx

    def update(self, dt):
        self.timer -= dt
        self.highlight_clock += dt
        if self.highlight_clock >= 50:
            self.color = utils.invert_color(self.color)
            self.highlight_clock = 0


def render_heartattack(scene, screen):
    if scene.heartattack_mode == 'killing':
        scene.heart_beat += 1
        if scene.heart_beat >= 4:
            scene.heart_beat = 0
            scene.heart_color = utils.invert_color(scene.heart_color)
    elif scene.heartattack_mode == 'ready':
        scene.heart_fade += 4 * scene.heart_fade_inv
        if not 0 < scene.heart_fade < 255:
            scene.heart_fade_inv *= -1
            scene.heart_fade += 4 * scene.heart_fade_inv
        scene.heart_color.a = 80 * round(scene.heart_fade / 80)

    color = pg.Color(scene.heart_color)  # a tuple while it flashes, opaque
    hud.cover(screen, color, color.a)
