import pygame as pg
import config
import killyourlungs

PADDING = 24
HEADER_SIZE = 40
MENU_OFFSET = 24


def get_entries(menu_type):
    entries = {
        'titlescreen': ['NO', 'YES'],
        'ingame': ['CONTINUE', 'EXIT']
    }
    return entries.get(menu_type)


def get_title(menu_type):
    titles = {
        'titlescreen': 'EXIT GAME?',
        'ingame': 'PAUSE'

    }
    return titles.get(menu_type)


def get_funcs(menu_type):
    funcs = {
        'titlescreen': ['back', killyourlungs.quit_game],
        'ingame': ['back', killyourlungs.quit_game]
    }
    return funcs.get(menu_type)


def get_surf(menu_type):
    x, y = PADDING * 2, PADDING * 2
    y += HEADER_SIZE
    y += MENU_OFFSET * len(get_entries(menu_type)) - MENU_OFFSET / 2
    lines = get_entries(menu_type)
    lines.append(get_title(menu_type))
    x += 16 * len(max(lines, key=len))
    return pg.Surface((x, y))


def make_outline(surface, fill_color, outline_color=config.TEXT_COLOR, border=4):
    surface.fill(outline_color)
    surface.fill(fill_color, surface.get_rect().inflate(-border, -border))

