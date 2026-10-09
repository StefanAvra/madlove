"""The HUD above the level: score, stage and lives with the cigarette pack."""

import pygame as pg

from madlove import hud


def test_the_pack_loads_once(game, monkeypatch):
    hud.pack_image.cache_clear()
    loads = []
    load = pg.image.load
    monkeypatch.setattr(pg.image, 'load', lambda *args: loads.append(args) or load(*args))
    for _ in range(3):
        hud.render_hud(game, game.screen, '0', 'HEALTHY', '3', 0)
    assert len(loads) == 1
    pack = hud.pack_image()
    x = game.screen.get_width() - 24
    assert game.screen.get_at((x + 8, 8 + 8)) == pack.get_at((8, 8))


def test_text_is_drawn_once_for_the_same_text_and_color(game):
    first = hud.text(game.font_16, '1200', (0, 0, 0))
    assert hud.text(game.font_16, '1200', pg.Color(0, 0, 0)) is first
    assert hud.text(game.font_16, '1210', (0, 0, 0)) is not first
    assert hud.text(game.font_16, '1200', (255, 255, 255)) is not first


def test_cover(game):
    game.screen.fill((0, 0, 0))
    hud.cover(game.screen, (255, 255, 255), 0)
    assert game.screen.get_at((10, 10)) == pg.Color(0, 0, 0)
    hud.cover(game.screen, (255, 255, 255), 128)
    assert all(abs(c - 128) <= 1 for c in game.screen.get_at((10, 10))[:3])  # SDL's blend rounds
    hud.cover(game.screen, (255, 255, 255))
    assert game.screen.get_at((10, 10)) == pg.Color(255, 255, 255)
