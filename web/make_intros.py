"""Makes the smaller level intro photos of the browser version, web/graphics/level_intro_*.png, from the game's
own in src/madlove/assets/graphics. Those have thousands of colours; these have 256, at about a seventh of the
size, and web/build.py puts them in their place. The rest of the intro screen comes from the other graphics
(madlove.scenes.intro).

    uv run --with pillow python web/make_intros.py

Pillow's octree keeps the photos' colours better than median cut; the photos are dithered already, so
dithering them again would only add noise.
"""

import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'src' / 'madlove' / 'assets' / 'graphics'
OUT = pathlib.Path(__file__).parent / 'graphics'


def main():
    OUT.mkdir(exist_ok=True)
    for source in sorted(SOURCE.glob('level_intro_*.png')):
        target = OUT / source.name
        with Image.open(source) as image:
            image = image.convert('RGB').quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
            image.save(target, optimize=True)
        print(f'{source.name}: {source.stat().st_size // 1024} KB -> {target.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
