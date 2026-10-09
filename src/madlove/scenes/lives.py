"""Losing a life, the continue countdown, and paying for more lives."""

import pygame as pg

from madlove import audio, config, hud, scores, utils
from madlove import strings as str_r
from madlove.scenes import base, game_over, menu


class LostLifeScene(base.Scene):
    def __init__(self, game, game_scene):
        super().__init__(game)
        self.game_scene = game_scene
        self.game.wallet.lose_life()
        self.game_scene.lost_life = True
        self.game_over = False
        audio.stop_music()

        if self.game.wallet.lives <= 0:
            audio.play_sfx('game_over')

            self.lost_text = str_r.get_str('zero_lives').splitlines()
            self.game_over = True
            self.fadeout_step = 255
            self.game_over_timer = 4000
            print('out of cigs')
        else:
            audio.play_sfx('lost_life')

            self.lost_text = str_r.get_str('lost_life').splitlines()
            print('lost a life')
            self.fadeout_step = 0
        text_surf_x, text_surf_y = menu.PADDING * 2, menu.PADDING * 2
        text_surf_y += menu.MENU_LINE_OFFSET * len(self.lost_text) - menu.MENU_LINE_OFFSET / 2
        text_surf_x += 16 * len(max(self.lost_text, key=len))
        self.text_bg_surf = pg.Surface((text_surf_x, text_surf_y))
        self.text_bg_shadow = pg.Surface((self.text_bg_surf.get_rect().width, self.text_bg_surf.get_rect().height))

    def render(self, screen):
        # if not self.game_over:
        self.text_bg_surf.fill(config.BG_COLOR)
        self.text_bg_shadow.fill(config.MENU_SHADOW_COLOR)
        for idx, line in enumerate(self.lost_text):
            lost_line_surf = self.game.font_16.render(line, True, config.TEXT_COLOR)
            lost_line_pos = lost_line_surf.get_rect()
            lost_line_pos.center = (screen.get_rect().centerx, screen.get_rect().centery + 100 + idx * menu.PADDING)
            lost_line_pos = (
                hud.x_center_to(self.text_bg_surf, lost_line_surf),
                menu.PADDING + idx * menu.MENU_LINE_OFFSET,
            )
            self.text_bg_surf.blit(lost_line_surf, lost_line_pos)

        text_bg_pos = hud.center_to(screen, self.text_bg_surf)
        text_bg_shadow_pos = (text_bg_pos[0] + config.MENU_SHADOW_OFFSET, text_bg_pos[1] + config.MENU_SHADOW_OFFSET)

        screen.blit(self.text_bg_shadow, text_bg_shadow_pos)
        screen.blit(self.text_bg_surf, text_bg_pos)

        if self.fadeout_step > 0 >= self.game_over_timer:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1, self.game.steps)

    def update(self):
        if self.game_over:
            if self.game_over_timer > 0:
                self.game_over_timer -= self.game.dt
            else:
                if self.fadeout_step <= 0:
                    self.manager.go_to(ContinueScene(self.game, self.game_scene))

    def handle_events(self, events):
        if not self.game_over:
            for e in events:
                if e.type == pg.JOYBUTTONDOWN:
                    if e.button in [0, 1]:
                        self.game_scene.reset_round()
                        self.go_back()
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_SPACE:
                        self.game_scene.reset_round()
                        self.go_back()
                    if e.key == pg.K_ESCAPE:
                        pass

    def go_back(self):
        audio.unpause_music()
        self.manager.go_to(self.game_scene)


class ContinueScene(base.Scene):
    def __init__(self, game, game_scene):
        super().__init__(game)
        self.game_scene = game_scene
        # self.lives_left = self.game.wallet.lives
        self.game_over = False
        self.countdown_timer = 10000
        self.countdown = int(self.countdown_timer / 1000)
        self.countdown_active = False if self.game.wallet.credit > 0 else True
        self.no_countdown = not self.countdown_active or self.game.settings.free_mode
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

        if audio.music_busy():
            audio.stop_music()

    def render(self, screen):
        screen.fill(config.BG_COLOR)

        if not self.no_countdown:
            for idx, line in enumerate(self.countdown_text):
                text_surf = self.game.font_16.render(line, True, config.TEXT_COLOR)
                text_rect = text_surf.get_rect()
                text_rect.center = (screen.get_rect().centerx, 150 + idx * menu.PADDING)
                screen.blit(text_surf, text_rect)
            counter = self.game.font_24.render(str(self.countdown), True, self.countdown_color)
            counter_pos = counter.get_rect()
            counter_pos.center = screen.get_rect().center
            screen.blit(counter, counter_pos)

        if self.game.wallet.credit == 0:
            hud.render_coin_text(self, screen)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0, self.game.steps)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1, self.game.steps)

    def update(self):
        if self.fade_leave_to is None:
            if self.game_over or self.game.settings.free_mode:
                self.fadeout_step = 255
                self.fade_leave_to = 'gameover'
            else:
                if self.game.wallet.credit > 0:
                    self.fadeout_step = 255
                    self.countdown_active = False
                    self.fade_leave_to = 'consume_coin'
                else:
                    self.countdown_active = True
            if self.countdown_active and self.fadein_step <= 0:
                if self.countdown_timer < 4000:
                    self.highlight_clock += self.game.dt
                    if self.highlight_clock >= 100:
                        self.highlight_clock = 0
                        self.countdown_color = utils.invert_color(self.countdown_color)
                if self.countdown_timer > 0:
                    self.countdown_timer -= self.game.dt
                else:
                    self.game_over = True
                if not self.countdown == int(self.countdown_timer / 1000):
                    self.countdown = int(self.countdown_timer / 1000)
                    audio.play_sfx('countdown')
        elif self.fadeout_step <= 0:
            if self.fade_leave_to == 'gameover':
                self.manager.go_to(game_over.GameOver(self.game, self.game_scene))
            if self.fade_leave_to == 'consume_coin':
                self.manager.go_to(ConsumeCoinScene(self.game, self.game_scene))

        self.coin_text_clock += self.game.dt
        if self.coin_text_clock >= 400:
            self.draw_coin_text = not self.draw_coin_text
            self.coin_text_clock = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE]:
                    self.countdown_timer -= 1000


class ConsumeCoinScene(base.Scene):
    def __init__(self, game, game_scene):
        super().__init__(game)
        self.game_scene = game_scene
        self.penalty = 0
        self.consume_coins_text = str_r.get_str('consume_coins').splitlines()
        self.consume_coins = False
        self.consume_coins_values = [self.game.score, self.penalty, self.game.wallet.credit, self.game.wallet.lives]
        self.blit_elements = [False] * 4
        self.blit_timer = 0
        self.score_timer = 0
        self.points_done = False
        self.cigs_bought = False
        self.fadeout_step = 0
        self.fadein_step = 0
        self.leave = False
        self.convert_step = 0
        self.game_scene.no_continue = False

    def render(self, screen):
        screen.fill(config.BG_COLOR)
        lines = []
        for idx, line in enumerate(self.consume_coins_text):
            new_line = f'{line:<10} {self.consume_coins_values[idx]:>13}'
            text_surf = self.game.font_16.render(new_line, True, config.TEXT_COLOR)
            text_pos = text_surf.get_rect()
            text_pos.topleft = (50, 150 + (40 * idx))
            lines.append((text_surf, text_pos))

        for idx, blit in enumerate(self.blit_elements):
            if blit:
                screen.blit(lines[idx][0], lines[idx][1])

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0, self.game.steps)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1, self.game.steps)

    def update(self):
        self.consume_coins_values = [self.game.score, self.penalty, self.game.wallet.credit, self.game.wallet.lives]
        self.blit_timer += self.game.dt
        if self.blit_timer >= 100:
            self.blit_timer = 0
            if False in self.blit_elements:
                self.blit_elements.insert(0, True)
                self.blit_elements.remove(False)

        if False not in self.blit_elements:
            self.score_timer += self.game.dt
            if not self.cigs_bought:
                if self.score_timer >= 1000:
                    self.cigs_bought = True
                    self.game.wallet.consume_coin()
                    audio.play_sfx('coin')
                    self.penalty, self.convert_step = scores.get_penalty(self.game.score)
            elif not self.points_done:
                if self.score_timer >= 2000:
                    # convert_step = 10
                    self.game.score -= self.convert_step
                    if self.game.score < 0:
                        self.game.score = 0
                    self.penalty += self.convert_step
                    if self.penalty >= 0:
                        self.penalty = 0
                        self.points_done = True
                        self.score_timer = 0
                    audio.play_sfx('point')
            else:
                if self.score_timer >= 2000 and not self.leave:
                    self.fadeout_step = 255
                    self.leave = True
                if self.leave and self.fadeout_step <= 0:
                    self.game_scene.reset_round()
                    self.manager.go_to(self.game_scene)

    def handle_events(self, events):
        pass
