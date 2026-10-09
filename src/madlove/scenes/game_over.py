"""Game over and entering a name for the high-score list."""

import pygame as pg

from madlove import audio, config, hud
from madlove import controls as ctrls
from madlove import strings as str_r
from madlove.scenes import base, highscores, play


class GameOver(base.Scene):
    def __init__(self, game, game_scene):
        super().__init__(game)
        self.game.highscores.load()  # make sure to load actual highscores
        self.score = self.game.score
        self.game.score = 0
        self.reached_lvl = game_scene.level_data.no + 1
        self.reached_stage = game_scene.current_stage
        self.game_over_text = 'GAME OVER'
        self.place, self.place_no = self.game.highscores.place(self.score)
        self.is_highscore = self.place_no <= 10
        self.blit_elements = [False] * 5
        self.timer = 0
        self.alphabet = str_r.get_alphabet()
        self.cursor = 0
        self.alphabet_pointer = self.alphabet.index(' ')
        self.cursor_clock = 0
        self.cursor_color = config.MENU_COLOR_HIGHLIGHT
        self.blit_cursor = False
        self.name = list('        ')
        self.name_input_active = self.is_highscore
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave = False
        self.char_timer = 0
        self.char_timer_threshold = 0
        if self.place_no == 1:
            audio.load_music('1stplace')
        else:
            audio.load_music('smoke_break')
        audio.play_music(-1)

    def render(self, screen):
        screen.fill(config.BG_COLOR)
        # todo: make game over text wave
        game_over_surf = self.game.font_24.render(self.game_over_text, True, config.TEXT_COLOR)
        game_over_rect = game_over_surf.get_rect()
        game_over_rect.center = (screen.get_width() / 2, screen.get_height() * 0.1)
        screen.blit(game_over_surf, game_over_rect)
        y_offset = game_over_rect.center[1] + 146
        f_line = '{:<13} {:>10}'
        if self.blit_elements[0]:
            # level = self.game.font_16.render(f'YOU REACHED LEVEL {self.reached_lvl}', True, config.TEXT_COLOR)
            level = self.game.font_16.render(
                f_line.format(str_r.get_str('reached_level'), self.reached_lvl), True, config.TEXT_COLOR
            )
            level_pos = level.get_rect()
            level_pos.topleft = (50, y_offset)
            screen.blit(level, level_pos)
            y_offset += level_pos.height * 2
        if self.blit_elements[1]:
            # stage = self.game.font_16.render(f'CANCER STAGE {stages[self.reached_stage]}' if self.reached_stage > 0
            #                        else stages[self.reached_stage], True, config.TEXT_COLOR)
            stage = self.game.font_16.render(
                f_line.format(str_r.get_str('cancer_stage'), play.stages[self.reached_stage]), True, config.TEXT_COLOR
            )
            stage_pos = stage.get_rect()
            stage_pos.topleft = (50, y_offset)
            screen.blit(stage, stage_pos)
            y_offset += stage_pos.height * 2
        if self.blit_elements[2]:
            your_score = self.game.font_16.render(
                f_line.format(str_r.get_str('end_score'), self.score), True, config.TEXT_COLOR
            )
            your_score_pos = your_score.get_rect()
            # your_score_pos.center = (screen.get_width() / 2, y_offset)
            your_score_pos.topleft = (50, y_offset)
            screen.blit(your_score, your_score_pos)
            y_offset += your_score_pos.height * 3
        # if self.blit_elements[3]:
        #     score_surf = self.game.font_16.render(str(self.score), True, config.TEXT_COLOR)
        #     score_pos = score_surf.get_rect()
        #     score_pos.center = (screen.get_width() / 2, y_offset)
        #     screen.blit(score_surf, score_pos)
        #     y_offset += score_pos.height * 3
        if self.is_highscore:
            if self.blit_elements[3]:
                # place = self.game.font_16.render(f'CONGRATULATIONS!'
                #                        f'YOU ARE ON {self.place} PLACE!', True, config.TEXT_COLOR)
                congrats_lines = str_r.get_str('congrats').splitlines()
                y_offset_congrats = 72
                for line in congrats_lines:
                    place = self.game.font_16.render(line.format(self.place), True, config.TEXT_COLOR)
                    place_pos = place.get_rect()
                    # place_pos.center = (screen.get_width() / 2, y_offset)
                    place_pos.center = (screen.get_width() / 2, game_over_rect.center[1] + y_offset_congrats)
                    screen.blit(place, place_pos)
                    y_offset_congrats += place_pos.height * 2
                    y_offset += place_pos.height * 2
            if self.blit_elements[4]:
                # name = self.game.font_16.render(f'ENTER NAME: {"".join(self.name)}', True, config.TEXT_COLOR)
                name = self.game.font_16.render(
                    f_line.format(str_r.get_str('enter_name'), ''.join(self.name)), True, config.TEXT_COLOR
                )
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
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0, self.game.steps)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1, self.game.steps)

    def update(self):
        if False in self.blit_elements:
            self.timer += self.game.dt
            if self.timer >= 200:
                self.timer = 0
                self.blit_elements.insert(0, True)
                self.blit_elements.remove(False)
        else:
            if self.name_input_active:
                self.cursor_clock += self.game.dt
                if self.cursor_clock >= 200:
                    self.cursor_clock = 0
                    self.blit_cursor = not self.blit_cursor
            elif self.fade_leave and self.fadeout_step <= 0:
                if self.place_no == 1:
                    audio.load_music('smoke_break')
                    audio.play_music(-1)

                self.manager.go_to(highscores.HighscoreScene(self.game, highlight_place=self.place_no, mode='gameover'))
            elif not self.fade_leave:
                self.timer += self.game.dt
                if self.timer >= 5000:
                    self.fade_leave = True
                    self.fadeout_step = 255

        up, left, right, down = [ctrls.get_buttons()[key] for key in (ctrls.UP, ctrls.LEFT, ctrls.RIGHT, ctrls.DOWN)]

        if up:
            self.char_timer_threshold += self.game.dt
            if self.char_timer_threshold > 800:
                self.char_timer += self.game.dt
                if self.char_timer >= 100:
                    self.char_timer = 0
                    self.decr_char()
        if down:
            self.char_timer_threshold += self.game.dt
            if self.char_timer_threshold > 1000:
                self.char_timer += self.game.dt
                if self.char_timer >= 100:
                    self.char_timer = 0
                    self.incr_char()

    def handle_events(self, events):
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
                    if e.value == 0:
                        self.char_timer = 0
                        self.char_timer_threshold = 0
                if e.axis == 0:
                    if e.value < 0:
                        self.prev_char()
                    if e.value > 0:
                        self.next_char()

            if e.type == pg.KEYUP:
                if e.key in [pg.K_DOWN, pg.K_UP]:
                    self.char_timer = 0
                    self.char_timer_threshold = 0

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
            audio.play_sfx('text')

    def incr_char(self):
        if self.name_input_active and self.blit_elements[4]:
            self.alphabet_pointer += 1
            self.alphabet_pointer = self.alphabet_pointer % (len(self.alphabet))
            self.name[self.cursor] = self.alphabet[self.alphabet_pointer]
            audio.play_sfx('text')

    def prev_char(self):
        if self.name_input_active and self.blit_elements[4]:
            if self.cursor > 0:
                self.cursor -= 1
                self.alphabet_pointer = self.alphabet.index(self.name[self.cursor])
                audio.play_sfx('menu_nav')

    def next_char(self):
        if self.name_input_active and self.blit_elements[4]:
            if self.cursor < len(self.name) - 1:
                self.cursor += 1
                self.alphabet_pointer = self.alphabet.index(self.name[self.cursor])
                audio.play_sfx('menu_nav')

    def accept_name(self):
        if self.name_input_active:
            self.name_input_active = False
            self.blit_cursor = False
            audio.play_sfx('select')
            self.game.highscores.add(''.join(self.name), self.score, self.game.settings.free_mode)
            self.game.highscores.save()
            self.fadeout_step = 255
            self.fade_leave = True
