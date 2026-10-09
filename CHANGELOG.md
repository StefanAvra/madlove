# Changelog

All notable changes to MadLove are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- The browser version's start screen warns when the screen is held at 30 frames per second, as iOS's Low Power Mode does, because the game then shows only every other step. Browsers don't tell a page about Low Power Mode, so it measures the time between frames. `?fps=1` shows what it measures.

### Changed
- The game moves in fixed steps of 1/60 s and runs as many per picture as the time since the last one, up to three, so it plays at the same speed on screens slower than 60 frames per second, such as Safari's 30 in Low Power Mode, where it played at half speed. Every step moves the ball as far as before and checks its collisions, so it hits, and clips, the same bricks at any frame rate. The fades and the heart attack's flashing count steps too. Below 20 frames per second the game slows down.

## [2.1.0] - 2026-10-09

The browser version starts with a 2.2 MB download instead of 7.3 MB, shows how far it has loaded, and does less work every frame.

### Added
- A favicon and home-screen icon for the browser version, and the MadLove logo at the top of the README, made from the title screen's graphics by `web/make_logo.py`.
- The browser version's start screen shows the loading progress: the cabinet turns black and white and fills with colour from the bottom as the game loads.

### Changed
- The browser version's music is about half the size of the game's own, made by `web/make_music.py` from Ozzed's MP3s. Only the title screen's track comes with the game; the others download while it runs, and a track asked for before it has arrived starts as soon as it does.
- The level intro images only hold the photo. The black space for the fact's text and the pack's logo below the photo are drawn from the title screen's graphics, in the same pink as the rest of the game. The browser version's photos have 256 colours, made by `web/make_intros.py`.
- Less work every frame: the HUD's cigarette pack and the bricks' images are loaded once, the HUD's text is only rendered when it changes, and the fades and the heart attack reuse one surface instead of making a new one each frame.
- A better transition for the buttons on the browser version's control panel.
- `M` (music) is a debug key, only with `--debug`, and is no longer listed in the browser version's footer.

## [2.0.0] - 2026-10-07

The 2019 game made runnable anywhere: a Python package with tests and command-line options, and a browser version with the cabinet's controls and a CRT look, playable at https://stefanavra.github.io/madlove/.

### Added
- `ROADMAP.md` with the plan for modernising the game and bringing it to the web.
- `pyproject.toml` and `uv.lock`: run the game with `uv run madlove`.
- `madlove` command with command-line options: `--fullscreen`, `--coin-op`, `--cabinet`, `--data-dir`, `--bot`, `--show-fps`, `--debug` and `--version`.
- README instructions for running the game, its controls and setting up a Raspberry Pi cabinet.
- Tests (`uv run pytest`): a headless smoke test that plays the whole game and compares it against a recorded trace, and unit tests for scores, coins and the level data.
- Linting and formatting with ruff.
- GitHub Actions workflow that runs the linter, the format check and the tests.
- A browser version built with pygbag (`web/build.py`). It saves high scores in the browser's local storage and has no exit menu.
- The browser version's own page: a start screen with a rotating 3D cabinet, and on touch screens the cabinet's control panel with the stick and the Start / Pause and Action buttons.
- A CRT look for the browser version: the cabinet's tube on its side, with vertical scanlines, a slight curve and the phosphor mask, from libretro's zfast_crt_geo shader (GPL-2.0-or-later). `?crt=geom` switches to libretro's crt-geom-mini (MIT), `?crt=0` turns it off.
- The browser version is online at https://stefanavra.github.io/madlove/. GitHub Actions builds and publishes it on every push to master, once the checks pass.

### Changed
- Switched from `pygame` to `pygame-ce`, the actively maintained fork. Requires Python 3.11 or newer.
- Free play is the default; coins are only required with `--coin-op` or `--cabinet`.
- The window uses pygame's `SCALED` mode, so the game always draws on an opaque surface. In fullscreen the picture is scaled to fit with black bars, instead of switching the screen resolution.
- High scores are saved as JSON (`highscores.json`) in the platform's app data folder, instead of a pickle file in the current directory. Each entry records the date in UTC and whether it was played in free mode.
- The code is a Python package in `src/madlove/`, installed with the `madlove` command. The 2,000-line `killyourlungs.py` is split into scenes, sprites and a `Game` object that holds the state of a running game; nothing starts or reads files at import any more.
- Choosing YES in the exit menu ends the main loop instead of calling `sys.exit()`.
- The main loop is async, so the same code runs in the browser.
- The debug keys (extra ball, clearing the level, shooting power-up, ball speed, bot, FPS display, and the credits and high-score shortcuts on the title screen) only work with `--debug`, so players can't trigger them by accident.
- The sound effects are OGG instead of WAV, because the browser version can only play OGG.

### Removed
- `numpy` and `noise` dependencies, replaced by small built-in helpers.
- The unused Firebase code for an online high-score list, with its upload queue and the location and cabinet ID it recorded.

### Fixed
- Assets load no matter which directory the game is started from.
- `SyntaxWarning`s on modern Python from `is` comparisons with numbers.
- The background colour lost its opacity after the first screen fade, because `render_fading()` modified the shared colour instead of a copy. This was invisible on the 2019 cabinet, but in windows with an alpha channel, such as on macOS, the logo and text were drawn with black or white boxes around them.
- Every ball added with the debug key `B` started in the same direction, because the default velocity was drawn only once.
- Holding the stick up or down on the name entry repeated letters in the opposite direction, because the held stick's up and down were swapped.
- Power-up graphics (`pu_hotball`, `pu_longer`, `pu_metastasis`, `pu_shoot`, `pu_shorter`) were never committed, so a fresh checkout crashed when a power-up dropped. They have been recovered and added.
- The browser version kept running, sound and CRT effect included, while its page was hidden or had lost focus, and a phone left with the game open in a tab got hot. Now everything stops until the page is back, and a running level comes back in the smoke break.
- The CRT effect drew every picture twice on 120 Hz screens. It now draws only when the game has drawn a new one.

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

[Unreleased]: https://github.com/StefanAvra/madlove/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/StefanAvra/madlove/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/StefanAvra/madlove/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/StefanAvra/madlove/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/StefanAvra/madlove/releases/tag/v1.0.0
