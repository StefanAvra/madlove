import pygame as pg
import sys
import config
import menus
import numpy
import math
import os

bg_color = pg.Color(config.BACKGROUND_COLOR)
font_16 = None
font_24 = None
stages = ['0', 'IA1', 'IA2', 'IA3', 'IB', 'IIA', 'IIB', 'IIIA', 'IIIB', 'IIIC', 'IVA', 'IVA', 'IVB']
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
        self.level_no = level_no
        self.current_stage = 0
        self.lives = 3
        self.player = Player()
        self.balls = pg.sprite.Group()
        self.balls.add(Ball())
        self.blocks = pg.sprite.Group()
        self.bombs = pg.sprite.Group()

        # todo: load level
        self.all_sprites = pg.sprite.Group()
        self.all_sprites.add(self.player, *self.balls, self.blocks, self.bombs)

    def render(self, screen):
        screen.fill(bg_color)
        stage_text = font_16.render('STAGE: {}'.format(stages[self.current_stage]), True, (0, 0, 0))
        screen.blit(stage_text, (10, 10))
        lives_text = font_16.render('SMOKES: {}'.format(self.lives), True, (0, 0, 0))
        screen.blit(lives_text, (screen.get_width() - 150, 10))

        self.all_sprites.draw(screen)
        # for ball in self.balls:
        #     screen.blit(ball.image, (ball.x, ball.y))

    def update(self):
        pressed = pg.key.get_pressed()
        up, left, right, down = [pressed[key] for key in (pg.K_UP, pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN)]
        for ball in self.balls:
            ball.update()
            if pg.sprite.collide_rect(ball, self.player):
                ball.hit_paddle(self.player.rect.center[0])
        self.player.update(left, right, up)
        pg.sprite.groupcollide(self.balls, self.blocks, False, True)
        if not self.balls.has(self.balls):
            self.manager.go_to(GameOver(self))

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                self.manager.go_to(OverlayMenuScene(self, 'ingame'))


class TitleScene(Scene):
    def __init__(self):
        super(TitleScene, self).__init__()
        # change these with titlescreen art later
        self.title_font = font_24
        self.subtitle_font = font_16

    def render(self, screen):
        screen.fill(bg_color)
        line1 = self.title_font.render(config.GAME_TITLE, True, (0, 0, 0))
        line2 = self.subtitle_font.render(config.GAME_SUBTITLE, True, (0, 0, 0))
        pos_line1 = center_to(screen, line1)
        pos_line1 = (pos_line1[0], pos_line1[1] - 24)
        pos_line2 = center_to(screen, line2)
        pos_line2 = (pos_line2[0], pos_line2[1] + 16)

        screen.blit(line1, pos_line1)
        screen.blit(line2, pos_line2)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE, pg.K_RETURN]:
                    self.manager.go_to(GameScene(0))
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'titlescreen'))


class GameOver(Scene):
    def __init__(self, game):
        super(GameOver, self).__init__()
        global score
        self.score = score
        self.reached_lvl = game.level_no
        self.reached_stage = game.current_stage
        self.lives_left = game.lives
        score = 0
        print('ded.')


    def render(self, screen):
        pass

    def update(self):
        pass

    def handle_events(self, events):
        pass


class OverlayMenuScene(Scene):
    def __init__(self, paused_scene, menu_type):
        super(OverlayMenuScene, self).__init__()
        self.menu_entries = menus.get_entries(menu_type)
        self.menu_surf = menus.get_surf(menu_type)
        self.menu_title = menus.get_title(menu_type)
        self.menu_funcs = menus.get_funcs(menu_type)
        self.paused_scene = paused_scene
        self.cursor = 0
        self.highlight_clock = 0
        self.highlight_color = config.MENU_COLOR_HIGHLIGHT

    def render(self, screen):
        self.highlight_clock += time_passed
        menus.make_outline(self.menu_surf, bg_color)
        menu_pos = center_to(screen, self.menu_surf)
        title = font_16.render(self.menu_title, True, config.MENU_COLOR)
        title_pos = (x_center_to(self.menu_surf, title), menus.PADDING)
        self.menu_surf.blit(title, title_pos)
        for idx, entry in enumerate(self.menu_entries):
            if self.cursor == idx:
                if self.highlight_clock >= 100:
                    self.highlight_color = tuple(numpy.subtract((255, 255, 255), self.highlight_color))
                    self.highlight_clock = 0
                color = self.highlight_color
            else:
                color = config.MENU_COLOR
            entry_surf = font_16.render(entry, True, color)
            entry_pos = (x_center_to(self.menu_surf, entry_surf),
                         menus.PADDING + menus.HEADER_SIZE + idx * menus.MENU_OFFSET)
            self.menu_surf.blit(entry_surf, entry_pos)

        screen.blit(self.menu_surf, menu_pos)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE, pg.K_RETURN]:
                    f = self.menu_funcs[self.cursor]
                    if f == 'back':
                        self.go_back()
                    else:
                        f()
                if e.key == pg.K_ESCAPE:
                    self.go_back()
                if e.key == pg.K_DOWN:
                    self.cursor += 1
                    if self.cursor >= len(self.menu_entries):
                        self.cursor = 0
                if e.key == pg.K_UP:
                    self.cursor -= 1
                    if self.cursor < 0:
                        self.cursor = len(self.menu_entries) - 1

    def go_back(self):
        self.manager.go_to(self.paused_scene)


class SceneManager(object):
    def __init__(self):
        self.go_to(TitleScene())

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self


class Ball(pg.sprite.Sprite):
    def __init__(self, pos_x=240, pos_y=550, velocity=(1.5, -3), size=6):
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

    def hit_paddle(self, x_hit):
        self.velocity = ((self.rect.center[0] - x_hit) * 0.09 + self.velocity[0], -self.velocity[1])

    def hit_wall(self):
        self.velocity = (self.velocity[0] * -1, self.velocity[1])

    def hit_top(self):
        self.velocity = (self.velocity[0], -self.velocity[1])

    def update(self):
        # x and y are used for storing floats so finer movement is possible
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if self.rect.center[0] not in range(int(self.rect.width / 2),
                                            pg.display.get_surface().get_width() - int(self.rect.width / 2)):
            self.hit_wall()
        if self.rect.top < 0:
            self.hit_top()
        if self.rect.y > pg.display.get_surface().get_height():
            self.kill()

    def speed_up(self, factor=1.1):
        self.velocity = (self.velocity[0] * factor, self.velocity[1] * factor)


class Player(pg.sprite.Sprite):
    def __init__(self, x=200, length=45, speed=7):
        super().__init__()
        self.length = length
        self.speed = speed
        self.image = pg.image.load(os.path.join('assets/graphics', 'paddle.png'))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 630
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


def center_to(center_surface, surface):
    """will return the position needed to set surface to the center of center_surface"""
    pos = surface.get_rect()
    pos.center = center_surface.get_rect().center
    return pos


def y_center_to(center_surface, surface):
    """will return the position needed to set surface to the vertical center of center_surface"""
    pos = surface.get_rect()
    pos.center = (pos.center[0], center_surface.get_rect().height / 2)
    return pos.y


def x_center_to(center_surface, surface):
    """will return the position needed to set surface to the horizontal center of center_surface"""
    pos = surface.get_rect()
    pos.center = (center_surface.get_rect().width / 2, pos.center[1])
    return pos.x


def quit_game():
    pg.display.quit()
    sys.exit()


def main():
    global time_passed
    pg.init()
    screen = pg.display.set_mode(config.DISPLAY, config.FLAGS, config.DEPTH)
    pg.display.set_caption(config.CAPTION)
    clock = pg.time.Clock()
    running = True

    global font_16
    global font_24
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
            fps = font_16.render(str(int(clock.get_fps())), True, pg.Color('white'))
            screen.blit(fps, (0, 0))
        pg.display.flip()

    quit_game()


if __name__ == "__main__":
    main()
