"""The game object, the scene manager and the main loop."""

import asyncio

import pygame as pg

from madlove import audio, bot, coins, config, scores, storage
from madlove import controls as ctrls
from madlove import strings as str_r
from madlove.scenes import menu, play, title

INTRO_IMAGES = 7  # level_intro_1.png to level_intro_7.png
PAUSED_POLL = 0.25  # seconds between checks whether the browser's page is back


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
        self.highscores = scores.HighScores(storage.highscores_store(self.settings))
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
        if config.WEB:
            from platform import window  # pygbag adds the browser's window object to this module

            window.canvas.style.imageRendering = 'pixelated'  # scale up without blurring the pixels
            self.page = window.madlove_page  # set up by web/static/madlove.js
        else:
            self.page = None
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

    def active(self):
        """False while the browser's page is hidden or has lost focus. always True outside the browser"""
        return self.page is None or self.page.active

    async def run(self):
        """runs until the game gets a QUIT event. it's async so the browser build can draw between frames"""
        self.clock = pg.time.Clock()
        self.scenes = SceneManager(self)
        while self.step():
            await asyncio.sleep(0)  # hands control back to the browser once per frame
            if not self.active():
                await self.wait_until_active()

    async def wait_until_active(self):
        """stops the game and its sound while the page is away, so a phone doesn't heat up with the game
        left open in a tab. a running level comes back in the smoke break"""
        audio.pause_all()
        while not self.active():
            await asyncio.sleep(PAUSED_POLL)
        audio.unpause_all()
        self.clock.tick()  # so the next frame's dt doesn't include the time away
        scene = self.scenes.scene
        if isinstance(scene, play.GameScene):
            self.scenes.go_to(menu.OverlayMenuScene(self, scene, 'pause'))

    def step(self):
        """runs one frame. returns False when the game should quit"""
        self.dt = self.clock.tick(config.FRAMERATE)

        if pg.event.get(pg.QUIT):
            return False

        ctrls.poll()  # the on-screen controls in the browser post their events now
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
    asyncio.run(Game(settings).run())
