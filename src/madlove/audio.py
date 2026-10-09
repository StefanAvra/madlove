"""Sound effects and music. Nothing starts at import: the game calls init() before pg.init()."""

import os

import pygame as pg

from madlove import config

SFX_DIR = config.asset('sounds', 'sfx')
MUSIC_DIR = config.asset('sounds', 'music')
MUSIC = ('titlescreen', 'bgm', 'smoke_break', '1stplace')  # in the order the game first plays them
sfx_lib = {}

# the browser version starts with only the title screen's music and downloads the rest while the game
# runs (web/build.py). a track asked for before its file is there waits here: its name, and the loops
# to play it with once it's there, None if play_music wasn't called for it
pending = None
pending_loops = None


def init():
    """starts the mixer and loads the sound effects. must run before pg.init(), which would start the
    mixer with its default settings"""
    pg.mixer.pre_init(44100, -16, 2, 2048)
    pg.mixer.init()
    print(f'Loading sounds from {SFX_DIR} ...')
    for filename in os.listdir(SFX_DIR):
        if filename.endswith('.ogg'):  # the only format the browser build can play
            print(f'{filename} ...')
            name = os.path.splitext(filename)[0]
            sfx_lib[name] = pg.mixer.Sound(file=os.path.join(SFX_DIR, filename))


def play_sfx(name):
    """plays a sound effect; does nothing if it isn't loaded"""
    sound = sfx_lib.get(name)
    if sound is not None:
        sound.play()


def music_path(name):
    return os.path.join(MUSIC_DIR, f'{name}.ogg')


def missing_music():
    """the tracks whose files aren't there yet, in the order the game first plays them"""
    return [name for name in MUSIC if not os.path.exists(music_path(name))]


def load_music(name):
    """loads a track for play_music. if its file is still downloading, the track waits for it (see update)"""
    global pending, pending_loops
    pending = pending_loops = None
    path = music_path(name)
    if os.path.exists(path):
        pg.mixer.music.load(path)
    else:
        pg.mixer.music.unload()  # so the track before doesn't play in its place
        pending = name


def play_music(loops=-1):
    global pending_loops
    if pending is not None:
        pending_loops = loops
    else:
        pg.mixer.music.play(loops)


def stop_music():
    global pending_loops
    pending_loops = None
    pg.mixer.music.stop()


def update():
    """the game calls this every frame: a track that was waiting for its file loads once the file is
    there, and plays if play_music was called for it"""
    if pending is not None and os.path.exists(music_path(pending)):
        loops = pending_loops
        load_music(pending)
        if loops is not None:
            play_music(loops)


def pause_music():
    pg.mixer.music.pause()


def unpause_music():
    pg.mixer.music.unpause()


def pause_all():
    """pauses the music and every sound effect that is playing"""
    pg.mixer.pause()
    pg.mixer.music.pause()


def unpause_all():
    pg.mixer.unpause()
    pg.mixer.music.unpause()


def music_busy():
    """True while music plays, or will play once its file is there"""
    return pending_loops is not None or pg.mixer.music.get_busy()


def set_music_volume(volume):
    pg.mixer.music.set_volume(volume)
