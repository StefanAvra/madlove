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
