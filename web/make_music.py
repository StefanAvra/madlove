"""Makes the smaller music of the browser version, web/music/*.ogg, from Ozzed's MP3s on ozzed.net. The game's
own music, src/madlove/assets/sounds/music, came from the same MP3s at about twice the size; web/build.py puts
these in its place, so phones download about half as much.

    uv run --with soundfile python web/make_music.py

It needs ffmpeg, which decodes the MP3s without the padding at their end; the music loops, so that would be heard.
libsndfile, through soundfile, encodes them, as ffmpeg often comes without a Vorbis encoder.
"""

import pathlib
import subprocess
import tempfile
import urllib.parse
import urllib.request

import soundfile

ALBUMS = 'https://ozzed.net/files/Albums/'
TRACKS = {  # the game's name for each track: album, file, title
    'titlescreen': ('8-bit Empire', '04 Boktipset Från Helvetet.mp3', 'Boktipset Från Helvetet'),
    'bgm': ('8-bit Empire', '02 Here Comes the 8-bit Empire.mp3', 'Here Comes the 8-bit Empire'),
    '1stplace': ('8-bit Empire', '10 8-bit Party.mp3', '8-bit Party'),
    'smoke_break': ('Dunes at Night', '06 About Ducks.mp3', 'About Ducks'),
}
# libsndfile's scale, 0 for the best quality to 1 for the smallest file: 0.7 is Vorbis quality 3, about 96 kbps
COMPRESSION = 0.7
BLOCK = 65536  # libsndfile crashes when it encodes a whole track in one call
OUT = pathlib.Path(__file__).parent / 'music'


def main():
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, (album, filename, title) in TRACKS.items():
            mp3 = pathlib.Path(tmp) / f'{name}.mp3'
            wav = mp3.with_suffix('.wav')
            urllib.request.urlretrieve(ALBUMS + urllib.parse.quote(f'{album}/{filename}'), mp3)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, wav], check=True)
            ogg = OUT / f'{name}.ogg'
            with soundfile.SoundFile(wav) as source:
                with soundfile.SoundFile(
                    ogg,
                    'w',
                    source.samplerate,
                    source.channels,
                    format='OGG',
                    subtype='VORBIS',
                    compression_level=COMPRESSION,
                ) as target:
                    target.title = title
                    target.artist = 'Ozzed'
                    target.album = album
                    target.comment = 'https://ozzed.net, CC BY-SA'
                    for block in source.blocks(blocksize=BLOCK):
                        target.write(block)
            print(f'{name}: {title}, {mp3.stat().st_size // 1024} KB -> {ogg.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
