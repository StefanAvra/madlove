# Roadmap

Plan for polishing MadLove after its 2019 run: make it runnable anywhere, put tests and a clean structure in place, and ship a web version.

## Known issues

- **Unknown premiere build.** The last commit before the Rundgang is `b0503a6` (2019-07-18, *"dirty fix for weird bug that occurs randomly on the raspberry pi"*). Code may have been edited directly on the Pi afterwards.
- **Written for Python 3.5.** The cabinet didn't support f-strings.
- **Barely used dependencies.**
  - `numpy` is only used for `interp` and for inverting colours.
  - `noise`, an unmaintained C extension, is only used by the bot.
- **Import-time side effects.**
  - Importing `sound.py` starts the audio mixer.
  - Importing `controls.py` starts the joystick.
  - Importing `scores.py` reads and writes files.
  - `menus.py` and `killyourlungs.py` import each other.
- **Small bugs.**
  - `scores.load_queue()` opens the queue file with `'wb'`, so the queue is emptied at every start.
  - `place is 1`-style comparisons produce `SyntaxWarning`.
  - Asset paths only work when the game is started from the repo root.
- **One huge file.** `killyourlungs.py` is 2,243 lines with every scene, every sprite and globals. It does already have a single main loop with scenes, which suits the web build.

## Versioning

Semantic versioning, with git tags for the historic builds:

| Tag | Commit | Meaning |
|---|---|---|
| `v1.0.0` | `b0503a6` (2019-07-18) | Rundgang premiere build (to be confirmed against the Pi's SD card) |
| `v1.1.0` | `fff788d` (2019-10-18) | End of the 2019 tour: free mode, location/cabinet ID, online + offline high scores |
| `v2.0.0` | — | Modernised codebase, runs anywhere, web build |

Changes are recorded in `CHANGELOG.md`.

## Phase 0: Archaeology

No code changes.

- [x] Get the missing `pu_*.png` power-up images back from the Pi's SD card or old machines
- [ ] Get the 2019 high-score file back, if it still exists
- [ ] Compare the SD card's code with the repo to confirm what `v1.0.0` really was
- [ ] Tag `v1.0.0` and `v1.1.0`
- [ ] Write `CHANGELOG.md` with the two historic entries, taken from the commit log
- [ ] Clarify asset licensing before any public release:
  - MIT covers the code
  - the music (Ozzed, CC BY-SA) and font (OFL) may be redistributed with credit
  - Gurkiman's graphics need explicit permission

## Phase 1: Make it runnable

- [ ] `pyproject.toml` + uv lockfile (`uv run madlove` for development)
- [ ] Switch `pygame` to `pygame-ce` (drop-in replacement, needed for the web build)
- [ ] Remove `numpy`; replace `noise` with a small pure-Python version
- [ ] Load assets relative to the package folder, not the working directory
- [ ] Command-line flags or environment variables instead of editing `config.py`: `--fullscreen`, `--free-mode`, `--cabinet`
- [ ] README: how to run it for development
- [ ] README: cabinet setup on Raspberry Pi OS, using a venv (recent Raspberry Pi OS blocks global `pip install`) and a systemd service instead of the old boot script

## Phase 2: Safety net

Tests come before the refactor, so the refactor has something to check it against.

- [ ] `ruff` for linting and formatting
- [ ] Headless smoke test: run with no display and no audio (`SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`), let the bot play a few thousand frames, and assert there's no crash
- [ ] Unit tests for pure logic:
  - `scores`: ranking, `get_place`, `get_penalty`, bonuses
  - `coins`
  - level parsing
- [ ] Run the checks on GitHub Actions

## Phase 3: Clean-code refactor

- [ ] Move to a `src/madlove/` package with `scenes/`, `sprites/`, `hud.py`, `audio.py` and `input.py`
- [ ] Replace the globals (`score`, the fonts, `time_passed`, the state in `coins` and `scores`) with an explicit game-state object
- [ ] Remove the import-time side effects and the circular import
- [ ] Fix the known bugs listed above
- [ ] Store high scores as JSON instead of pickle, with a one-time migration from the 2019 format
- [ ] Remove the Firebase code or move it behind an optional extra
- [ ] Release `v2.0.0`

## Phase 4: Web build (WebAssembly)

Use [pygbag](https://github.com/pygame-web/pygbag), which compiles CPython and pygame-ce to WebAssembly and packages the game as a static site. Check its current docs before starting.

- [ ] Make `main()` an `async` function that calls `await asyncio.sleep(0)` once per frame
- [ ] Save high scores in browser storage
- [ ] Default to free mode, or add an on-screen coin/start button
- [ ] Touch controls for phones (the 480×640 portrait layout already suits phones)
- [ ] "Click to start" screen, because browsers block audio until the player interacts
- [ ] Deploy to GitHub Pages, next to the JS prototype at `stefanavra.github.io`
- [ ] Optionally also publish on itch.io

## Phase 5: Optional extras

- [ ] Online leaderboard behind a small API (the Firebase admin SDK can't run in a browser and would expose credentials)
- [ ] Attract mode: a demo played by the bot
- [ ] 2019 hall of fame with the original cabinet high scores
