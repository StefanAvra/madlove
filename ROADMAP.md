# Roadmap

Plan for polishing MadLove after its 2019 run: make it runnable anywhere, put tests and a clean structure in place, and ship a web version.

## Known issues

- **Import-time side effects.**
  - Importing `sound.py` starts the audio mixer.
  - Importing `controls.py` starts the joystick.
  - Importing `scores.py` reads and writes files.
  - `menus.py` and `killyourlungs.py` import each other.
- **Upload queue bug.** `scores.load_queue()` opens the queue file with `'wb'`, so the queue is emptied at every start. Just fixing the mode would make the queue grow forever in offline mode, so fix it together with the high-score rework in Phase 3.
- **One huge file.** `killyourlungs.py` is 2,243 lines with every scene, every sprite and globals. It does already have a single main loop with scenes, which suits the web build.

## Versioning

Semantic versioning, with git tags for the historic builds:

| Tag | Commit | Meaning |
|---|---|---|
| `v1.0.0` | `b0503a6` (2019-07-18) | Rundgang premiere build (the SD card is lost, so the last commit before the premiere is assumed to be it) |
| `v1.1.0` | `fff788d` (2019-10-18) | End of the 2019 tour: free mode, location/cabinet ID, online + offline high scores |
| `v2.0.0` | — | Modernised codebase, runs anywhere, web build |

Changes are recorded in `CHANGELOG.md`.

## Phase 0: Archaeology

No code changes.

- [x] Get the missing `pu_*.png` power-up images back from the Pi's SD card or old machines
- [x] Tag `v1.0.0` and `v1.1.0`
- [x] Write `CHANGELOG.md` with the two historic entries, taken from the commit log
- [x] Clarify asset licensing before any public release:
  - MIT covers the code
  - the music (Ozzed, CC BY-SA) and font (OFL) may be redistributed with credit
  - Gurkiman approved publishing the graphics with the web version (2026-10-06)

## Phase 1: Make it runnable

- [x] `pyproject.toml` + uv lockfile (`uv run main.py` for development)
- [x] Switch `pygame` to `pygame-ce` (drop-in replacement, needed for the web build)
- [x] Remove `numpy`; replace `noise` with a small pure-Python version
- [x] Load assets relative to the code, not the working directory; save high scores in the platform's app data folder
- [x] Command-line flags instead of editing `config.py`: `--fullscreen`, `--coin-op`, `--cabinet`, `--data-dir`, `--bot`, `--show-fps`
- [x] Fix `SyntaxWarning`s from `place is 1`-style comparisons
- [x] README: how to run it for development, with controls
- [ ] README: cabinet setup on Raspberry Pi OS with uv and a systemd service (written, still needs testing on a Pi)

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

- [ ] Move to a `src/madlove/` package with `scenes/`, `sprites/`, `hud.py`, `audio.py` and `input.py`, and a `madlove` command (`uv run madlove`)
- [ ] Replace the globals (`score`, the fonts, `time_passed`, the state in `coins` and `scores`) with an explicit game-state object
- [ ] Remove the import-time side effects and the circular import
- [ ] Fix the known bugs listed above
- [ ] Store high scores as JSON instead of pickle (no migration needed, since no 2019 score file survived)
- [ ] Remove the Firebase code (its dependency is already only an optional `online` extra)
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
