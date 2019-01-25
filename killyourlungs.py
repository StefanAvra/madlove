import pygame as pg
import sys
import config
import menus


bg_color = pg.Color(config.BACKGROUND_COLOR)
font_16 = None
font_24 = None
stages = ['0', 'IA1', 'IA2', 'IA3', 'IB', 'IIA', 'IIB', 'IIIA', 'IIIB', 'IIIC', 'IVA', 'IVA', 'IVB']
score = 0


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

        # todo: load level

    def render(self, screen):
        screen.fill(bg_color)
        stage_text = font_16.render('STAGE: {}'.format(stages[self.current_stage]), True, (0, 0, 0))
        screen.blit(stage_text, (10, 10))
        lives_text = font_16.render('SMOKES: {}'.format(self.lives), True, (0, 0, 0))
        screen.blit(lives_text, (screen.get_width() - 150, 10))

    def update(self):
        pressed = pg.key.get_pressed()
        up, left, right, down = [pressed[key] for key in (pg.K_UP, pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN)]

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                self.manager.go_to(OverlayMenuScene(self, 'ingame'))


class TitleScene(Scene):
    def __init__(self):
        super(TitleScene, self).__init__()
        # change these with titlescreen art later
        self.title_font = pg.font.Font(config.FONT, 24)
        self.subtitle_font = pg.font.Font(config.FONT, 16)

    def render(self, screen):
        screen.fill(bg_color)
        line1 = self.title_font.render(config.GAME_TITLE, True, (0, 0, 0))
        line2 = self.subtitle_font.render(config.GAME_SUBTITLE, True, (0, 0, 0))
        pos_line1 = line1.get_rect()
        pos_line1.center = (screen.get_width() / 2, screen.get_height() / 2 - 24)
        pos_line2 = line2.get_rect()
        pos_line2.center = (screen.get_width() / 2, screen.get_height() / 2 + 16)
        screen.blit(line1, pos_line1)
        screen.blit(line2, pos_line2)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                self.manager.go_to(GameScene(0))
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                self.manager.go_to(OverlayMenuScene(self, 'titlescreen'))


class OverlayMenuScene(Scene):
    def __init__(self, paused_scene, menu_type):
        super(OverlayMenuScene, self).__init__()
        self.menu_entries = menus.get_entries(menu_type)
        self.menu_surf = menus.get_surf(menu_type)
        self.menu_title = menus.get_title(menu_type)
        self.paused_scene = paused_scene
        self.cursor = 0

    def render(self, screen):
        make_outline(self.menu_surf, bg_color)
        title = font_16.render(self.menu_title, True, config.MENU_COLOR)
        title_pos = title.get_rect()
        title_pos
        for entries in self.menu_entries:
            pass

        screen.blit(self.menu_surf, (50, 50))

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    self.manager.go_to(GameScene(0))
                if e.key == pg.K_ESCAPE:
                    self.manager.go_to(self.paused_scene)


class SceneManager(object):
    def __init__(self):
        self.go_to(TitleScene())

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self


def make_outline(surface, fill_color, outline_color=config.MENU_COLOR, border=4):
    surface.fill(outline_color)
    surface.fill(fill_color, surface.get_rect().inflate(-border, -border))


def main():
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
        clock.tick(config.FRAMERATE)

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

    pg.display.quit()
    sys.exit()


if __name__ == "__main__":
    main()
