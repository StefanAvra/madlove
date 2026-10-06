# Changelog

All notable changes to MadLove are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `ROADMAP.md` with the plan for modernising the game and bringing it to the web.
- `pyproject.toml` and `uv.lock`: run the game with `uv run main.py`.
- `main.py` entry point with command-line options: `--fullscreen`, `--coin-op`, `--cabinet`, `--data-dir`, `--bot`, `--show-fps` and `--version`.
- README instructions for running the game, its controls and setting up a Raspberry Pi cabinet.

### Changed
- Switched from `pygame` to `pygame-ce`, the actively maintained fork. Requires Python 3.11 or newer.
- Free play is the default; coins are only required with `--coin-op` or `--cabinet`.
- The window uses pygame's `SCALED` mode, so the game always draws on an opaque surface. In fullscreen the picture is scaled to fit with black bars, instead of switching the screen resolution.
- High scores are saved in the platform's app data folder instead of the current directory.
- `firebase-admin` is now an optional dependency (`online` extra).

### Removed
- `numpy` and `noise` dependencies, replaced by small built-in helpers.

### Fixed
- Assets load no matter which directory the game is started from.
- `SyntaxWarning`s on modern Python from `is` comparisons with numbers.
- The background colour lost its opacity after the first screen fade, because `render_fading()` modified the shared colour instead of a copy. This was invisible on the 2019 cabinet, but in windows with an alpha channel, such as on macOS, the logo and text were drawn with black or white boxes around them.
- Power-up graphics (`pu_hotball`, `pu_longer`, `pu_metastasis`, `pu_shoot`, `pu_shorter`) were never committed, so a fresh checkout crashed when a power-up dropped. They have been recovered and added.

## [1.1.0] - 2019-10-18

The version that toured Stuttgart bars and the Terz festival in Dresden after the premiere.

### Added
- Free mode, enabled in `config.py`, for playing without a coin acceptor.
- High scores record the date, the free-mode setting, the location and a cabinet ID.
- Online high-score list synced to Firebase, with a local upload queue for when there's no connection.
- Offline mode that disables the online high-score list. This was the mode actually used.

### Changed
- High scores below 10th place are kept but not shown; storage was later limited to 10 entries again.

### Fixed
- The game always asked for a name, even without a high score.
- A critical bug that could delete the high-score list.
- The combo multiplier carried over into a new game.

## [1.0.0] - 2019-07-18

The premiere build, shown at the Rundgang of the State Academy of Fine Arts Stuttgart, 19–21 July 2019. It ran on a Raspberry Pi 3 inside the arcade cabinet with a CRT monitor, arcade stick and buttons, and a coin acceptor.

### Added
- Breakout gameplay: lung-shaped levels built from tile maps, a ball and a paddle, combos, and four paddle sizes.
- Power-ups: longer and shorter paddle, extra cigarette pack (life), shooting, hot ball, metastasis and heart attack.
- Time, clear, perfect-play, no-continue and all-power-ups bonuses between levels.
- Coin acceptor support: a credit display, consuming credits, and a continue countdown where inserting a coin keeps you in the game, at a 10% score penalty.
- Top-10 high-score list saved locally, with name entry using the joystick.
- Scenes: intro, title screen, attract mode (cycling between the title and high scores), level intros, game over, continue, credits.
- The "smoke break": a pause screen on a dedicated pause button.
- Smoking facts shown in random order during play.
- Music by Ozzed, sound effects, and the Press Start 2P font.
- Gamepad and arcade-stick controls.
- A simple bot that plays the game, for debugging.

[Unreleased]: https://github.com/StefanAvra/madlove/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/StefanAvra/madlove/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/StefanAvra/madlove/releases/tag/v1.0.0
