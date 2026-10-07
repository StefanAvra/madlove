"""Makes MadLove's logo and icons from the title screen's lettering and arrow, graphics/title.png and arrow.png.

    uv run python web/make_logo.py

web/static/logo.png is the title as on the title screen, on its red arrow, for the README.
web/static/favicon.png (browser tabs) and web/static/apple-touch-icon.png (home screens) show its M.
"""

import os
import pathlib

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame as pg  # noqa: E402

from madlove import config, hud  # noqa: E402
from madlove.sprites.decor import Arrow, Title  # noqa: E402

STATIC = pathlib.Path(__file__).parent / 'static'
LOGO_SCALE = 2  # pixels doubled, for sharp high-density screens
LOGO_PAD = 32  # pink around the arrow
M = pg.Rect(0, 51, 71, 118)  # the M in title.png


def logo(font):
    """the title screen once its intro has played, without the cigarettes and texts below, cut to the arrow"""
    screen = pg.display.get_surface()
    screen.fill(config.BG_COLOR)
    arrow = Arrow(True)
    while not arrow.done:
        arrow.update()
    screen.blit(arrow.image, arrow.rect)
    title = Title()
    screen.blit(title.image, title.rect)
    # placed as in TitleScene.render
    subtitle = font.render(config.GAME_SUBTITLE, True, config.TEXT_COLOR)
    screen.blit(subtitle, hud.center_to(screen, subtitle).move(0, 16))
    out = pg.Surface(arrow.rect.inflate(2 * LOGO_PAD, 2 * LOGO_PAD).size)
    out.fill(config.BG_COLOR)
    out.blit(screen, (LOGO_PAD, LOGO_PAD), arrow.rect)
    return pg.transform.scale_by(out, LOGO_SCALE)


def icon(title, size):
    """the M, filling the square but for a small margin"""
    letter = title.subsurface(M)
    letter = pg.transform.smoothscale_by(letter, (size - 2 * max(1, size // 16)) / letter.get_height())
    out = pg.Surface((size, size))
    out.fill(config.BG_COLOR)
    out.blit(letter, letter.get_rect(center=(size // 2, size // 2)))
    return out


def main():
    pg.init()
    pg.display.set_mode((480, 640))
    title = pg.image.load(config.asset('graphics', 'title.png')).convert_alpha()
    font = pg.font.Font(config.FONT, 16)
    for name, surface in [
        ('logo.png', logo(font)),
        ('favicon.png', icon(title, 64)),
        ('apple-touch-icon.png', icon(title, 180)),
    ]:
        path = STATIC / name
        pg.image.save(surface, path)
        print(f'{surface.get_width()}x{surface.get_height()} -> {path}')


if __name__ == '__main__':
    main()
