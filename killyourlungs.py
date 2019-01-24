import pygame as pg
import sys
import config


bg_color = pg.Color(config.BACKGROUND_COLOR)


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

        # todo: load level

    def render(self, screen):
        screen.blit(self.bg)

    def update(self):
        pressed = pg.key.get_pressed()
        up, left, right = [pressed[key] for key in (pg.K_UP, pg.K_LEFT, pg.K_RIGHT)]

    def handle_events(self, events):
        for e in events:
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                pass  # open menu


class TitleScene(object):

    def __init__(self):
        super(TitleScene, self).__init__()
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


class SceneManager(object):
    def __init__(self):
        self.go_to(TitleScene())

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self


def main():
    pg.init()
    screen = pg.display.set_mode(config.DISPLAY, config.FLAGS, config.DEPTH)
    pg.display.set_caption(config.CAPTION)
    clock = pg.time.Clock()
    running = True

    font = pg.font.Font(config.FONT, 16)

    manager = SceneManager()

    while running:
        clock.tick(config.FRAMERATE)

        if pg.event.get(pg.QUIT):
            running = False
            return



        pressed = pg.key.get_pressed()
        up, left, right, down = [pressed[key] for key in (pg.K_UP, pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN)]

        manager.scene.handle_events(pg.event.get())
        manager.scene.update()
        manager.scene.render(screen)
        if config.SHOW_FPS:
            fps = font.render(str(int(clock.get_fps())), True, pg.Color('white'))
            screen.blit(fps, (50, 50))
        pg.display.flip()

    pg.display.quit()
    sys.exit()


if __name__ == "__main__":
    main()
