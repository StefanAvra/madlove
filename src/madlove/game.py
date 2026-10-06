"""The game object, the scene manager and the main loop."""

import pygame as pg

from madlove import audio, bot, coins, config, scores
from madlove import controls as ctrls
from madlove import strings as str_r
from madlove.scenes import title

INTRO_IMAGES = 7  # level_intro_1.png to level_intro_7.png


class SceneManager:
    def __init__(self, game):
        self.scene = None
        self.go_to(title.TitleScene(game))

    def go_to(self, scene):
        print(f'Switching to {scene.__class__.__name__}')
        self.scene = scene
        self.scene.manager = self


class Game:
    """the running game: settings, score, credit and lives, combo, high scores, fonts and the current scene"""

    def __init__(self, settings=None):
        self.settings = settings or config.Settings()
        self.score = 0
        self.dt = 0  # milliseconds since the last frame
        self.wallet = coins.Wallet()
        self.combo = scores.Combo()
        self.highscores = scores.HighScores(self.settings.data_dir)
        self.highscores.load()
        self.facts = str_r.Facts()
        self.intro_no = 1
        self.bot = bot.Bot()  # plays when settings.bot is on

        audio.init()
        ctrls.init()
        pg.init()
        flags = config.FLAGS | (pg.FULLSCREEN if self.settings.fullscreen else 0)
        self.screen = pg.display.set_mode(config.DISPLAY, flags, config.DEPTH)
        pg.mouse.set_visible(False)
        pg.display.set_caption(config.CAPTION)
        self.font_8 = pg.font.Font(config.FONT, 8)
        self.font_16 = pg.font.Font(config.FONT, 16)
        self.font_24 = pg.font.Font(config.FONT, 24)
        self.clock = None
        self.scenes = None

    def next_intro(self):
        """the number of the next level intro image, counting from 1 and starting over after the last"""
        number = self.intro_no
        self.intro_no += 1
        if self.intro_no > INTRO_IMAGES:
            self.intro_no = 1
        return number

    def run(self):
        """runs until the game gets a QUIT event"""
        self.clock = pg.time.Clock()
        self.scenes = SceneManager(self)
        while self.step():
            pass

    def step(self):
        """runs one frame. returns False when the game should quit"""
        self.dt = self.clock.tick(config.FRAMERATE)

        if pg.event.get(pg.QUIT):
            return False

        events = pg.event.get()
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_1:
                    self.wallet.add_coin()
                    audio.play_sfx('coin')
            if e.type == pg.JOYBUTTONDOWN:
                if e.button == ctrls.INSERT_COIN:
                    self.wallet.add_coin()
                    audio.play_sfx('coin')

        # each call can switch scenes; the next one then goes to the new scene
        self.scenes.scene.handle_events(events)
        self.scenes.scene.update()
        self.scenes.scene.render(self.screen)
        if self.settings.show_fps:
            fps = self.font_8.render(str(int(self.clock.get_fps())), True, config.DEBUG_COLOR)
            self.screen.blit(fps, (0, 0))
        pg.display.flip()
        return True


def main(settings=None):
    Game(settings).run()
