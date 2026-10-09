"""The high-score list."""

import pygame as pg

from madlove import audio, config, hud, utils
from madlove import strings as str_r
from madlove.scenes import base, credits, intro, title


class HighscoreScene(base.Scene):
    def __init__(self, game, mode='show', previous_scene=None, highlight_place=None):
        super().__init__(game)
        self.game.highscores.load()
        self.lines = []
        self.previous_scene = previous_scene
        self.highlight_place = highlight_place
        self.highlight_place_clock = 0
        self.title = self.game.font_16.render(str_r.get_str('highscores_title'), True, config.TEXT_COLOR)
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
        self.coin_text = str_r.get_str('start') if self.game.wallet.credit > 0 else str_r.get_str('coin')
        self.highlight_clock = 0
        self.highlight_color = config.TEXT_COLOR
        self.draw_credit = True if mode == 'show' else False
        self.credit_text = str_r.get_str('credit')

    def render(self, screen):

        screen.fill(config.BG_COLOR)
        title_pos = self.title.get_rect()
        title_pos.center = (screen.get_width() / 2, screen.get_height() * 0.1)
        screen.blit(self.title, title_pos)
        self.lines = []
        place = 0
        for highscore in self.game.highscores.entries:
            place += 1
            new_line = f'{place:<2}   {highscore.name:<8} {highscore.score:>10}'
            if self.mode == 'gameover' and place == self.highlight_place:
                self.lines.append(self.game.font_16.render(new_line, True, self.highlight_color))
            else:
                self.lines.append(self.game.font_16.render(new_line, True, config.TEXT_COLOR))
        for idx, line in enumerate(self.lines[: self.print_step]):
            screen.blit(line, (50, 150 + (40 * idx)))

        if self.mode == 'show':
            hud.render_coin_text(self, screen, y_pos=0.9)

        hud.render_credit(self, screen)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0, self.game.steps)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1, self.game.steps)

    def update(self):
        if self.print_step < 10:
            self.clock += self.game.dt
            if self.clock >= 100:
                self.clock = 0
                self.print_step += 1
        elif self.mode in ['show', 'gameover']:
            self.leave_timer -= self.game.dt
            if self.leave_timer < 0 and not self.leaving:
                self.fadeout_step = 255
                self.fade_leave_to = True
                self.leaving = True

        if self.fade_leave_to and self.fadeout_step <= 0:
            if self.mode == 'gameover':
                self.manager.go_to(credits.CreditsScene(self.game, 0))
            else:
                if self.fade_leave_to == 'game':
                    self.manager.go_to(intro.IntroScene(self.game, 0))
                elif self.previous_scene:
                    self.previous_scene.fade_leave_to = False
                    self.previous_scene.timer = 0
                    self.previous_scene.fadein_step = 255
                    self.previous_scene.title.restart_animation(timer=2000)
                    self.manager.go_to(self.previous_scene)
                else:
                    self.manager.go_to(title.TitleScene(self.game))

        if self.mode == 'show':
            hud.update_highlight_text(self)

        if self.mode == 'gameover':
            self.highlight_place_clock += self.game.dt
            if self.highlight_place_clock >= 400:
                self.highlight_color = utils.invert_color(self.highlight_color)
                self.highlight_place_clock = 0

        if self.game.settings.free_mode:
            self.game.wallet.give_free_credit()

    def handle_events(self, events):
        for e in events:
            if not self.fade_leave_to:
                if e.type == pg.JOYBUTTONDOWN:
                    if e.button == 0:
                        if self.ready_to_play:
                            audio.play_sfx('select')
                            self.game.wallet.consume_coin()
                            self.fadeout_step = 255
                            self.fade_leave_to = 'game'

                if e.type == pg.KEYDOWN:
                    if self.ready_to_play:
                        if e.key in [pg.K_SPACE, pg.K_RETURN]:
                            audio.play_sfx('select')
                            self.game.wallet.consume_coin()
                            self.fadeout_step = 255
                            self.fade_leave_to = 'game'
                    if e.key == pg.K_1:
                        # self.game.wallet.add_coin()
                        pass
                    if e.key == pg.K_ESCAPE:
                        self.fadeout_step = 255
                        self.fade_leave_to = True
