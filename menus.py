import pygame as pg

PADDING = 48
HEADER_SIZE = 16


def get_entries(menu_type):
    entries = {
        'titlescreen': ['Yes', 'No'],
        'ingame': ['Continue', 'Exit']
    }
    return entries.get(menu_type)


def get_title(menu_type):
    titles = {
        'titlescreen': 'EXIT GAME?',
        'ingame': 'PAUSE'

    }
    return titles.get(menu_type)


def get_surf(menu_type):
    x, y = PADDING, PADDING
    x += HEADER_SIZE
    y += 24 * len(get_entries(menu_type)) - 16
    x += 16 * len(max(get_entries(menu_type), key=len))
    return pg.Surface((x, y))
