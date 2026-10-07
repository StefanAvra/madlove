"""Starts MadLove. Run with `uv run madlove --help` to see the options."""

import argparse
import importlib.metadata

from madlove import config, game


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog='madlove', description='MadLove - the arcade game.')
    parser.add_argument('--version', action='version', version=f"%(prog)s {importlib.metadata.version('madlove')}")
    parser.add_argument('--fullscreen', action='store_true', help='run in fullscreen')
    parser.add_argument('--coin-op', action='store_true', help='require coins to play (default: free play)')
    parser.add_argument(
        '--cabinet', action='store_true', help='settings for the arcade cabinet: same as --fullscreen --coin-op'
    )
    parser.add_argument(
        '--data-dir', default=config.default_data_dir(), help='where high scores are saved (default: %(default)s)'
    )
    parser.add_argument('--bot', action='store_true', help='let the bot play')
    parser.add_argument('--show-fps', action='store_true', help='show frames per second')
    parser.add_argument('--debug', action='store_true', help='enable the debug keys (see the README)')
    return parser.parse_args(argv)


def settings_from_args(args):
    return config.Settings(
        fullscreen=args.fullscreen or args.cabinet,
        free_mode=not (args.coin_op or args.cabinet),
        bot=args.bot,
        show_fps=args.show_fps,
        debug=args.debug,
        data_dir=args.data_dir,
    )


def run(argv=None):
    game.main(settings_from_args(parse_args(argv)))


if __name__ == '__main__':
    run()
