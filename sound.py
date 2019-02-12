import pygame as pg
import os

pg.mixer.pre_init(44100, -16, 2, 2048)
pg.mixer.init()

hit_will = None
bgm = None
SFX_DIR = 'assets/sounds/sfx'
MUSIC_DIR = 'assets/sounds/music'
sfx_lib = {}
music_lib = {}


print('Loading sounds from {} ...'.format(SFX_DIR))
for filename in os.listdir(SFX_DIR):
    if filename.endswith('.ogg') or filename.endswith('.wav'):
        print('{} ...'.format(filename))
        name = os.path.splitext(filename)[0]
        sound = pg.mixer.Sound(file=os.path.join(SFX_DIR, filename))
        sfx_lib[name] = sound

