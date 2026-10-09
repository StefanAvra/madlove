"""The smoking fact shown before each level."""

import pygame as pg

from madlove import audio, config, hud
from madlove.scenes import base, play

PHOTO_POS = (7, 191)  # the photo, on black under the fact's text
LOGO_TOP = 416  # the pack's logo below it, made like the title screen's
TITLE_POS = (68, 423)


def intro_image(number):
    """the screen behind the fact: the level intro's photo above the pack's logo"""
    image = pg.Surface(config.DISPLAY).convert()
    image.fill((0, 0, 0))
    image.blit(pg.image.load(config.asset('graphics', f'level_intro_{number}.png')).convert(), PHOTO_POS)
    image.fill(config.BG_COLOR, (0, LOGO_TOP, config.WIDTH, config.HEIGHT - LOGO_TOP))
    image.blit(pg.image.load(config.asset('graphics', 'arrow.png')).convert_alpha(), (0, LOGO_TOP))
    image.blit(pg.image.load(config.asset('graphics', 'title.png')).convert_alpha(), TITLE_POS)
    return image


class IntroScene(base.Scene):
    # should be called before the next level/play.GameScene()
    def __init__(self, game, next_lvl):
        super().__init__(game)
        self.next_lvl = next_lvl
        self.text = self.game.facts.next()
        self.text_cursor = 0
        self.intro = intro_image(self.game.next_intro())
        self.timer = 0
        self.text_cursor_speed = 40
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave = False
        self.delay_done = False
        audio.stop_music()

    def render(self, screen):
        # screen.fill(config.BG_COLOR)
        screen.blit(self.intro, (0, 0))
        fact_offset = 0
        for text in self.text[: self.text_cursor].split('\n'):
            fact = self.game.font_16.render(text, True, config.MENU_COLOR_HIGHLIGHT)
            screen.blit(fact, (8, 8 + fact_offset))
            fact_offset += 24

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1)

    def update(self):
        self.timer += self.game.dt
        if self.timer > 700:
            self.delay_done = True
        if self.delay_done:
            if self.text_cursor < len(self.text):
                if self.timer >= self.text_cursor_speed:
                    self.timer = 0
                    self.text_cursor += 1
                    audio.play_sfx('text')
            elif not self.fade_leave and self.timer > 3000:
                self.fade_leave = True
                self.fadeout_step = 255
            if self.fade_leave and self.fadeout_step <= 0:
                self.manager.go_to(play.GameScene(self.game, self.next_lvl))

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
