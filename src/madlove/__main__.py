"""Starts MadLove. Run with `uv run madlove --help` to see the options."""

import argparse
import importlib.metadata

import pygame as pg

from madlove import config


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog='madlove', description='MadLove - the arcade game.')
    parser.add_argument('--version', action='version', version=f"%(prog)s {importlib.metadata.version('madlove')}")
    parser.add_argument('--fullscreen', action='store_true', help='run in fullscreen')
    parser.add_argument('--coin-op', action='store_true', help='require coins to play (default: free play)')
    parser.add_argument(
        '--cabinet', action='store_true', help='settings for the arcade cabinet: same as --fullscreen --coin-op'
    )
    parser.add_argument(
        '--data-dir', default=config.DATA_DIR, help='where high scores are saved (default: %(default)s)'
    )
    parser.add_argument('--bot', action='store_true', help='let the bot play')
    parser.add_argument('--show-fps', action='store_true', help='show frames per second')
    return parser.parse_args(argv)


def apply_args(args):
    """writes the command line options into config. must run before the game modules are imported"""
    if args.fullscreen or args.cabinet:
        config.FLAGS |= pg.FULLSCREEN
    config.FREE_MODE = not (args.coin_op or args.cabinet)
    config.ENABLE_BOT = args.bot
    config.SHOW_FPS = args.show_fps
    config.set_data_dir(args.data_dir)


def run(argv=None):
    apply_args(parse_args(argv))
    # imported here because these modules read config when they are imported
    from madlove import killyourlungs

    killyourlungs.main()


if __name__ == '__main__':
    run()
