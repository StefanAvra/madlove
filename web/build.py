"""Builds the browser version with pygbag.

    uv run --group web python web/build.py           # writes build/madlove/build/web
    uv run --group web python web/build.py --serve   # builds it and serves it at http://localhost:8000

pygbag packs a folder with a main.py, so this first copies web/main.py and the madlove package into
build/madlove.
"""

import argparse
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_DIR = ROOT / 'build' / 'madlove'  # the folder name becomes the name of the packed game, madlove.apk


def stage():
    if APP_DIR.exists():
        shutil.rmtree(APP_DIR)
    shutil.copytree(ROOT / 'src' / 'madlove', APP_DIR / 'madlove', ignore=shutil.ignore_patterns('__pycache__', '.*'))
    shutil.copy(ROOT / 'web' / 'main.py', APP_DIR / 'main.py')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--serve', action='store_true', help='serve the game at http://localhost:8000 after building')
    args = parser.parse_args()

    stage()
    command = [sys.executable, '-m', 'pygbag', '--title', 'MadLove']
    if not args.serve:
        command.append('--build')
    command.append(str(APP_DIR))
    subprocess.run(command, check=True)
    if not args.serve:
        print(f'built {APP_DIR / "build" / "web"}')


if __name__ == '__main__':
    main()
