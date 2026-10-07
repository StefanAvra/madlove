"""Makes the loading spinner of the browser version, web/static/spinner.webp, from the rendered frames of the
rotating cabinet (not in the repository: Komp00.png to Komp79.png).

    uv run --with pillow python web/make_spinner.py path/to/MadLove_Small
"""

import pathlib
import sys

from PIL import Image

HEIGHT = 320  # twice the displayed height, for sharp high-density screens
FRAME_MS = 40  # 25 frames per second: one turn in 3.2 seconds
OUT = pathlib.Path(__file__).parent / 'static' / 'spinner.webp'


def main(frames_dir):
    paths = sorted(pathlib.Path(frames_dir).glob('Komp*.png'))
    frames = []
    for path in paths:
        frame = Image.open(path).convert('RGBA')
        width = round(frame.width * HEIGHT / frame.height)
        frames.append(frame.resize((width, HEIGHT), Image.LANCZOS))
    frames[0].save(
        OUT, save_all=True, append_images=frames[1:], duration=FRAME_MS, loop=0, quality=80, method=6, lossless=False
    )
    print(f'{len(frames)} frames, {frames[0].size[0]}x{HEIGHT}, {OUT.stat().st_size // 1024} KB -> {OUT}')


if __name__ == '__main__':
    main(sys.argv[1])
