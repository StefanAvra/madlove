"""Sound effects and music. Nothing starts at import: the game calls init() before pg.init()."""

import os

import pygame as pg

from madlove import config

SFX_DIR = config.asset('sounds', 'sfx')
MUSIC_DIR = config.asset('sounds', 'music')
sfx_lib = {}


def init():
    """starts the mixer and loads the sound effects. must run before pg.init(), which would start the
    mixer with its default settings"""
    pg.mixer.pre_init(44100, -16, 2, 2048)
    pg.mixer.init()
    print(f'Loading sounds from {SFX_DIR} ...')
    for filename in os.listdir(SFX_DIR):
        if filename.endswith('.ogg') or filename.endswith('.wav'):
            print(f'{filename} ...')
            name = os.path.splitext(filename)[0]
            sfx_lib[name] = pg.mixer.Sound(file=os.path.join(SFX_DIR, filename))


def play_sfx(name):
    """plays a sound effect; does nothing if it isn't loaded"""
    sound = sfx_lib.get(name)
    if sound is not None:
        sound.play()


def load_music(name):
    pg.mixer.music.load(os.path.join(MUSIC_DIR, f'{name}.ogg'))


def play_music(loops=-1):
    pg.mixer.music.play(loops)


def stop_music():
    pg.mixer.music.stop()


def pause_music():
    pg.mixer.music.pause()


def unpause_music():
    pg.mixer.music.unpause()


def music_busy():
    return pg.mixer.music.get_busy()


def set_music_volume(volume):
    pg.mixer.music.set_volume(volume)
