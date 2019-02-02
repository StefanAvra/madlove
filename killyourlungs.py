import pygame as pg
import sys
import numpy
import os

import sound
import config
import menus
import string_resource as str_r
import levels

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
        self.current_stage = 0
        self.lives = 3
        self.player = Player()
        self.balls = pg.sprite.Group()
        self.balls.add(Ball())
        self.bricks = pg.sprite.Group()
        self.bombs = pg.sprite.Group()
        self.level_data = levels.Level(level_no)

        tile_offset_y = 0
        for line in self.level_data.bricks:
            tile_offset_x = 0
            for tile in line:
                if tile == 'b':
                    brick = Brick(tile_offset_x, tile_offset_y)
                    self.bricks.add(brick)
                tile_offset_x += levels.TILE[0]
            tile_offset_y += levels.TILE[1]
        print('Level data for Level {}:\n{}'.format(self.level_data.no, self.level_data.bricks))
        self.all_sprites = pg.sprite.Group()
        self.all_sprites.add(self.player, self.balls, self.bricks, self.bombs)
        pg.mixer.music.load(os.path.join(sound.MUSIC_DIR, 'bgm.ogg'))
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)

    def render(self, screen):
        screen.fill(bg_color)
        stage_text = font_16.render(str_r.get_string('stage_text').format(stages[self.current_stage]), True, (0, 0, 0))
        screen.blit(stage_text, (10, 10))
        lives_text = font_16.render(str_r.get_string('lives_text').format(self.lives), True, (0, 0, 0))
        screen.blit(lives_text, (screen.get_width() - 150, 10))

        self.all_sprites.draw(screen)

    def update(self):
        pressed = pg.key.get_pressed()
        up, left, right, down = [pressed[key] for key in (pg.K_UP, pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN)]
        for ball in self.balls:
            ball.update(self.player, self.bricks, self.bombs)

        self.player.update(left, right, up)
        if not self.balls.has(self.balls):
            # make a lost life scene?
            self.manager.go_to(LostLifeScene(self))
        if not self.bricks.has(self.bricks):
            self.manager.go_to(FinishedLevelScene(self))

    def reset_round(self):
        self.balls.add(Ball())
        self.all_sprites.add(self.balls)
        self.player.rect.centerx = pg.display.get_surface().get_rect().centerx
        pg.mixer.music.play(-1)

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'ingame'))
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
        stage_text = font_16.render(str_r.get_string('stage_text').format(stages[self.current_stage]), True, (0, 0, 0))
        screen.blit(stage_text, (10, 10))
        lives_text = font_16.render(str_r.get_string('lives_text').format(self.lives), True, (0, 0, 0))
        screen.blit(lives_text, (screen.get_width() - 150, 10))
        finished_text = font_16.render(str_r.get_string('finished'), True, (0, 0, 0))
        finished_pos = finished_text.get_rect()
        finished_pos.center = screen.get_rect().center
        screen.blit(finished_text, finished_pos)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'ingame'))
                if e.key == pg.K_SPACE:
                    self.manager.go_to(GameScene(self.next_level))


class LostLifeScene(Scene):
    def __init__(self, game_state):
        super(LostLifeScene, self).__init__()
        self.game_state = game_state
        self.game_state.lives -= 1
        self.game_over = False
        pg.mixer.music.stop()

        if self.game_state.lives <= 0:
            self.game_over = True
        else:
            print('lost a life')

    def render(self, screen):
        if not self.game_over:
            lost_text = str_r.get_string('lost_life').splitlines()
            for idx, line in enumerate(lost_text):
                lost_text_surfs = font_16.render(line, True, (0, 0, 0))
                lost_rect = lost_text_surfs.get_rect()
                lost_rect.center = (screen.get_rect().centerx, screen.get_rect().centery + 100 + idx*20)
                screen.blit(lost_text_surfs, lost_rect)

    def update(self):
        if self.game_over:
            self.manager.go_to(GameOver(self.game_state))

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    self.game_state.reset_round()
                    self.go_back()
            if e.type == pg.K_ESCAPE:
                pass

    def go_back(self):
        pg.mixer.music.unpause()
        self.manager.go_to(self.game_state)


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
            over_text_surf = font_16.render(line, True, (0, 0, 0))

            over_rect = over_text_surf.get_rect()
            over_rect.center = (screen.get_rect().centerx, screen.get_rect().centery + idx*20)
            screen.blit(over_text_surf, over_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key in [pg.K_SPACE, pg.K_RETURN]:
                    sound.sfx_lib.get('game_over').stop()
                    self.manager.go_to(TitleScene())
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(OverlayMenuScene(self, 'titlescreen'))


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
        pg.mixer.music.pause()

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
        pg.mixer.music.unpause()
        self.manager.go_to(self.paused_scene)


class SceneManager(object):
    def __init__(self):
        self.go_to(TitleScene())

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self


class Ball(pg.sprite.Sprite):
    def __init__(self, pos_x=240, pos_y=550, velocity=(2, -4), size=7):
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

    def check_collision(self, rect):
        # intended to be called only after collision detected!
        self.collisions[0] = rect.collidepoint(self.rect.midtop)
        #self.collisions[1] = rect.collidepoint(self.rect.topright)
        self.collisions[2] = rect.collidepoint(self.rect.midright)
        #self.collisions[3] = rect.collidepoint(self.rect.bottomright)
        self.collisions[4] = rect.collidepoint(self.rect.midbottom)
        #self.collisions[5] = rect.collidepoint(self.rect.bottomleft)
        self.collisions[6] = rect.collidepoint(self.rect.midleft)
        #self.collisions[7] = rect.collidepoint(self.rect.topleft)

    def hit_paddle(self, paddle_rect):
        x_hit = paddle_rect.center[0]
        sound.sfx_lib.get('hit_wall').play()
        self.velocity = ((self.rect.center[0] - x_hit) * 0.09 + self.velocity[0], -abs(self.velocity[1]))
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
        if not direction % 2 == 0:
            self.velocity = (-self.velocity[0], -self.velocity[1])
        elif direction == 0:
            self.velocity = (self.velocity[0], abs(self.velocity[1]))
        elif direction == 4:
            self.velocity = (self.velocity[0], -abs(self.velocity[1]))
        elif direction == 2:
            self.velocity = (-abs(self.velocity[0]), self.velocity[1])
        elif direction == 6:
            self.velocity = (abs(self.velocity[0]), self.velocity[1])

    def hit_brick(self, brick):
        self.check_collision(brick.rect)
        if True in self.collisions[::2]:
            self.bounce(self.collisions[::2].index(True) * 2)
        # else:
        #     self.bounce(self.collisions.index(True))
            brick.health -= 1
            if brick.health <= 0:
                brick.kill()
            sound.sfx_lib.get('hit_brick').play()

    def update(self, player, bricks, bombs):
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
        # todo: check collision via sub-rects, that go almost to the corners of ball.rect

        if collided_brick:
            self.hit_brick(collided_brick)

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


class Brick(pg.sprite.Sprite):
    def __init__(self, x=0, y=0, color=(0, 0, 0), health=1):
        super().__init__()
        self.image = pg.Surface(levels.TILE)
        self.image.fill(color)
        self.health = health
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


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
