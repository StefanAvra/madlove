import pygame as pg
import sys


WIDTH = 480
HEIGHT = 640
DISPLAY = (WIDTH, HEIGHT)
DEPTH = 0
GAME_TITLE = "Kill Your Lungs"
CAPTION = GAME_TITLE
FRAMERATE = 60
SHOW_FPS = 1
FLAGS = 0
# pg.FULLSCREEN   create a fullscreen display
# pg.DOUBLEBUF    recommended for HWSURFACE or OPENGL
# pg.HWSURFACE    hardware accelerated, only in FULLSCREEN
# pg.OPENGL       create an OpenGL-renderable display
# pg.RESIZABLE    display window should be sizeable
# pg.NOFRAME      display window will have no border or controls

PINK = pg.Color("#fabfd0")


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
    def __init__(self):
        super(GameScene, self).__init__()
        level = 0
        self.bg = pg.Surface((32, 32))
        self.bg.convert()
        self.bg.fill(PINK)

    def render(self, screen):
        yield

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
        self.font = pg.font.SysFont('Arial', 56)
        self.sfont = pg.font.SysFont('Arial', 32)

    def render(self, screen):
        # ugly!
        screen.fill(PINK)
        line1 = self.font.render(GAME_TITLE, True, (0, 0, 0))
        line2 = self.sfont.render('The Game', True, (0, 0, 0))
        screen.blit(line1, (200, 50))
        screen.blit(line2, (200, 350))

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
    screen = pg.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pg.display.set_caption(CAPTION)
    clock = pg.time.Clock()
    running = True

    font = pg.font.Font(None, 30)

    scene = GameScene()

    while running:
        clock.tick(FRAMERATE)

        if pg.event.get(pg.QUIT):
            running = False
            return

        if SHOW_FPS:
            fps = font.render(str(int(clock.get_fps())), True, pg.Color('white'))
            screen.blit(fps, (50, 50))

        pressed = pg.key.get_pressed()
        up, left, right = [pressed[key] for key in (pg.K_UP, pg.K_LEFT, pg.K_RIGHT)]

        # manager.scene.handle_events(pg.event.get())
        # manager.scene.update()
        # manager.scene.render(screen)
        pg.display.flip()


if __name__ == "__main__":
    main()
