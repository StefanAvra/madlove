"""Builds the browser version with pygbag.

    uv run --group web python web/build.py                 # writes build/madlove/build/web
    uv run --group web python web/build.py --serve         # builds it and serves it at http://127.0.0.1:8000
    uv run --group web python web/build.py --serve --lan   # also reachable from phones on the same network

pygbag packs a folder with a main.py, so this first copies web/main.py and the madlove package into
build/madlove. The page comes from web/madlove.tmpl, plus the files in web/static and the game's font.

The music is the smaller one from web/music (see web/make_music.py). Only the title screen's is packed with
the game; the page downloads the rest from music/ while the game runs (madlove.audio).
"""

import argparse
import functools
import http.server
import pathlib
import shutil
import socket
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'
APP_DIR = ROOT / 'build' / 'madlove'  # the folder name becomes the name of the packed game, madlove.apk
SITE_DIR = APP_DIR / 'build' / 'web'
FONT = ROOT / 'src' / 'madlove' / 'assets' / 'font' / 'PressStart2P-Regular.ttf'
MUSIC_DIR = APP_DIR / 'madlove' / 'assets' / 'sounds' / 'music'
PACKED_MUSIC = ['titlescreen.ogg']  # what the game starts with
PORT = 8000
# not 'localhost': pygbag takes pages on localhost for its own test server, and loads pygame from there
HOST = '127.0.0.1'


def stage():
    if APP_DIR.exists():
        shutil.rmtree(APP_DIR)
    shutil.copytree(ROOT / 'src' / 'madlove', APP_DIR / 'madlove', ignore=shutil.ignore_patterns('__pycache__', '.*'))
    shutil.rmtree(MUSIC_DIR)
    MUSIC_DIR.mkdir()
    for name in PACKED_MUSIC:
        shutil.copy(WEB / 'music' / name, MUSIC_DIR)
    shutil.copy(WEB / 'main.py', APP_DIR / 'main.py')


def build():
    command = [sys.executable, '-m', 'pygbag', '--build', '--title', 'MadLove', '--template', str(WEB / 'madlove.tmpl')]
    subprocess.run(command + [str(APP_DIR)], check=True)
    # after pygbag, so these files are served next to index.html but not packed into the game
    shutil.copytree(WEB / 'static', SITE_DIR, dirs_exist_ok=True)
    shutil.copytree(WEB / 'music', SITE_DIR / 'music', ignore=lambda folder, names: PACKED_MUSIC)
    shutil.copy(FONT, SITE_DIR)
    print(f'built {SITE_DIR}')


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    """serves the site without browser caching, so a rebuild shows up on reload"""

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def lan_address():
    """this computer's address in the local network (connecting a UDP socket sends nothing)"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(('192.0.2.1', 9))
            return s.getsockname()[0]
        except OSError:
            return socket.gethostname()


def serve(lan):
    host = '0.0.0.0' if lan else HOST
    handler = functools.partial(NoCacheHandler, directory=str(SITE_DIR))
    with http.server.ThreadingHTTPServer((host, PORT), handler) as server:
        print(f'serving at http://{HOST}:{PORT}')
        if lan:
            print(f'on phones in the same network: http://{lan_address()}:{PORT}')
        print('stop with Ctrl+C')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--serve', action='store_true', help=f'then serve it at http://{HOST}:{PORT}')
    parser.add_argument('--lan', action='store_true', help='with --serve, also serve it to devices in the network')
    args = parser.parse_args()

    stage()
    build()
    if args.serve:
        serve(args.lan)


if __name__ == '__main__':
    main()
