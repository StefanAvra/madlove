import collections
import random

import pygame as pg
import sys
import numpy
import os

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
        self.lives = 3
        self.player = Player()
        self.balls = pg.sprite.Group()
        # self.balls.add(Ball())
        self.bricks = pg.sprite.Group()
        self.bombs = pg.sprite.Group()
        self.level_data = levels.Level(level_no)
        self.notif_stack = []
        self.notification = None
        self.timer = 0
        self.hud_highlight_clock = 0
        self.hud_highlight_combo = 0
        self.timer = 0
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave_to = False

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
        pg.mixer.music.load(os.path.join(sound.MUSIC_DIR, 'bgm.ogg'))
        pg.mixer.music.set_volume(0.5)
        # pg.mixer.music.play(-1)
        self.reset_round()

    def render(self, screen):
        global score
        screen.fill(bg_color)

        render_hud(screen, str(score), stages[self.current_stage], str(self.lives), self.timer,
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

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        self.timer += time_passed
        # pressed = pg.key.get_pressed()
        # up, left, right, down = [pressed[key] for key in (pg.K_UP, pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN)]

        up, left, right, down = [ctrls.get_buttons()[key] for key in (ctrls.UP, ctrls.LEFT, ctrls.RIGHT, ctrls.DOWN)]

        if config.ENABLE_BOT:
            left, right = bot.play(self.player, self.balls)
        for ball in self.balls:
            ball.update(self.player, self.bricks, self.bombs)

        self.player.update(left, right, up)
        if not self.balls.has(self.balls):
            self.manager.go_to(LostLifeScene(self))
        if not self.bricks.has(self.bricks):
            self.manager.go_to(FinishedLevelScene(self))

        past_stage = self.current_stage
        self.current_stage = int(numpy.interp(len(self.bricks), [0, self.total_bricks], [len(stages), 0]))
        if stages[past_stage] == stages[0] and stages[past_stage] != stages[self.current_stage]:
            print('cancer')
            self.notif_stack.append(Message("got cancer!"))

        if len(self.notif_stack) > 0 and self.notification is None:
            self.notification = self.notif_stack.pop(0)

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

    def reset_round(self):
        self.balls.add(Ball(velocity=(random.randint(-2, 2), -3)))
        self.all_sprites.add(self.balls)
        self.player.rect.centerx = pg.display.get_surface().get_rect().centerx
        pg.mixer.music.play(-1)

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button == 0:
                    self.manager.go_to(OverlayMenuScene(self, 'ingame-exit'))
                if e.button == 1:
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
                    for ball in self.balls:
                        ball.sticky = False
                if e.key == pg.K_n:
                    self.bricks.empty()


class FinishedLevelScene(Scene):
    def __init__(self, game_state):
        super(FinishedLevelScene, self).__init__()
        self.finished_lvl = game_state.level_data.no
        self.current_stage = game_state.current_stage
        self.lives = game_state.lives
        self.next_level = self.finished_lvl + 1
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

        # todo: show time bonus, reached cancer stage, score

        finished_text = font_16.render(str_r.get_string('finished'), True, config.TEXT_COLOR)
        finished_pos = finished_text.get_rect()
        finished_pos.center = screen.get_rect().center
        screen.blit(finished_text, finished_pos)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button in [0, 1]:
                    self.manager.go_to(GameScene(self.next_level))
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'ingame-exit'))
                if e.key == pg.K_SPACE:
                    self.manager.go_to(GameScene(self.next_level))


class LostLifeScene(Scene):
    def __init__(self, game_state):
        super(LostLifeScene, self).__init__()
        self.game_state = game_state
        self.game_state.lives -= 1
        self.game_over = False
        self.lost_text = str_r.get_string('lost_life').splitlines()
        text_surf_x, text_surf_y = menus.PADDING * 2, menus.PADDING * 2
        text_surf_y += menus.MENU_LINE_OFFSET * len(self.lost_text) - menus.MENU_LINE_OFFSET / 2
        text_surf_x += 16 * len(max(self.lost_text, key=len))
        self.text_bg_surf = pg.Surface((text_surf_x, text_surf_y))
        self.text_bg_shadow = pg.Surface((self.text_bg_surf.get_rect().width, self.text_bg_surf.get_rect().height))
        pg.mixer.music.stop()

        if self.game_state.lives <= 0:
            self.game_over = True
        else:
            print('lost a life')

    def render(self, screen):
        if not self.game_over:
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

    def update(self):
        if self.game_over:
            self.manager.go_to(GameOver(self.game_state))

    def handle_events(self, events):
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
        # todo: change these with titlescreen art later
        self.line1 = font_24.render(config.GAME_TITLE, True, config.TEXT_COLOR)
        self.line2 = font_16.render(config.GAME_SUBTITLE, True, config.TEXT_COLOR)
        self.cprght = font_8.render(str_r.get_string('copyright'), True, config.TEXT_COLOR)
        self.menu = menus.get_entries('titlescreen')
        self.menu_funcs = menus.get_funcs('titlescreen')
        self.highlight_clock = 0
        self.highlight_color = config.MENU_COLOR_HIGHLIGHT
        self.cursor = 0
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave_to = False

    def render(self, screen):
        self.highlight_clock += time_passed
        screen.fill(bg_color)
        pos_line1 = center_to(screen, self.line1)
        pos_line1 = (pos_line1[0], pos_line1[1] - 24)
        pos_line2 = center_to(screen, self.line2)
        pos_line2 = (pos_line2[0], pos_line2[1] + 16)
        pos_copy = self.cprght.get_rect()
        pos_copy.center = (screen.get_rect().centerx, screen.get_rect().height * 0.8)
        screen.blit(self.line1, pos_line1)
        screen.blit(self.line2, pos_line2)
        screen.blit(self.cprght, pos_copy)
        for idx, entry in enumerate(self.menu):
            if self.cursor == idx:
                if self.highlight_clock >= 100:
                    self.highlight_color = tuple(numpy.subtract((255, 255, 255), self.highlight_color))
                    self.highlight_clock = 0
                color = self.highlight_color
            else:
                color = config.TEXT_COLOR
            entry_surf = font_16.render(entry, True, color)
            entry_pos = (x_center_to(screen, entry_surf), 400 + idx * menus.MENU_LINE_OFFSET)
            screen.blit(entry_surf, entry_pos)

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        if self.fade_leave_to and self.fadeout_step <= 0:
            if self.fade_leave_to == 1:
                self.manager.go_to(GameScene(0))
            if self.fade_leave_to == 2:
                self.manager.go_to(HighscoreScene())
            if self.fade_leave_to == 3:
                pass

    def handle_events(self, events):
        if not self.fade_leave_to:
            for e in events:
                if e.type == pg.JOYBUTTONDOWN:
                    if e.button == 0:
                        self.fadeout_step = 255
                        f = self.menu_funcs[self.cursor]
                        if f == 'start':
                            self.fade_leave_to = 1
                        elif f == 'scores':
                            self.fade_leave_to = 2
                        elif f == 'credits':
                            pass

                if e.type == pg.JOYAXISMOTION:
                    if e.axis == 1:
                        if e.value < 0:
                            sound.sfx_lib.get('menu_nav').play()
                            self.cursor -= 1
                            if self.cursor < 0:
                                self.cursor = len(self.menu) - 1
                        if e.value > 0:
                            sound.sfx_lib.get('menu_nav').play()
                            self.cursor += 1
                            if self.cursor >= len(self.menu):
                                self.cursor = 0

                if e.type == pg.KEYDOWN:
                    if e.key in [pg.K_SPACE, pg.K_RETURN]:
                        self.fadeout_step = 255
                        f = self.menu_funcs[self.cursor]
                        if f == 'start':
                            self.fade_leave_to = 1
                        elif f == 'scores':
                            self.fade_leave_to = 2
                        elif f == 'credits':
                            pass

                    if e.key == pg.K_ESCAPE:
                        self.manager.go_to(OverlayMenuScene(self, 'exit'))
                    if e.key == pg.K_h:
                        self.manager.go_to(HighscoreScene())
                    if e.key == pg.K_DOWN:
                        sound.sfx_lib.get('menu_nav').play()
                        self.cursor += 1
                        if self.cursor >= len(self.menu):
                            self.cursor = 0
                    if e.key == pg.K_UP:
                        sound.sfx_lib.get('menu_nav').play()
                        self.cursor -= 1
                        if self.cursor < 0:
                            self.cursor = len(self.menu) - 1


class GameOver(Scene):
    def __init__(self, game_state):
        super(GameOver, self).__init__()
        global score
        self.score = score
        self.reached_lvl = game_state.level_data.no
        self.reached_stage = game_state.current_stage
        self.lives_left = game_state.lives

        score = 0
        print('ded.')
        if pg.mixer.music.get_busy():
            pg.mixer.music.stop()
        sound.sfx_lib.get('game_over').play()

        # todo: calc score, load highscores, input name if highscore

    def render(self, screen):
        screen.fill(bg_color)
        game_over_txt = str_r.get_string('game_over').splitlines()
        for idx, line in enumerate(game_over_txt):
            over_text_surf = font_16.render(line, True, config.TEXT_COLOR)

            over_rect = over_text_surf.get_rect()
            over_rect.center = (screen.get_rect().centerx, screen.get_rect().centery + idx * menus.PADDING)
            screen.blit(over_text_surf, over_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.JOYBUTTONDOWN:
                if e.button == 0:
                    sound.sfx_lib.get('game_over').stop()
                    self.manager.go_to(TitleScene())

            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE, pg.K_RETURN]:
                    sound.sfx_lib.get('game_over').stop()
                    self.manager.go_to(TitleScene())
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'exit'))


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
        pg.mixer.music.pause()
        if self.menu_type == 'pause':
            self.animation = Ashtray()

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
        pg.mixer.music.unpause()
        self.manager.go_to(self.paused_scene)


class HighscoreScene(Scene):
    def __init__(self):
        super(HighscoreScene, self).__init__()
        scores.load_highscores()
        self.lines = []
        place = 0
        for score in scores.highscores:
            place += 1
            # new_line = '{name: <{fill}}    {score}'.format(name=score[0], fill='8', score=score[1])
            new_line = '{:<2}   {:<8} {:>10}'.format(place, score[0], score[1])
            self.lines.append(
                font_16.render(new_line,
                               True, config.TEXT_COLOR))
        self.title = font_16.render(str_r.get_string('highscores_title'), True, config.TEXT_COLOR)
        self.fadein_step = 255
        self.fadeout_step = 0
        self.fade_leave = False

    def render(self, screen):

        # todo: place on the left, names left aligned, score right aligned, labels for name and score

        screen.fill(bg_color)
        title_pos = self.title.get_rect()
        title_pos.center = (screen.get_width() / 2, screen.get_height() * 0.1)
        screen.blit(self.title, title_pos)
        for idx, line in enumerate(self.lines):
            screen.blit(line, (50, 150 + (40 * idx)))

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = render_fading(screen, self.fadein_step, 0)
        if self.fadeout_step > 0:
            self.fadeout_step = render_fading(screen, self.fadeout_step, 1)

    def update(self):
        if self.fade_leave and self.fadeout_step <= 0:
            self.manager.go_to(TitleScene())

    def handle_events(self, events):
        for e in events:
            if not self.fade_leave:
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE:
                        self.fadeout_step = 255
                        self.fade_leave = True


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
    # should be called inside GameScene() for each new level
    def __init__(self):
        super(IntroScene, self).__init__()

    def render(self, screen):
        pass

    def update(self):
        pass

    def handle_events(self, events):
        pass


class SceneManager(object):
    def __init__(self):
        self.scene = None
        self.go_to(TitleScene())

    def go_to(self, scene):
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
        self.velocity = (round((self.rect.centerx - x_hit)/5), -abs(self.velocity[1]))
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
        # todo: check collision via sub-rects, that go almost to the corners of ball.rect -- or maybe not? maybe circle?

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
        self.rect.y = 630


class Brick(pg.sprite.Sprite):
    def __init__(self, x=0, y=0, color=(255, 0, 0), health=2, brick_type='b'):
        types = {'r': 'red', 'w': 'white', 'b': 'black'}
        super().__init__()
        self.image = pg.image.load(os.path.join('assets', 'graphics', 'brick_{}.png'.format(types[brick_type]))).convert()
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
    def __init__(self, msg):
        self.timer = 2000
        self.color = config.TEXT_COLOR
        self.msg = msg.upper()
        self.highlight_clock = 0

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
    print(alpha)
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
        score_text = font_16.render(str_r.get_string('combo').format(scores.get_combo()), True, color)
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

        manager.scene.handle_events(pg.event.get())
        manager.scene.update()
        manager.scene.render(screen)
        if config.SHOW_FPS:
            fps = font_8.render(str(int(clock.get_fps())), True, config.DEBUG_COLOR)
            screen.blit(fps, (0, 0))
        pg.display.flip()

    quit_game()


if __name__ == "__main__":
    main()
