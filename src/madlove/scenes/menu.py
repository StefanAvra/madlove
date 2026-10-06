"""Menus drawn over another scene, like the smoke break."""

import pygame as pg

from madlove import audio, config, hud, utils
from madlove.scenes import base
from madlove.sprites.decor import Ashtray

PADDING = 24
HEADER_SIZE = 40
MENU_LINE_OFFSET = 24


def get_entries(menu_type):
    entries = {
        'exit': ['NO', 'YES'],
        'ingame-exit': ['CONTINUE', 'GIVE UP'],
        'titlescreen': ['START', 'HIGHSCORES', 'CREDITS'],
    }
    return entries.get(menu_type)


def get_title(menu_type):
    titles = {'exit': 'EXIT GAME?', 'ingame-exit': 'PAUSE', 'pause': 'SMOKE BREAK'}
    return titles.get(menu_type)


def get_funcs(menu_type):
    funcs = {
        'exit': ['back', 'quit'],
        'ingame-exit': ['back', 'quit'],
        'titlescreen': ['start', 'scores', 'credits'],
        'pause': ['back'],
    }
    return funcs.get(menu_type)


def get_surf(menu_type):
    x, y = PADDING * 2, PADDING * 2
    y += HEADER_SIZE
    if menu_type != 'pause':
        y += MENU_LINE_OFFSET * len(get_entries(menu_type)) - MENU_LINE_OFFSET / 2
        lines = get_entries(menu_type)
        lines.append(get_title(menu_type))
        x += 16 * len(max(lines, key=len))
    else:
        x += 208
        y += 162  # ashtray size

    return pg.Surface((x, y))


def make_outline(surface, fill_color, outline_color=config.TEXT_COLOR, border=4):
    surface.fill(outline_color)
    surface.fill(fill_color, surface.get_rect().inflate(-border, -border))


class OverlayMenuScene(base.Scene):
    def __init__(self, game, paused_scene, menu_type):
        super().__init__(game)
        self.menu_type = menu_type
        self.menu_entries = get_entries(menu_type)
        self.menu_surf = get_surf(menu_type)
        self.menu_drop_shadow = pg.Surface((self.menu_surf.get_rect().width, self.menu_surf.get_rect().height))
        self.menu_title = get_title(menu_type)
        self.menu_funcs = get_funcs(menu_type)
        self.paused_scene = paused_scene
        self.cursor = 0
        self.highlight_clock = 0
        self.highlight_color = config.MENU_COLOR_HIGHLIGHT
        self.animation_clock = 0
        self.music_timer = 0
        audio.pause_music()
        if self.menu_type == 'pause':
            audio.play_sfx('pause_in')
            self.animation = Ashtray()
            audio.load_music('smoke_break')

    def render(self, screen):

        self.highlight_clock += self.game.dt
        # make_outline(self.menu_surf, config.BG_COLOR)
        self.menu_surf.fill(config.BG_COLOR)
        self.menu_drop_shadow.fill(config.MENU_SHADOW_COLOR)
        menu_pos = hud.center_to(screen, self.menu_surf)
        shadow_pos = (menu_pos[0] + config.MENU_SHADOW_OFFSET, menu_pos[1] + config.MENU_SHADOW_OFFSET)
        title = self.game.font_16.render(self.menu_title, True, config.TEXT_COLOR)
        title_pos = (hud.x_center_to(self.menu_surf, title), PADDING)
        self.menu_surf.blit(title, title_pos)

        if self.menu_type != 'pause':
            for idx, entry in enumerate(self.menu_entries):
                if self.cursor == idx:
                    if self.highlight_clock >= 100:
                        self.highlight_color = utils.invert_color(self.highlight_color)
                        self.highlight_clock = 0
                    color = self.highlight_color
                else:
                    color = config.TEXT_COLOR
                entry_surf = self.game.font_16.render(entry, True, color)
                entry_pos = (
                    hud.x_center_to(self.menu_surf, entry_surf),
                    PADDING + HEADER_SIZE + idx * MENU_LINE_OFFSET,
                )
                self.menu_surf.blit(entry_surf, entry_pos)
        else:
            animation_pos = (hud.x_center_to(self.menu_surf, self.animation.image), PADDING + HEADER_SIZE)
            self.menu_surf.blit(self.animation.image, animation_pos)

        screen.blit(self.menu_drop_shadow, shadow_pos)
        screen.blit(self.menu_surf, menu_pos)

    def update(self):
        self.music_timer += self.game.dt
        if not audio.music_busy() and self.music_timer >= 1000:
            audio.play_music(-1)
        if self.menu_type == 'pause':
            self.animation_clock += self.game.dt
            if self.animation_clock >= 100:
                self.animation.update()
                self.animation_clock = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button in [0, 1]:
                    self.choose()
            if self.menu_type != 'pause':
                if e.type == pg.JOYAXISMOTION:
                    if e.axis == 1:
                        if e.value < 0:
                            audio.play_sfx('menu_nav')
                            self.cursor -= 1
                            if self.cursor < 0:
                                self.cursor = len(self.menu_entries) - 1
                        if e.value > 0:
                            audio.play_sfx('menu_nav')
                            self.cursor += 1
                            if self.cursor >= len(self.menu_entries):
                                self.cursor = 0

            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE, pg.K_RETURN]:
                    self.choose()
                if e.key == pg.K_ESCAPE:
                    self.go_back()
                if self.menu_type != 'pause':
                    if e.key == pg.K_DOWN:
                        audio.play_sfx('menu_nav')
                        self.cursor += 1
                        if self.cursor >= len(self.menu_entries):
                            self.cursor = 0
                    if e.key == pg.K_UP:
                        audio.play_sfx('menu_nav')
                        self.cursor -= 1
                        if self.cursor < 0:
                            self.cursor = len(self.menu_entries) - 1

    def choose(self):
        """runs the menu entry under the cursor"""
        action = self.menu_funcs[self.cursor]
        if action == 'back':
            self.go_back()
        elif action == 'quit':
            pg.event.post(pg.event.Event(pg.QUIT))  # the main loop stops at the next frame

    def go_back(self):
        audio.stop_music()
        audio.play_sfx('pause_out')
        audio.load_music('bgm')
        audio.play_music(-1)
        self.manager.go_to(self.paused_scene)
