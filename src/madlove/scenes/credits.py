"""The credits."""

import pygame as pg

from madlove import config, hud
from madlove import strings as str_r
from madlove.scenes import base, title


class CreditsScene(base.Scene):
    def __init__(self, game, view_no):
        super().__init__(game)
        self.views = str_r.get_credits()
        self.view_idx = view_no
        self.next_view_timer = 0
        self.fadein_step = 255
        self.fadeout_step = 0
        self.leave = False
        self.leave_to_title = False

    def render(self, screen):
        screen.fill(config.BG_COLOR)
        line_height = 30
        view_height = line_height * len(self.views[self.view_idx].splitlines())
        view_surf = pg.Surface((config.WIDTH, view_height))
        view_surf.fill(config.BG_COLOR)
        view_rect = view_surf.get_rect()
        for idx, line in enumerate(self.views[self.view_idx].splitlines()):
            text_surf = self.game.font_16.render(line, True, config.TEXT_COLOR)
            text_pos = text_surf.get_rect()
            text_pos.centerx = view_rect.centerx
            text_pos.y = line_height * idx
            view_surf.blit(text_surf, text_pos)
        view_rect.center = screen.get_rect().center
        screen.blit(view_surf, view_rect)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1)

    def update(self):
        if self.fadeout_step <= 0 and self.fadein_step <= 0 and not self.leave:
            self.next_view_timer += self.game.dt
            if self.next_view_timer > 3000:
                self.fadeout_step = 255
                self.leave = True
                if self.view_idx + 1 >= len(self.views):
                    self.leave_to_title = True

        if self.leave and self.fadeout_step <= 0:
            if self.leave_to_title:
                self.manager.go_to(title.TitleScene(self.game))
            else:
                self.manager.go_to(CreditsScene(self.game, self.view_idx + 1))

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button in [0, 1]:
                    self.next_view_timer += 3000
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    self.next_view_timer += 3000
