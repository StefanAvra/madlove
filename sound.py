import os

import pygame as pg

import config

pg.mixer.pre_init(44100, -16, 2, 2048)
pg.mixer.init()

hit_will = None
bgm = None
SFX_DIR = config.asset('sounds', 'sfx')
MUSIC_DIR = config.asset('sounds', 'music')
sfx_lib = {}
music_lib = {}


print(f'Loading sounds from {SFX_DIR} ...')
for filename in os.listdir(SFX_DIR):
    if filename.endswith('.ogg') or filename.endswith('.wav'):
        print(f'{filename} ...')
        name = os.path.splitext(filename)[0]
        sound = pg.mixer.Sound(file=os.path.join(SFX_DIR, filename))
        sfx_lib[name] = sound
