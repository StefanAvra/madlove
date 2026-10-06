"""The title screen."""

import pygame as pg

from madlove import audio, config, hud
from madlove import strings as str_r
from madlove.scenes import base, credits, highscores, intro, menu
from madlove.sprites.decor import Arrow, Title


class TitleScene(base.Scene):
    def __init__(self, game):
        super().__init__(game)
        # self.line1 = self.game.font_24.render(config.GAME_TITLE, True, config.TEXT_COLOR)
        self.line2 = self.game.font_16.render(config.GAME_SUBTITLE, True, config.TEXT_COLOR)
        self.cprght = self.game.font_8.render(str_r.get_str('copyright'), True, config.TEXT_COLOR)
        self.coin_text = str_r.get_str('start') if self.game.wallet.credit > 0 else str_r.get_str('coin')
        self.draw_coin_text = True
        self.credit_text = str_r.get_str('credit')
        self.draw_credit = False
        self.ready_to_play = False
        # self.menu = menu.get_entries('titlescreen')
        # self.menu_funcs = menu.get_funcs('titlescreen')
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
        audio.load_music('titlescreen')
        # audio.play_music(-1)
        audio.play_sfx('intro1')

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
                cig.image = pg.image.load(config.asset('graphics', 'paddle_m.png')).convert()
                cig.image = pg.transform.rotate(cig.image, -90)
                cig.rect = cig.image.get_rect()
                cig.rect.midtop = (cig_offset[0] * x + 48, cig_offset[1] * y)
                self.cigs.add(cig)

    def render(self, screen):
        screen.fill(config.BG_COLOR)
        if self.draw_cigs:
            self.cigs.draw(screen)
        if self.bg_arrow.active:
            screen.blit(self.bg_arrow.image, self.bg_arrow.rect)
        # pos_line1 = hud.center_to(screen, self.line1)
        # pos_line1 = (pos_line1[0], pos_line1[1] - 24)
        pos_line2 = hud.center_to(screen, self.line2)
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
        #             self.highlight_color = utils.invert_color(self.highlight_color)
        #             self.highlight_clock = 0
        #         color = self.highlight_color
        #     else:
        #         color = config.TEXT_COLOR
        #     entry_surf = self.game.font_16.render(entry, True, color)
        #     entry_pos = (hud.x_center_to(screen, entry_surf), 400 + idx * menu.MENU_LINE_OFFSET)
        #     screen.blit(entry_surf, entry_pos)

        if self.blit_elements[2]:
            hud.render_coin_text(self, screen)
        if self.blit_elements[0]:
            screen.blit(self.title.image, self.title.rect)

        hud.render_credit(self, screen)

        screen.blit(self.arrow.image, self.arrow.rect)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1)

    def update(self):
        self.timer += self.game.dt
        if self.timer > 30000 and not self.fade_leave_to:
            self.fadeout_step = 255
            self.fade_leave_to = 2
        if self.fade_leave_to and self.fadeout_step <= 0:
            if self.fade_leave_to == 1:
                # self.manager.go_to(play.GameScene(self.game, 0))
                self.manager.go_to(intro.IntroScene(self.game, 0))
            if self.fade_leave_to == 2:
                self.manager.go_to(highscores.HighscoreScene(self.game, previous_scene=self))
            if self.fade_leave_to == 3:
                self.manager.go_to(TitleScene(self.game))

        hud.update_highlight_text(self)

        self.title.update(self.game.dt)
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
                                if not audio.music_busy():
                                    audio.play_music(1)

                                    self.wait_for_music = False
        if self.bg_arrow.active:
            self.bg_arrow.update()
            if self.bg_arrow.done:
                self.title.animate = True
        if not audio.music_busy() and not self.wait_for_music and not self.fade_leave_to:
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

        if self.game.settings.free_mode:
            self.game.wallet.give_free_credit()

    def handle_events(self, events):
        if not self.fade_leave_to:
            for e in events:
                if e.type == pg.JOYBUTTONDOWN:
                    if e.button == 0:
                        if self.ready_to_play:
                            audio.play_sfx('select')

                            self.game.wallet.consume_coin()
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
                    #         audio.play_sfx('menu_nav')
                    #         self.cursor -= 1
                    #         if self.cursor < 0:
                    #             self.cursor = len(self.menu) - 1
                    #     if e.value > 0:
                    #         audio.play_sfx('menu_nav')
                    #         self.cursor += 1
                    #         if self.cursor >= len(self.menu):
                    #             self.cursor = 0
                    pass

                if e.type == pg.KEYDOWN:
                    if e.key in [pg.K_SPACE, pg.K_RETURN]:
                        if self.ready_to_play:
                            audio.play_sfx('select')

                            self.game.wallet.consume_coin()
                            self.fadeout_step = 255
                            self.fade_leave_to = 1
                            # f = self.menu_funcs[self.cursor]
                            # if f == 'start':
                            #     self.fade_leave_to = 1
                            # elif f == 'scores':
                            #     self.fade_leave_to = 2
                            # elif f == 'credits':
                            #     pass
                    if e.key == pg.K_c:
                        self.manager.go_to(credits.CreditsScene(self.game, 0))
                    if e.key == pg.K_ESCAPE:
                        self.manager.go_to(menu.OverlayMenuScene(self.game, self, 'exit'))
                    if e.key == pg.K_h:
                        self.manager.go_to(highscores.HighscoreScene(self.game))
                    # if e.key == pg.K_DOWN:
                    #     audio.play_sfx('menu_nav')
                    #     self.cursor += 1
                    #     if self.cursor >= len(self.menu):
                    #         self.cursor = 0
                    # if e.key == pg.K_UP:
                    #     audio.play_sfx('menu_nav')
                    #     self.cursor -= 1
                    #     if self.cursor < 0:
                    #         self.cursor = len(self.menu) - 1
