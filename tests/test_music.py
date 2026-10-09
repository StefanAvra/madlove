"""The browser version downloads most of its music while the game runs: a track asked for before its file is
there plays once it is."""

import shutil

import pytest

from madlove import audio


class FakeMusic:
    """stands in for pygame.mixer.music, recording what the game asks of it"""

    def __init__(self):
        self.calls = []
        self.playing = False

    def load(self, path):
        self.calls.append(('load', path))

    def unload(self):
        self.calls.append(('unload',))
        self.playing = False

    def play(self, loops):
        self.calls.append(('play', loops))
        self.playing = True

    def stop(self):
        self.calls.append(('stop',))
        self.playing = False

    def get_busy(self):
        return self.playing


@pytest.fixture
def music(tmp_path, monkeypatch):
    """a music folder with only the title screen's track, as the browser version starts"""
    shutil.copy(audio.music_path('titlescreen'), tmp_path)
    monkeypatch.setattr(audio, 'MUSIC_DIR', str(tmp_path))
    monkeypatch.setattr(audio, 'pending', None)
    monkeypatch.setattr(audio, 'pending_loops', None)
    fake = FakeMusic()
    monkeypatch.setattr(audio.pg.mixer, 'music', fake)
    return fake


def arrive(name):
    """the page has downloaded the track"""
    shutil.copy(audio.config.asset('sounds', 'music', f'{name}.ogg'), audio.MUSIC_DIR)


def test_all_music_is_there_outside_the_browser():
    assert audio.missing_music() == []


def test_missing_music_in_the_order_the_game_plays_it(music):
    assert audio.missing_music() == ['bgm', 'smoke_break', '1stplace']


def test_a_track_that_is_there_plays_at_once(music):
    audio.load_music('titlescreen')
    audio.play_music(1)
    assert music.calls == [('load', audio.music_path('titlescreen')), ('play', 1)]


def test_a_missing_track_plays_once_it_arrives(music):
    audio.load_music('titlescreen')
    audio.load_music('bgm')
    audio.play_music(-1)
    assert music.calls[-1] == ('unload',)  # the title screen's music doesn't play instead
    assert audio.music_busy()  # so the scenes don't ask for it again

    audio.update()
    assert music.calls[-1] == ('unload',)

    arrive('bgm')
    audio.update()
    assert music.calls[-2:] == [('load', audio.music_path('bgm')), ('play', -1)]
    assert audio.pending is None

    music.calls.clear()
    audio.update()
    assert music.calls == []


def test_a_missing_track_that_was_not_played_only_loads(music):
    audio.load_music('bgm')
    assert not audio.music_busy()
    arrive('bgm')
    audio.update()
    assert music.calls[-1] == ('load', audio.music_path('bgm'))


def test_a_stopped_track_does_not_play_when_it_arrives(music):
    audio.load_music('bgm')
    audio.play_music(-1)
    audio.stop_music()
    assert not audio.music_busy()
    arrive('bgm')
    audio.update()
    assert music.calls[-1] == ('load', audio.music_path('bgm'))


def test_the_last_track_asked_for_is_the_one_that_plays(music):
    audio.load_music('bgm')
    audio.play_music(-1)
    audio.load_music('smoke_break')
    audio.play_music(-1)
    arrive('bgm')
    audio.update()
    assert ('load', audio.music_path('bgm')) not in music.calls
    arrive('smoke_break')
    audio.update()
    assert music.calls[-2:] == [('load', audio.music_path('smoke_break')), ('play', -1)]
