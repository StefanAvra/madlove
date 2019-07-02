import collections
import random

import pygame as pg
import sys
import numpy
import os

import coins
import sound
import config
import menus
import string_resource as str_r
import levels
import bot
import scores
import controls as ctrls

bg_color = pg.Color(config.BACKGROUND_COLOR)
font_8 = None
font_16 = None
font_24 = None
stages = ['HEALTHY', 'IA1', 'IA2', 'IA3', 'IB', 'IIA', 'IIB', 'IIIA', 'IIIB', 'IIIC', 'IVA', 'IVA', 'IVB',
          'IVB', 'IVB', 'IVB']
score = 0
time_passed = 0

intro_order = [i for i in range(7)]
random.shuffle(intro_order)
current_intro = 1


class Scene(object):
    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError


class GameScene(Scene):
    def __init__(self, level_no):
        super(GameScene, self).__init__()
        self.bg = pg.Surface((32, 32))
        self.bg.convert()
        self.bg.fill(bg_color)
        self.current_stage = 0
        self.player = Player()
        self.balls = pg.sprite.Group()
        # self.balls.add(Ball())
        self.bricks = pg.sprite.Group()
        self.bombs = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
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
        self.credit = coins.get_credit()
        self.credit_text_timer = 0
        self.heartattack_mode = None
        self.heart_fade = 0
        self.heart_color = pg.Color(255, 255, 255, 0)
        self.heart_fade_inv = 1
        self.heart_beat = 0
        self.killing_timer = 0

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
        self.current_total_bricks = self.total_bricks
        self.all_sprites = pg.sprite.Group()
        self.all_sprites.add(self.player, self.balls, self.bricks, self.bombs)
        pg.mixer.music.load(os.path.join(sound.MUSIC_DIR, 'bgm.ogg'))
        pg.mixer.music.set_volume(0.8)
        self.reset_round()

    def render(self, screen):
        screen.fill(bg_color)

        if self.heartattack_mode is not None:
            render_heartattack(self, screen)

        render_hud(screen, str(score), stages[self.current_stage], str(coins.get_lives()), self.timer,
                   self.hud_highlight_combo)

        if self.notification is not None:
            text = font_16.render(self.notification.msg, True, self.notification.color)
            pos = text.get_rect()
            pos.center = (screen.get_width() / 2, 550)
            screen.blit(text, pos)

        self.all_sprites.draw(screen)

        if config.SHOW_VELOCITY:
            # first ball only
            velocity = self.balls.sprites()[0].velocity
            velocity = font_8.render(str((round(velocity[0], 2),
                                          round(velocity[1], 2))), True, config.DEBUG_COLOR)
            screen.blit(velocity, (40, 0))

        # if self.draw_credit:
        #     render_credit(self, screen)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        self.timer += time_passed

        up, left, right, down = [ctrls.get_buttons()[key] for key in (ctrls.UP, ctrls.LEFT, ctrls.RIGHT, ctrls.DOWN)]

        if config.ENABLE_BOT:
            left, right = bot.play(self.player, self.balls)
        if not self.heartattack_mode == 'killing':
            for ball in self.balls:
                ball.update(self.player, self.bricks, self.bombs)
            self.player.update(left, right, up)
        else:
            self.killing_timer += time_passed
            if self.killing_timer >= 1200 and not self.fade_leave_to:
                self.fadeout_step = 255
                self.fade_leave_to = 'finished'

        if self.fade_leave_to == 'finished' and self.fadeout_step <= 0:
            self.manager.go_to(FinishedLevelScene(self))

        if not self.balls.has(self.balls):
            self.manager.go_to(LostLifeScene(self))
        if not self.bricks.has(self.bricks) and not self.fade_leave_to:
            self.fadeout_step = 255
            self.fade_leave_to = 'finished'

        self.powerups.update(self.player.rect)

        past_stage = self.current_stage
        self.current_stage = int(numpy.interp(len(self.bricks), [0, self.total_bricks], [len(stages) - 1, 0]))
        if stages[past_stage] != stages[self.current_stage]:
            if stages[past_stage] == stages[0]:
                self.notif_stack.append(Message("got cancer!", 'cancer'))

        self.current_total_bricks = len(self.bricks)
        if self.total_bricks * 0.1 >= self.current_total_bricks:
            if self.heartattack_mode is None:
                pu_event = pg.event.Event(pg.USEREVENT, powerup='heartattack')
                pg.event.post(pu_event)

        if len(self.notif_stack) > 0 and self.notification is None:
            self.notification = self.notif_stack.pop(0)
            if self.notification.std_sfx == 'normal':
                sound.sfx_lib.get('message').play()
            elif self.notification.std_sfx == 'cancer':
                sound.sfx_lib.get('cancer').play()

        if self.notification is not None:
            if self.notification.timer <= 0:
                self.notification = None
            else:
                self.notification.update()

        scores.decrease_multiplier(time_passed)

        if scores.is_combo():
            new_combo = scores.get_new_combo()
            if new_combo in [25, 50, 100]:
                self.notif_stack.append(Message(str_r.get_combo_msg(new_combo)))

            self.hud_highlight_clock += time_passed
            if self.hud_highlight_clock >= 50:
                self.hud_highlight_clock = 0
                self.hud_highlight_combo += 1  # 1 for black, 2 for white combo text
                if self.hud_highlight_combo > 2:
                    self.hud_highlight_combo = 1
        else:
            self.hud_highlight_combo = 0

        if self.credit < coins.get_credit():
            self.credit = coins.get_credit()
            self.notif_stack.append(Message(self.credit_text.format(coins.get_credit()), sfx=False))

        if self.draw_credit:
            self.credit_text_timer += time_passed
            if self.credit_text_timer >= 2000:
                self.draw_credit = False
                self.credit_text_timer = 0

    def reset_round(self):
        pg.mixer.music.play(-1)
        self.balls.add(Ball(velocity=(random.randint(-2, 2), -3)))
        self.all_sprites.add(self.balls)
        self.player.rect.centerx = pg.display.get_surface().get_rect().centerx

    def spread_metastasis(self, amount=1):
        try:
            new_ball_pos = self.balls.sprites()[0].rect
        except IndexError:
            new_ball_pos = (random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT * 0.5))
        for ball in range(amount):
            self.balls.add(Ball(velocity=(random.randint(-3, 3), -3),
                                pos_x=new_ball_pos[0], pos_y=new_ball_pos[1], sticky=False))
            self.all_sprites.add(self.balls)
            print(new_ball_pos)

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button == 0:
                    self.manager.go_to(OverlayMenuScene(self, 'pause'))
                if e.button == 1:
                    if True not in [ball.sticky for ball in self.balls]:
                        if self.heartattack_mode == 'ready':
                            self.heartattack_mode = 'killing'
                            self.heart_color = (255, 255, 255)
                            pg.mixer.music.stop()
                            sound.sfx_lib.get('heartattack').play()
                            self.notif_stack.append(Message(str_r.get_str('heart_killing'), False))
                    for ball in self.balls:
                        ball.sticky = False

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'pause'))
                if e.key == pg.K_o:
                    for ball in self.balls:
                        ball.speed_up(0.9)
                if e.key == pg.K_p:
                    for ball in self.balls:
                        ball.speed_up(1.1)
                if e.key == pg.K_m:
                    if pg.mixer.music.get_busy():
                        pg.mixer.music.stop()
                    else:
                        pg.mixer.music.play(-1)
                if e.key == pg.K_b:
                    self.balls.add(Ball())
                    self.all_sprites.add(self.balls)
                if e.key == pg.K_COMMA:
                    config.ENABLE_BOT = not config.ENABLE_BOT
                if e.key == pg.K_f:
                    config.SHOW_FPS = not config.SHOW_FPS
                    config.SHOW_VELOCITY = not config.SHOW_VELOCITY
                if e.key == pg.K_SPACE:
                    if True not in [ball.sticky for ball in self.balls]:
                        if self.heartattack_mode == 'ready':
                            self.heartattack_mode = 'killing'
                            self.heart_color = (255, 255, 255)
                            pg.mixer.music.stop()
                            sound.sfx_lib.get('heartattack').play()
                            self.notif_stack.append(Message(str_r.get_str('heart_killing'), False))
                    for ball in self.balls:
                        ball.sticky = False

                if e.key == pg.K_n:
                    self.bricks.empty()
                if e.key == pg.K_h:
                    pu_event = pg.event.Event(pg.USEREVENT, powerup='metastasis')
                    pg.event.post(pu_event)

            if e.type == pg.USEREVENT:
                global score
                s = ''
                if e.powerup == 'pack':
                    score += scores.increase_score('powerup')
                    if e.cigs > 1:
                        s = 's'
                    coins.add_life(e.cigs)
                if e.powerup == 'heartattack':
                    score += scores.increase_score('powerup')
                    self.heartattack_mode = 'ready'
                if e.powerup == 'hotball':
                    score += scores.increase_score('powerup')
                if e.powerup == 'shorter':
                    self.player.shorter()
                if e.powerup == 'longer':
                    self.player.longer()
                    score += scores.increase_score('powerup')
                if e.powerup == 'shoot':
                    score += scores.increase_score('powerup')
                if e.powerup == 'metastasis':
                    score += scores.increase_score('powerup')
                    self.spread_metastasis(2)
                self.notif_stack.append(Message(str_r.get_str('pu_{}'.format(e.powerup)).format(s), 'normal'))
                if e.powerup == 'heartattack':
                    self.notif_stack.append(Message('push button to kill!', None))


class FinishedLevelScene(Scene):
    def __init__(self, game_state):
        super(FinishedLevelScene, self).__init__()
        self.finished_lvl = game_state.level_data.no
        self.current_stage = game_state.current_stage
        self.next_level = self.finished_lvl + 1
        self.fadein_step = 255
        self.fadeout_step = 0
        global score
        pg.mixer.music.stop()

    def render(self, screen):
        screen.fill(bg_color)

        # stage_text = font_16.render(stages[self.current_stage], True, config.TEXT_COLOR)
        # stage_pos = stage_text.get_rect()
        # stage_pos.midtop = (screen.get_width() / 2, 8)
        # screen.blit(stage_text, stage_pos)
        # lives_text = font_16.render(str_r.get_string('lives_text').format(self.lives), True, config.TEXT_COLOR)
        # screen.blit(lives_text, (screen.get_width() - 150, 8))
        # score_text = font_16.render(str(score), True, config.TEXT_COLOR)
        # score_pos = score_text.get_rect()
        # score_pos.topleft = (8, 8)
        # screen.blit(score_text, score_pos)

        # render_hud(screen, str(score), stages[self.current_stage], str(self.lives), 4000, 0)

        # todo: time bonus, perfect, picked up all power ups

        finished_text = font_16.render(str_r.get_str('finished'), True, config.TEXT_COLOR)
        finished_pos = finished_text.get_rect()
        finished_pos.center = screen.get_rect().center
        screen.blit(finished_text, finished_pos)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button in [0, 1]:
                    self.manager.go_to(IntroScene(self.next_level))
                    # self.manager.go_to(GameScene(self.next_level))
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'ingame-exit'))
                if e.key == pg.K_SPACE:
                    self.manager.go_to(IntroScene(self.next_level))
                    # self.manager.go_to(GameScene(self.next_level))


class LostLifeScene(Scene):
    def __init__(self, game_state):
        super(LostLifeScene, self).__init__()
        self.game_state = game_state
        coins.lose_life()
        self.game_over = False
        pg.mixer.music.stop()

        if coins.get_lives() <= 0:
            sound.sfx_lib.get('game_over').play()
            self.lost_text = str_r.get_str('zero_lives').splitlines()
            self.game_over = True
            self.fadeout_step = 255
            self.game_over_timer = 4000
            print('out of cigs')
        else:
            sound.sfx_lib.get('lost_life').play()
            self.lost_text = str_r.get_str('lost_life').splitlines()
            print('lost a life')
            self.fadeout_step = 0
        text_surf_x, text_surf_y = menus.PADDING * 2, menus.PADDING * 2
        text_surf_y += menus.MENU_LINE_OFFSET * len(self.lost_text) - menus.MENU_LINE_OFFSET / 2
        text_surf_x += 16 * len(max(self.lost_text, key=len))
        self.text_bg_surf = pg.Surface((text_surf_x, text_surf_y))
        self.text_bg_shadow = pg.Surface((self.text_bg_surf.get_rect().width, self.text_bg_surf.get_rect().height))

    def render(self, screen):
        # if not self.game_over:
        self.text_bg_surf.fill(bg_color)
        self.text_bg_shadow.fill(config.MENU_SHADOW_COLOR)
        for idx, line in enumerate(self.lost_text):
            lost_line_surf = font_16.render(line, True, config.TEXT_COLOR)
            lost_line_pos = lost_line_surf.get_rect()
            lost_line_pos.center = (screen.get_rect().centerx, screen.get_rect().centery + 100 + idx * menus.PADDING)
            lost_line_pos = (x_center_to(self.text_bg_surf, lost_line_surf),
                             menus.PADDING + idx * menus.MENU_LINE_OFFSET)
            self.text_bg_surf.blit(lost_line_surf, lost_line_pos)

        text_bg_pos = center_to(screen, self.text_bg_surf)
        text_bg_shadow_pos = (text_bg_pos[0] + config.MENU_SHADOW_OFFSET,
                              text_bg_pos[1] + config.MENU_SHADOW_OFFSET)

        screen.blit(self.text_bg_shadow, text_bg_shadow_pos)
        screen.blit(self.text_bg_surf, text_bg_pos)

        if self.fadeout_step > 0 >= self.game_over_timer:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        if self.game_over:
            if self.game_over_timer > 0:
                self.game_over_timer -= time_passed
            else:
                if self.fadeout_step <= 0:
                    self.manager.go_to(ContinueScene(self.game_state))

    def handle_events(self, events):
        if not self.game_over:
            for e in events:
                if e.type == pg.JOYBUTTONDOWN:
                    if e.button in [0, 1]:
                        self.game_state.reset_round()
                        self.go_back()
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_SPACE:
                        self.game_state.reset_round()
                        self.go_back()
                    if e.key == pg.K_ESCAPE:
                        pass

    def go_back(self):
        pg.mixer.music.unpause()
        self.manager.go_to(self.game_state)


class TitleScene(Scene):
    def __init__(self):
        super(TitleScene, self).__init__()
        # self.line1 = font_24.render(config.GAME_TITLE, True, config.TEXT_COLOR)
        self.line2 = font_16.render(config.GAME_SUBTITLE, True, config.TEXT_COLOR)
        self.cprght = font_8.render(str_r.get_str('copyright'), True, config.TEXT_COLOR)
        self.coin_text = str_r.get_str('start') if coins.get_credit() > 0 else str_r.get_str('coin')
        self.draw_coin_text = True
        self.credit_text = str_r.get_str('credit')
        self.draw_credit = False
        self.ready_to_play = False
        # self.menu = menus.get_entries('titlescreen')
        # self.menu_funcs = menus.get_funcs('titlescreen')
        self.highlight_clock = 0
        self.highlight_color = config.TEXT_COLOR
        self.cursor = 0
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave_to = False
        self.title = Title()
        self.arrow = Arrow()
        self.bg_arrow = Arrow(True)
        self.blit_elements = [False, False, False, False]
        pg.mixer.music.load(os.path.join(sound.MUSIC_DIR, 'titlescreen.ogg'))
        # pg.mixer.music.play(-1)
        sound.sfx_lib.get('intro1').play()
        self.timer = 0
        self.wait_for_music = True

        self.cigs = pg.sprite.Group()
        self.draw_cigs = False
        self.cig_fade = 0
        self.cig_fade_invert = 1
        cig_grid = (5, 4)
        cig_offset = (int(480 / cig_grid[0]), int(640 / cig_grid[1]) + 18)
        for y in range(cig_grid[1]):
            for x in range(cig_grid[0]):
                cig = pg.sprite.Sprite()
                cig.image = pg.image.load(os.path.join('assets', 'graphics', 'paddle_m.png')).convert()
                cig.image = pg.transform.rotate(cig.image, -90)
                cig.rect = cig.image.get_rect()
                cig.rect.midtop = (cig_offset[0] * x + 48, cig_offset[1] * y)
                self.cigs.add(cig)

    def render(self, screen):
        screen.fill(bg_color)
        if self.draw_cigs:
            self.cigs.draw(screen)
        if self.bg_arrow.active:
            screen.blit(self.bg_arrow.image, self.bg_arrow.rect)
        # pos_line1 = center_to(screen, self.line1)
        # pos_line1 = (pos_line1[0], pos_line1[1] - 24)
        pos_line2 = center_to(screen, self.line2)
        pos_line2 = (pos_line2[0], pos_line2[1] + 16)
        pos_copy = self.cprght.get_rect()
        pos_copy.center = (screen.get_rect().centerx, screen.get_rect().height * 0.9)
        # screen.blit(self.line1, pos_line1)
        if self.blit_elements[1]:
            screen.blit(self.line2, pos_line2)
        if self.blit_elements[3]:
            screen.blit(self.cprght, pos_copy)
        # for idx, entry in enumerate(self.menu):
        #     if self.cursor == idx:
        #         if self.highlight_clock >= 100:
        #             self.highlight_color = tuple(numpy.subtract((255, 255, 255), self.highlight_color))
        #             self.highlight_clock = 0
        #         color = self.highlight_color
        #     else:
        #         color = config.TEXT_COLOR
        #     entry_surf = font_16.render(entry, True, color)
        #     entry_pos = (x_center_to(screen, entry_surf), 400 + idx * menus.MENU_LINE_OFFSET)
        #     screen.blit(entry_surf, entry_pos)

        if self.blit_elements[2]:
            render_coin_text(self, screen)
        if self.blit_elements[0]:
            screen.blit(self.title.image, self.title.rect)

        render_credit(self, screen)

        screen.blit(self.arrow.image, self.arrow.rect)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        self.timer += time_passed
        if self.timer > 30000 and not self.fade_leave_to:
            self.fadeout_step = 255
            self.fade_leave_to = 2
        if self.fade_leave_to and self.fadeout_step <= 0:
            if self.fade_leave_to == 1:
                # self.manager.go_to(GameScene(0))
                self.manager.go_to(IntroScene(0))
            if self.fade_leave_to == 2:
                self.manager.go_to(HighscoreScene(previous_scene=self))
            if self.fade_leave_to == 3:
                self.manager.go_to(TitleScene())

        update_highlight_text(self)

        self.title.update()
        self.arrow.update()
        if not self.arrow.done:
            if self.arrow.rect.centery >= 213:
                self.blit_elements[0] = True
                if self.arrow.rect.centery >= 240:
                    self.blit_elements[1] = True
                    if self.arrow.rect.centery >= 400:
                        self.blit_elements[2] = True
                        if self.arrow.rect.centery >= 550:
                            self.blit_elements[3] = True
                            if self.arrow.rect.centery >= 640:
                                self.bg_arrow.active = True
                                self.draw_credit = True
                                if not pg.mixer.music.get_busy():
                                    pg.mixer.music.play(1)
                                    self.wait_for_music = False
        if self.bg_arrow.active:
            self.bg_arrow.update()
            if self.bg_arrow.done:
                self.title.animate = True
        if not pg.mixer.music.get_busy() and not self.wait_for_music and not self.fade_leave_to:
            self.fadeout_step = 255
            self.fade_leave_to = 3

        if not self.draw_cigs and self.timer > 5350:
            self.draw_cigs = True

        if self.draw_cigs:
            for cig in self.cigs:
                cig.rect.y += 1
                cig.image.set_alpha(40 * round(self.cig_fade / 40))
                if cig.rect.y > 640:
                    cig.rect.y = 0 - cig.rect.height

            if self.cig_fade not in range(0, 255):
                self.cig_fade_invert = self.cig_fade_invert * -1
            self.cig_fade += 1 * self.cig_fade_invert

    def handle_events(self, events):
        if not self.fade_leave_to:
            for e in events:
                if e.type == pg.JOYBUTTONDOWN:
                    if e.button == 0:
                        if self.ready_to_play:
                            sound.sfx_lib.get('select').play()
                            coins.consume_coin()
                            self.fadeout_step = 255
                            self.fade_leave_to = 1
                        # f = self.menu_funcs[self.cursor]
                        # if f == 'start':
                        #     self.fade_leave_to = 1
                        # elif f == 'scores':
                        #     self.fade_leave_to = 2
                        # elif f == 'credits':
                        #     pass

                if e.type == pg.JOYAXISMOTION:
                    # if e.axis == 1:
                    #     if e.value < 0:
                    #         sound.sfx_lib.get('menu_nav').play()
                    #         self.cursor -= 1
                    #         if self.cursor < 0:
                    #             self.cursor = len(self.menu) - 1
                    #     if e.value > 0:
                    #         sound.sfx_lib.get('menu_nav').play()
                    #         self.cursor += 1
                    #         if self.cursor >= len(self.menu):
                    #             self.cursor = 0
                    pass

                if e.type == pg.KEYDOWN:
                    if e.key in [pg.K_SPACE, pg.K_RETURN]:
                        if self.ready_to_play:
                            sound.sfx_lib.get('select').play()
                            coins.consume_coin()
                            self.fadeout_step = 255
                            self.fade_leave_to = 1
                            # f = self.menu_funcs[self.cursor]
                            # if f == 'start':
                            #     self.fade_leave_to = 1
                            # elif f == 'scores':
                            #     self.fade_leave_to = 2
                            # elif f == 'credits':
                            #     pass
                    if e.key == pg.K_1:
                        # coins.add_coin()
                        pass
                    if e.key == pg.K_ESCAPE:
                        self.manager.go_to(OverlayMenuScene(self, 'exit'))
                    if e.key == pg.K_h:
                        self.manager.go_to(HighscoreScene())
                    # if e.key == pg.K_DOWN:
                    #     sound.sfx_lib.get('menu_nav').play()
                    #     self.cursor += 1
                    #     if self.cursor >= len(self.menu):
                    #         self.cursor = 0
                    # if e.key == pg.K_UP:
                    #     sound.sfx_lib.get('menu_nav').play()
                    #     self.cursor -= 1
                    #     if self.cursor < 0:
                    #         self.cursor = len(self.menu) - 1


class GameOver(Scene):
    def __init__(self, game_state):
        super(GameOver, self).__init__()
        global score
        self.score = score
        score = 0
        self.reached_lvl = game_state.level_data.no + 1
        self.reached_stage = game_state.current_stage
        self.game_over_text = 'GAME OVER'
        self.is_highscore = self.score > scores.lowest_score()
        self.place, self.place_no = scores.get_place(self.score)
        self.blit_elements = [False] * 5
        self.timer = 0
        self.alphabet = str_r.get_alphabet()
        self.cursor = 0
        self.alphabet_pointer = self.alphabet.index(' ')
        self.cursor_clock = 0
        self.cursor_color = config.MENU_COLOR_HIGHLIGHT
        self.blit_cursor = False
        self.name = list('        ')
        self.name_input_active = True if self.is_highscore else False
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave = False

        pg.mixer.music.load(os.path.join(sound.MUSIC_DIR, 'smoke_break.ogg'))
        pg.mixer.music.play(-1)

    def render(self, screen):
        screen.fill(bg_color)
        # todo: make game over text wave
        game_over_surf = font_24.render(self.game_over_text, True, config.TEXT_COLOR)
        game_over_rect = game_over_surf.get_rect()
        game_over_rect.center = (screen.get_width() / 2, screen.get_height() * 0.1)
        screen.blit(game_over_surf, game_over_rect)
        y_offset = game_over_rect.center[1] + 146
        f_line = '{:<13} {:>10}'
        if self.blit_elements[0]:
            # level = font_16.render(f'YOU REACHED LEVEL {self.reached_lvl}', True, config.TEXT_COLOR)
            level = font_16.render(f_line.format(str_r.get_str('reached_level'),
                                                self.reached_lvl), True, config.TEXT_COLOR)
            level_pos = level.get_rect()
            level_pos.topleft = (50, y_offset)
            screen.blit(level, level_pos)
            y_offset += level_pos.height * 2
        if self.blit_elements[1]:
            # stage = font_16.render(f'CANCER STAGE {stages[self.reached_stage]}' if self.reached_stage > 0
            #                        else stages[self.reached_stage], True, config.TEXT_COLOR)
            stage = font_16.render(f_line.format(str_r.get_str('cancer_stage'),
                                               stages[self.reached_stage]), True, config.TEXT_COLOR)
            stage_pos = stage.get_rect()
            stage_pos.topleft = (50, y_offset)
            screen.blit(stage, stage_pos)
            y_offset += stage_pos.height * 2
        if self.blit_elements[2]:
            your_score = font_16.render(f_line.format(str_r.get_str('end_score'), self.score), True, config.TEXT_COLOR)
            your_score_pos = your_score.get_rect()
            # your_score_pos.center = (screen.get_width() / 2, y_offset)
            your_score_pos.topleft = (50, y_offset)
            screen.blit(your_score, your_score_pos)
            y_offset += your_score_pos.height * 3
        # if self.blit_elements[3]:
        #     score_surf = font_16.render(str(self.score), True, config.TEXT_COLOR)
        #     score_pos = score_surf.get_rect()
        #     score_pos.center = (screen.get_width() / 2, y_offset)
        #     screen.blit(score_surf, score_pos)
        #     y_offset += score_pos.height * 3
        if self.is_highscore:
            if self.blit_elements[3]:
                # place = font_16.render(f'CONGRATULATIONS!'
                #                        f'YOU ARE ON {self.place} PLACE!', True, config.TEXT_COLOR)
                congrats_lines = str_r.get_str('congrats').splitlines()
                y_offset_congrats = 72
                for line in congrats_lines:
                    place = font_16.render(line.format(self.place), True, config.TEXT_COLOR)
                    place_pos = place.get_rect()
                    # place_pos.center = (screen.get_width() / 2, y_offset)
                    place_pos.center = (screen.get_width() / 2, game_over_rect.center[1] + y_offset_congrats)
                    screen.blit(place, place_pos)
                    y_offset_congrats += place_pos.height * 2
                    y_offset += place_pos.height * 2
            if self.blit_elements[4]:
                # name = font_16.render(f'ENTER NAME: {"".join(self.name)}', True, config.TEXT_COLOR)
                name = font_16.render(f_line.format(str_r.get_str('enter_name'), ''.join(self.name)),
                                      True, config.TEXT_COLOR)
                name_pos = name.get_rect()
                name_pos.center = (screen.get_width() / 2, y_offset)
                screen.blit(name, name_pos)
                if self.blit_cursor:
                    cursor_surf = pg.Surface((16, 17)).convert_alpha()
                    cursor_surf.fill(self.cursor_color)
                    cursor_surf.set_alpha(128)
                    cursor_pos = cursor_surf.get_rect()
                    cursor_pos.topleft = (name_pos.x + 16 * 16 + self.cursor * 16, name_pos.y)
                    screen.blit(cursor_surf, cursor_pos)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        if False in self.blit_elements:
            self.timer += time_passed
            if self.timer >= 200:
                self.timer = 0
                self.blit_elements.insert(0, True)
                self.blit_elements.remove(False)
        else:
            if self.name_input_active:
                self.cursor_clock += time_passed
                if self.cursor_clock >= 200:
                    self.cursor_clock = 0
                    self.blit_cursor = not self.blit_cursor
            elif self.fade_leave and self.fadeout_step <= 0:
                self.manager.go_to(HighscoreScene(highlight_place=self.place_no, mode='gameover'))
            elif not self.fade_leave:
                self.timer += time_passed
                if self.timer >= 5000:
                    self.fade_leave = True
                    self.fadeout_step = 255

    def handle_events(self, events):
        # todo: change chars by holding down
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button == 1:
                    if self.cursor == len(self.name) - 1:
                        self.accept_name()
                    else:
                        self.next_char()

            if e.type == pg.JOYAXISMOTION:
                if e.axis == 1:
                    if e.value < 0:
                        self.decr_char()
                    if e.value > 0:
                        self.incr_char()
                if e.axis == 0:
                    if e.value < 0:
                        self.prev_char()
                    if e.value > 0:
                        self.next_char()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    if self.cursor == len(self.name) - 1:
                        self.accept_name()
                    else:
                        self.next_char()
                if e.key == pg.K_RETURN:
                    self.accept_name()
                if e.key == pg.K_UP:
                    self.decr_char()
                if e.key == pg.K_DOWN:
                    self.incr_char()
                if e.key == pg.K_LEFT:
                    self.prev_char()
                if e.key == pg.K_RIGHT:
                    self.next_char()

    def decr_char(self):
        if self.name_input_active and self.blit_elements[4]:
            self.alphabet_pointer -= 1
            if self.alphabet_pointer < 0:
                self.alphabet_pointer = len(self.alphabet) - 1
            self.name[self.cursor] = self.alphabet[self.alphabet_pointer]
            sound.sfx_lib.get('text').play()

    def incr_char(self):
        if self.name_input_active and self.blit_elements[4]:
            self.alphabet_pointer += 1
            self.alphabet_pointer = self.alphabet_pointer % (len(self.alphabet))
            self.name[self.cursor] = self.alphabet[self.alphabet_pointer]
            sound.sfx_lib.get('text').play()

    def prev_char(self):
        if self.name_input_active and self.blit_elements[4]:
            if self.cursor > 0:
                self.cursor -= 1
                self.alphabet_pointer = self.alphabet.index(self.name[self.cursor])
                sound.sfx_lib.get('menu_nav').play()

    def next_char(self):
        if self.name_input_active and self.blit_elements[4]:
            if self.cursor < len(self.name) - 1:
                self.cursor += 1
                self.alphabet_pointer = self.alphabet.index(self.name[self.cursor])
                sound.sfx_lib.get('menu_nav').play()

    def accept_name(self):
        if self.name_input_active:
            self.name_input_active = False
            self.blit_cursor = False
            sound.sfx_lib.get('select').play()
            scores.update_highscores((''.join(self.name), self.score))
            scores.save_highscores()
            self.fadeout_step = 255
            self.fade_leave = True


class ContinueScene(Scene):
    def __init__(self, game_state):
        super(ContinueScene, self).__init__()
        self.game_state = game_state
        # self.lives_left = coins.get_lives()
        self.game_over = False
        self.countdown_timer = 10000
        self.countdown = int(self.countdown_timer / 1000)
        self.countdown_active = False if coins.get_credit() > 0 else True
        self.countdown_text = str_r.get_str('no_cigs').splitlines()
        self.countdown_color = config.TEXT_COLOR
        self.highlight_clock = 0
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave_to = None
        self.coin_text = str_r.get_str('coin')
        self.coin_text_clock = 0
        self.draw_coin_text = True
        self.highlight_color = config.TEXT_COLOR

        if pg.mixer.music.get_busy():
            pg.mixer.music.stop()

    def render(self, screen):
        screen.fill(bg_color)

        # if self.countdown_active:
        for idx, line in enumerate(self.countdown_text):
            text_surf = font_16.render(line, True, config.TEXT_COLOR)
            text_rect = text_surf.get_rect()
            text_rect.center = (screen.get_rect().centerx, 150 + idx * menus.PADDING)
            screen.blit(text_surf, text_rect)
        counter = font_24.render(str(self.countdown), True, self.countdown_color)
        counter_pos = counter.get_rect()
        counter_pos.center = screen.get_rect().center
        screen.blit(counter, counter_pos)

        if coins.get_credit() == 0:
            render_coin_text(self, screen)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        if self.fade_leave_to is None:
            if self.game_over:
                self.fadeout_step = 255
                self.fade_leave_to = 'gameover'
            else:
                if coins.get_credit() > 0:
                    self.fadeout_step = 255
                    self.countdown_active = False
                    self.fade_leave_to = 'consume_coin'
                else:
                    self.countdown_active = True
            if self.countdown_active and self.fadein_step <= 0:
                if self.countdown_timer < 4000:
                    self.highlight_clock += time_passed
                    if self.highlight_clock >= 100:
                        self.highlight_clock = 0
                        self.countdown_color = tuple(numpy.subtract((255, 255, 255), self.countdown_color))
                if self.countdown_timer > 0:
                    self.countdown_timer -= time_passed
                else:
                    self.game_over = True
                if not self.countdown == int(self.countdown_timer / 1000):
                    self.countdown = int(self.countdown_timer / 1000)
                    sound.sfx_lib.get('countdown').play()
        elif self.fadeout_step <= 0:
            if self.fade_leave_to == 'gameover':
                self.manager.go_to(GameOver(self.game_state))
            if self.fade_leave_to == 'consume_coin':
                self.manager.go_to(ConsumeCoinScene(self.game_state))

        self.coin_text_clock += time_passed
        if self.coin_text_clock >= 400:
            self.draw_coin_text = not self.draw_coin_text
            self.coin_text_clock = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button == 0:
                    sound.sfx_lib.get('game_over').stop()
                    self.manager.go_to(TitleScene())

            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE]:
                    self.countdown_timer -= 1000
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'exit'))


class ConsumeCoinScene(Scene):
    def __init__(self, game_state):
        super(ConsumeCoinScene, self).__init__()
        self.game_state = game_state
        self.penalty = 0
        self.consume_coins_text = str_r.get_str('consume_coins').splitlines()
        self.consume_coins = False
        self.consume_coins_values = [score, self.penalty, coins.get_credit(), coins.get_lives()]
        self.blit_elements = [False] * 4
        self.blit_timer = 0
        self.score_timer = 0
        self.points_done = False
        self.cigs_bought = False
        self.fadeout_step = 0
        self.fadein_step = 0
        self.leave = False
        self.convert_step = 0

    def render(self, screen):
        screen.fill(bg_color)
        lines = []
        for idx, line in enumerate(self.consume_coins_text):
            new_line = '{:<10} {:>13}'.format(line, self.consume_coins_values[idx])
            text_surf = font_16.render(new_line, True, config.TEXT_COLOR)
            text_pos = text_surf.get_rect()
            text_pos.topleft = (50, 150 + (40 * idx))
            lines.append((text_surf, text_pos))

        for idx, blit in enumerate(self.blit_elements):
            if blit:
                screen.blit(lines[idx][0], lines[idx][1])

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        global score
        self.consume_coins_values = [score, self.penalty, coins.get_credit(), coins.get_lives()]
        self.blit_timer += time_passed
        if self.blit_timer >= 100:
            self.blit_timer = 0
            if False in self.blit_elements:
                self.blit_elements.insert(0, True)
                self.blit_elements.remove(False)

        if False not in self.blit_elements:
            self.score_timer += time_passed
            if not self.cigs_bought:
                if self.score_timer >= 1000:
                    self.cigs_bought = True
                    coins.consume_coin()
                    sound.sfx_lib.get('coin').play()
                    self.penalty, self.convert_step = scores.get_penalty(score)
            elif not self.points_done:
                if self.score_timer >= 2000:
                    # convert_step = 10
                    score -= self.convert_step
                    if score < 0:
                        score = 0
                    self.penalty += self.convert_step
                    if self.penalty >= 0:
                        self.penalty = 0
                        self.points_done = True
                        self.score_timer = 0
                    sound.sfx_lib.get('point').play()
            else:
                if self.score_timer >= 2000 and not self.leave:
                    self.fadeout_step = 255
                    self.leave = True
                if self.leave and self.fadeout_step <= 0:
                    self.game_state.reset_round()
                    self.manager.go_to(self.game_state)

    def handle_events(self, events):
        pass


class OverlayMenuScene(Scene):
    def __init__(self, paused_scene, menu_type):
        super(OverlayMenuScene, self).__init__()
        self.menu_type = menu_type
        self.menu_entries = menus.get_entries(menu_type)
        self.menu_surf = menus.get_surf(menu_type)
        self.menu_drop_shadow = pg.Surface((self.menu_surf.get_rect().width, self.menu_surf.get_rect().height))
        self.menu_title = menus.get_title(menu_type)
        self.menu_funcs = menus.get_funcs(menu_type)
        self.paused_scene = paused_scene
        self.cursor = 0
        self.highlight_clock = 0
        self.highlight_color = config.MENU_COLOR_HIGHLIGHT
        self.animation_clock = 0
        self.music_timer = 0
        pg.mixer.music.pause()
        if self.menu_type == 'pause':
            sound.sfx_lib.get('pause_in').play()
            self.animation = Ashtray()
            pg.mixer.music.load(os.path.join(sound.MUSIC_DIR, 'smoke_break.ogg'))

    def render(self, screen):

        self.highlight_clock += time_passed
        # menus.make_outline(self.menu_surf, bg_color)
        self.menu_surf.fill(bg_color)
        self.menu_drop_shadow.fill(config.MENU_SHADOW_COLOR)
        menu_pos = center_to(screen, self.menu_surf)
        shadow_pos = (menu_pos[0] + config.MENU_SHADOW_OFFSET, menu_pos[1] + config.MENU_SHADOW_OFFSET)
        title = font_16.render(self.menu_title, True, config.TEXT_COLOR)
        title_pos = (x_center_to(self.menu_surf, title), menus.PADDING)
        self.menu_surf.blit(title, title_pos)

        if self.menu_type != 'pause':
            for idx, entry in enumerate(self.menu_entries):
                if self.cursor == idx:
                    if self.highlight_clock >= 100:
                        self.highlight_color = tuple(numpy.subtract((255, 255, 255), self.highlight_color))
                        self.highlight_clock = 0
                    color = self.highlight_color
                else:
                    color = config.TEXT_COLOR
                entry_surf = font_16.render(entry, True, color)
                entry_pos = (x_center_to(self.menu_surf, entry_surf),
                             menus.PADDING + menus.HEADER_SIZE + idx * menus.MENU_LINE_OFFSET)
                self.menu_surf.blit(entry_surf, entry_pos)
        else:
            animation_pos = (x_center_to(self.menu_surf, self.animation.image), menus.PADDING + menus.HEADER_SIZE)
            self.menu_surf.blit(self.animation.image, animation_pos)

        screen.blit(self.menu_drop_shadow, shadow_pos)
        screen.blit(self.menu_surf, menu_pos)

    def update(self):
        self.music_timer += time_passed
        if not pg.mixer.music.get_busy() and self.music_timer >= 1000:
            pg.mixer.music.play(-1)
        if self.menu_type == 'pause':
            self.animation_clock += time_passed
            if self.animation_clock >= 100:
                self.animation.update()
                self.animation_clock = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button in [0, 1]:
                    f = self.menu_funcs[self.cursor]
                    if f == 'back':
                        self.go_back()
                    else:
                        f()
            if self.menu_type != 'pause':
                if e.type == pg.JOYAXISMOTION:
                    if e.axis == 1:
                        if e.value < 0:
                            sound.sfx_lib.get('menu_nav').play()
                            self.cursor -= 1
                            if self.cursor < 0:
                                self.cursor = len(self.menu_entries) - 1
                        if e.value > 0:
                            sound.sfx_lib.get('menu_nav').play()
                            self.cursor += 1
                            if self.cursor >= len(self.menu_entries):
                                self.cursor = 0

            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE, pg.K_RETURN]:
                    f = self.menu_funcs[self.cursor]
                    if f == 'back':
                        self.go_back()
                    else:
                        f()
                if e.key == pg.K_ESCAPE:
                    self.go_back()
                if self.menu_type != 'pause':
                    if e.key == pg.K_DOWN:
                        sound.sfx_lib.get('menu_nav').play()
                        self.cursor += 1
                        if self.cursor >= len(self.menu_entries):
                            self.cursor = 0
                    if e.key == pg.K_UP:
                        sound.sfx_lib.get('menu_nav').play()
                        self.cursor -= 1
                        if self.cursor < 0:
                            self.cursor = len(self.menu_entries) - 1

    def go_back(self):
        pg.mixer.music.stop()
        sound.sfx_lib.get('pause_out').play()
        pg.mixer.music.load(os.path.join(sound.MUSIC_DIR, 'bgm.ogg'))
        pg.mixer.music.play(-1)
        self.manager.go_to(self.paused_scene)


class HighscoreScene(Scene):
    def __init__(self, mode='show', previous_scene=None, highlight_place=None):
        super(HighscoreScene, self).__init__()
        scores.load_highscores()
        self.lines = []
        self.previous_scene = previous_scene
        self.highlight_place = highlight_place
        self.highlight_place_clock = 0
        self.title = font_16.render(str_r.get_str('highscores_title'), True, config.TEXT_COLOR)
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave_to = False
        self.print_step = 0
        self.clock = 0
        self.mode = mode
        self.leave_timer = 5000
        self.leaving = False
        self.draw_coin_text = True
        self.ready_to_play = False
        self.coin_text = str_r.get_str('start') if coins.get_credit() > 0 else str_r.get_str('coin')
        self.highlight_clock = 0
        self.highlight_color = config.TEXT_COLOR
        self.draw_credit = True if mode == 'show' else False
        self.credit_text = str_r.get_str('credit')

    def render(self, screen):

        screen.fill(bg_color)
        title_pos = self.title.get_rect()
        title_pos.center = (screen.get_width() / 2, screen.get_height() * 0.1)
        screen.blit(self.title, title_pos)
        self.lines = []
        place = 0
        for highscore in scores.highscores:
            place += 1
            new_line = '{:<2}   {:<8} {:>10}'.format(place, highscore[0], highscore[1])
            if self.mode == 'gameover' and place == self.highlight_place:
                self.lines.append(font_16.render(new_line, True, self.highlight_color))
            else:
                self.lines.append(font_16.render(new_line, True, config.TEXT_COLOR))
        for idx, line in enumerate(self.lines[:self.print_step]):
            screen.blit(line, (50, 150 + (40 * idx)))

        if self.mode == 'show':
            render_coin_text(self, screen, y_pos=0.9)

        render_credit(self, screen)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        if self.print_step < 10:
            self.clock += time_passed
            if self.clock >= 100:
                self.clock = 0
                self.print_step += 1
        elif self.mode in ['show', 'gameover']:
            self.leave_timer -= time_passed
            if self.leave_timer < 0 and not self.leaving:
                self.fadeout_step = 255
                self.fade_leave_to = True
                self.leaving = True

        if self.fade_leave_to and self.fadeout_step <= 0:
            # todo: go to credits
            if self.fade_leave_to == 'game':
                self.manager.go_to(IntroScene(0))
            elif self.previous_scene:
                self.previous_scene.fade_leave_to = False
                self.previous_scene.timer = 0
                self.previous_scene.fadein_step = 255
                self.previous_scene.title.restart_animation(timer=2000)
                self.manager.go_to(self.previous_scene)
            else:
                self.manager.go_to(TitleScene())

        if self.mode == 'show':
            update_highlight_text(self)

        if self.mode == 'gameover':
            self.highlight_place_clock += time_passed
            if self.highlight_place_clock >= 400:
                self.highlight_color = tuple(numpy.subtract((255, 255, 255), self.highlight_color))
                self.highlight_place_clock = 0

    def handle_events(self, events):
        for e in events:
            if not self.fade_leave_to:
                if e.type == pg.JOYBUTTONDOWN:
                    if e.button == 0:
                        if self.ready_to_play:
                            sound.sfx_lib.get('select').play()
                            coins.consume_coin()
                            self.fadeout_step = 255
                            self.fade_leave_to = 'game'

                if e.type == pg.KEYDOWN:
                    if self.ready_to_play:
                        if e.key in [pg.K_SPACE, pg.K_RETURN]:
                            sound.sfx_lib.get('select').play()
                            coins.consume_coin()
                            self.fadeout_step = 255
                            self.fade_leave_to = 'game'
                    if e.key == pg.K_1:
                        # coins.add_coin()
                        pass
                    if e.key == pg.K_ESCAPE:
                        self.fadeout_step = 255
                        self.fade_leave_to = True


class CreditsScene(Scene):
    def __init__(self):
        super(CreditsScene, self).__init__()

    def render(self, screen):
        pass

    def update(self):
        pass

    def handle_events(self, events):
        pass


class IntroScene(Scene):
    # should be called before the next level/GameScene()
    def __init__(self, next_lvl):
        super(IntroScene, self).__init__()
        self.next_lvl = next_lvl
        self.text = str_r.get_fact()
        self.text_cursor = 0
        self.intro = pg.image.load(os.path.join('assets', 'graphics', 'level_intro_{}.png'.format(self.get_intro())))
        self.timer = 0
        self.text_cursor_speed = 40
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave = False
        self.delay_done = False
        pg.mixer.music.stop()

    def render(self, screen):
        # screen.fill(bg_color)
        screen.blit(self.intro, (0, 0))
        fact_offset = 0
        for text in self.text[:self.text_cursor].split('\n'):
            # todo: align in center
            fact = font_16.render(text, True, config.MENU_COLOR_HIGHLIGHT)
            screen.blit(fact, (8, 8 + fact_offset))
            fact_offset += 24

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        self.timer += time_passed
        if self.timer > 700:
            self.delay_done = True
        if self.delay_done:
            if self.text_cursor < len(self.text):
                if self.timer >= self.text_cursor_speed:
                    self.timer = 0
                    self.text_cursor += 1
                    sound.sfx_lib.get('text').play()
            elif not self.fade_leave and self.timer > 3000:
                self.fade_leave = True
                self.fadeout_step = 255
            if self.fade_leave and self.fadeout_step <= 0:
                self.manager.go_to(GameScene(self.next_lvl))

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE]:
                    self.text_cursor_speed = 10
            if e.type == pg.KEYUP:
                if e.key in [pg.K_SPACE]:
                    self.text_cursor_speed = 40

            if e.type == pg.JOYBUTTONDOWN:
                if e.button in [0, 1]:
                    self.text_cursor_speed = 10
            if e.type == pg.JOYBUTTONUP:
                if e.button in [0, 1]:
                    self.text_cursor_speed = 40

    @staticmethod
    def get_intro():
        global current_intro
        number = current_intro
        current_intro += 1
        if current_intro > len(intro_order):
            current_intro = 1
        return number


class SceneManager(object):
    def __init__(self):
        self.scene = None
        self.go_to(TitleScene())

    def go_to(self, scene):
        print('Switching to {}'.format(scene.__class__.__name__))
        self.scene = scene
        self.scene.manager = self


class Ball(pg.sprite.Sprite):
    def __init__(self, pos_x=240, pos_y=550, velocity=(random.randint(-3, 3), -3), size=7, sticky=True):
        super().__init__()
        self.velocity = velocity
        self.x = pos_x
        self.y = pos_y
        self.size = size
        self.color = config.BALL_COLOR
        self.image = pg.Surface((self.size,) * 2)
        self.image.fill(bg_color)
        self.image.set_colorkey(bg_color)
        pg.draw.circle(self.image, self.color, (int(self.size / 2),) * 2, int(self.size / 2))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.collisions = [False] * 8
        self.last_bounces = collections.deque([], 18)
        self.last_bounce_times = collections.deque([], 3)
        self.tail = collections.deque([], 10)
        self.sticky = sticky

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
        sound.sfx_lib.get('hit_wall').play()
        # self.velocity = ((self.rect.center[0] - x_hit) * 0.09 + self.velocity[0], -abs(self.velocity[1]))
        self.velocity = (round((self.rect.centerx - x_hit) / 5), -abs(self.velocity[1]))
        self.rect.bottom = paddle_rect.y - 1

    def hit_wall(self, left_right):
        sound.sfx_lib.get('hit_wall').play()
        if left_right == 0:
            self.bounce(6)
            self.rect.left = 1
        else:
            self.bounce(2)
            self.rect.right = pg.display.get_surface().get_width() - 1

    def hit_top(self):
        sound.sfx_lib.get('hit_wall').play()
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

    def hit_brick(self, brick):
        global score
        self.check_collision(brick.rect)
        if True in self.collisions[::2]:
            self.bounce(self.collisions[::2].index(True) * 2)
        else:
            self.bounce(self.collisions.index(True))
        brick.health -= 1
        brick.update()
        score += scores.increase_score()
        scores.increase_multiplier()
        if brick.health <= 0:
            brick.kill()
            score += scores.increase_score('killed_brick')
        sound.sfx_lib.get('hit_brick').play()

    def update(self, player, bricks, bombs):
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
        # collision detection is just as accurate as it should be. at high speeds glitches can occure that

        if collided_brick:
            self.hit_brick(collided_brick)

    def speed_up(self, factor=1.1):
        self.velocity = (self.velocity[0] * factor, self.velocity[1] * factor)


class Player(pg.sprite.Sprite):
    def __init__(self, x=200, p_type='m', speed=7):
        super().__init__()
        self.type = p_type
        self.speed = speed
        self.image = pg.image.load(os.path.join('assets', 'graphics', 'paddle_{}.png'.format(self.type))).convert()
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
        self.image = pg.image.load(os.path.join('assets', 'graphics', 'paddle_{}.png'.format(self.type))).convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = temp_rect.centerx
        self.rect.y = config.PLAYER_Y

    def longer(self):
        current_length = self.lengths.index(self.type)
        if current_length < len(self.lengths)-1:
            self.update_length(self.lengths[current_length+1])

    def shorter(self):
        current_length = self.lengths.index(self.type)
        if current_length > 0:
            self.update_length(self.lengths[current_length-1])


class Brick(pg.sprite.Sprite):
    def __init__(self, x=0, y=0, color=(255, 0, 0), health=2, brick_type='b'):
        types = {'r': 'red', 'w': 'white', 'b': 'black'}
        super().__init__()
        self.image = pg.image.load(
            os.path.join('assets', 'graphics', 'brick_{}.png'.format(types[brick_type]))).convert()
        self.dark = pg.image.load(os.path.join('assets', 'graphics', 'brick_{}.png'.format(types['b']))).convert()
        self.max_health = health
        self.health = health
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # self.color = [(0, 0, 0), color]

    def update(self):
        # darken_factor = numpy.interp(self.health, [1, self.max_health], [255, 100])
        # darker = pg.Surface(self.image.get_size()).convert_alpha()
        # darker.fill((0, 0, 0, darken_factor * 255))
        darken_factor = 255
        self.dark.set_alpha(darken_factor)

        self.image.blit(self.dark, (0, 0))


class Arrow(pg.sprite.Sprite):
    def __init__(self, second=False):
        super().__init__()
        self.image = pg.image.load(os.path.join('assets', 'graphics', 'arrow.png')).convert_alpha()
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
        self.image = pg.image.load(os.path.join('assets', 'graphics', 'title.png')).convert_alpha()
        self.image_clean = pg.image.load(os.path.join('assets', 'graphics', 'title.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (240, 220)
        self.animate = False
        self.shine = pg.Surface((20, self.rect.height))
        self.shine.fill((255, 255, 255))
        self.shine_pos = -20
        self.shine_timer = 0

    def update(self):
        if not self.shine_timer == 0:
            self.shine_timer -= time_passed
            if self.shine_timer < 0:
                self.shine_timer = 0
        else:
            if self.animate:
                if self.shine_pos == 0:
                    sound.sfx_lib.get('intro2').play()
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
            self.sheet = pg.image.load(os.path.join('assets', 'graphics', '{}.png'.format(filename))).convert_alpha()
        else:
            self.sheet = pg.image.load(os.path.join('assets', 'graphics', '{}.png'.format(filename))).convert()
        self.sprites = []
        for x in range(image_count):
            self.sprites.append(self.load_image(size, (size[0] * x, 0)))

    def load_image(self, size, pos):
        image = pg.Surface(size).convert_alpha()
        image.fill(bg_color)
        rect = image.get_rect()
        rect.x = pos[0]
        rect.y = pos[1]
        image.blit(self.sheet, (0, 0), rect)
        return image


class Message:
    def __init__(self, msg, sfx='normal'):
        self.timer = 2000
        self.color = config.TEXT_COLOR
        self.msg = msg.upper()
        self.highlight_clock = 0
        self.std_sfx = sfx

    def update(self):
        self.timer -= time_passed
        self.highlight_clock += time_passed
        if self.highlight_clock >= 50:
            self.color = tuple(numpy.subtract((255, 255, 255), self.color))
            self.highlight_clock = 0


def render_fading(screen, fade_step, invert_fading=0):
    # fade screen
    if invert_fading:
        alpha = abs(fade_step - 254)
    else:
        alpha = fade_step
    fading_surf = pg.Surface(screen.get_size(), pg.SRCALPHA)
    fade_color = bg_color
    alpha = 80 * round(alpha / 80)  # fades a bit rougher
    print('fading {} {}'.format(('out' if invert_fading else 'in'), alpha))
    fade_color.a = alpha
    fading_surf.fill(fade_color)
    screen.blit(fading_surf, (0, 0))
    # decrease fade_step until 0
    fade_step -= 10

    return fade_step


def render_hud(screen, hud_score, stage, lives, timer, highlight_combo=0):
    if timer <= 2000:
        # blink labels at beginning of game
        pass

    if highlight_combo:
        # 1 for black, 2 for white
        if highlight_combo > 1:
            color = (0, 0, 0)
        else:
            color = (255, 255, 255)
        score_text = font_16.render(str_r.get_str('combo').format(scores.get_combo()), True, color)
    else:
        score_text = font_16.render(str(hud_score), True, config.TEXT_COLOR)

    stage_text = font_16.render(stage, True, config.TEXT_COLOR)
    stage_pos = stage_text.get_rect()
    stage_pos.midtop = (screen.get_width() / 2, 8)
    screen.blit(stage_text, stage_pos)

    lives_text = font_16.render(str(lives), True, config.TEXT_COLOR)
    lives__text_pos = lives_text.get_rect()
    lives__text_pos.topright = (screen.get_width() - 28, 8)
    screen.blit(lives_text, lives__text_pos)

    pack = pg.image.load(os.path.join('assets', 'graphics', 'pack.png')).convert()
    screen.blit(pack, (screen.get_width() - 24, 8))

    score_pos = score_text.get_rect()
    score_pos.topleft = (8, 8)
    screen.blit(score_text, score_pos)


def render_falling_cigs(screen, offset):
    grid = (6, 5)
    x_off_step = int(screen.get_width() / grid[0])
    x_off = x_off_step
    y_off_step = int(screen.get_height() / grid[1])
    y_off = y_off_step
    for y in range(grid[1]):
        for x in range(grid[0]):
            cig = pg.image.load(os.path.join('assets', 'graphics', 'paddle_m.png')).convert()
            cig = pg.transform.rotate(cig, -90)
            screen.blit(cig, (x_off, y_off))
            x_off += x_off_step
        x_off = x_off_step
        y_off += y_off_step

    return offset


def update_highlight_text(scene):
    if scene.ready_to_play:
        scene.highlight_clock += time_passed
        if scene.highlight_clock >= 100:
            scene.highlight_color = tuple(numpy.subtract((255, 255, 255), scene.highlight_color))
            scene.highlight_clock = 0
    else:
        scene.highlight_clock += time_passed
        if scene.highlight_clock >= 500:
            scene.highlight_clock = 0
            scene.draw_coin_text = not scene.draw_coin_text

    if coins.get_credit() > 0:
        scene.ready_to_play = True
        scene.draw_coin_text = True
        scene.coin_text = str_r.get_str('start') if coins.get_credit() > 0 else str_r.get_str('coin')


def render_coin_text(scene, screen, y_pos=0.7):
    if scene.draw_coin_text:
        insert_coin = font_16.render(scene.coin_text, True, scene.highlight_color)
        pos_insert = insert_coin.get_rect()
        pos_insert.center = (screen.get_rect().centerx, screen.get_rect().height * y_pos)
        screen.blit(insert_coin, pos_insert)


def render_credit(scene, screen):
    if scene.draw_credit and coins.get_credit():
        credit = font_16.render(scene.credit_text.format(coins.get_credit()), True, config.TEXT_COLOR)
        pos_credit = credit.get_rect()
        pos_credit.midtop = (screen.get_width() / 2, screen.get_height() * 0.96)
        screen.blit(credit, pos_credit)


def render_heartattack(scene, screen):
    heart_bg = pg.Surface((config.WIDTH, config.HEIGHT)).convert_alpha()
    if scene.heartattack_mode == 'killing':
        scene.heart_beat += 1
        if scene.heart_beat >= 4:
            scene.heart_beat = 0
            scene.heart_color = tuple(numpy.subtract((255, 255, 255), scene.heart_color))
    elif scene.heartattack_mode == 'ready':
        scene.heart_fade += 4 * scene.heart_fade_inv
        if not 0 < scene.heart_fade < 255:
            scene.heart_fade_inv *= -1
            scene.heart_fade += 4 * scene.heart_fade_inv
        scene.heart_color.a = 80 * round(scene.heart_fade / 80)

    heart_bg.fill(bg_color)
    heart_bg.fill(scene.heart_color)
    screen.blit(heart_bg, (0, 0))


def center_to(center_surface, surface):
    """will return the position needed to set surface to the center of center_surface"""
    pos = surface.get_rect()
    pos.center = center_surface.get_rect().center
    return pos


def y_center_to(center_surface, surface):
    """will return the position needed to set surface to the vertical center of center_surface"""
    pos = surface.get_rect()
    pos.centery = center_surface.get_rect().centery
    return pos.y


def x_center_to(center_surface, surface):
    """will return the position needed to set surface to the horizontal center of center_surface"""
    pos = surface.get_rect()
    pos.centerx = center_surface.get_rect().centerx
    return pos.x


def quit_game():
    pg.display.quit()
    sys.exit()


def main():
    global time_passed
    pg.init()
    screen = pg.display.set_mode(config.DISPLAY, config.FLAGS, config.DEPTH)
    pg.mouse.set_visible(False)
    pg.display.set_caption(config.CAPTION)
    clock = pg.time.Clock()
    running = True

    global font_8
    global font_16
    global font_24
    font_8 = pg.font.Font(config.FONT, 8)
    font_16 = pg.font.Font(config.FONT, 16)
    font_24 = pg.font.Font(config.FONT, 24)

    manager = SceneManager()

    while running:
        time_passed = clock.tick(config.FRAMERATE)

        if pg.event.get(pg.QUIT):
            running = False
            return

        events = pg.event.get()
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_1:
                    coins.add_coin()
            if e.type == pg.JOYBUTTONDOWN:
                if e.button == ctrls.INSERT_COIN:
                    coins.add_coin()

        manager.scene.handle_events(events)
        manager.scene.update()
        manager.scene.render(screen)
        if config.SHOW_FPS:
            fps = font_8.render(str(int(clock.get_fps())), True, config.DEBUG_COLOR)
            screen.blit(fps, (0, 0))
        pg.display.flip()

    quit_game()


if __name__ == "__main__":
    main()
