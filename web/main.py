"""Entry point of the browser version, which pygbag runs. Build it with web/build.py."""

import asyncio

# pygbag only loads pygame-ce for the browser when main.py itself imports it
import pygame  # noqa: F401

from madlove import config, game

asyncio.run(game.Game(config.Settings(can_quit=False)).run())
