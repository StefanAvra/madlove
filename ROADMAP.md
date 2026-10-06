# Roadmap

Plan for polishing MadLove after its 2019 run: make it runnable anywhere, put tests and a clean structure in place, and ship a web version.

## Known issues

- **Fact 8 is never shown.** The facts before each level skip the last one, about lawsuits, because its lines are up to 33 characters, wider than the screen. Re-wrap it to show it.
- **Scene modules import each other.** Scenes switch to each other, so for example `scenes/title.py` and `scenes/highscores.py` import one another. This works because they only look up the classes when switching, but adding module-level code that uses another scene would break it.

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

- [x] `pyproject.toml` + uv lockfile (`uv run main.py` for development, `uv run madlove` since Phase 3)
- [x] Switch `pygame` to `pygame-ce` (drop-in replacement, needed for the web build)
- [x] Remove `numpy`; replace `noise` with a small pure-Python version
- [x] Load assets relative to the code, not the working directory; save high scores in the platform's app data folder
- [x] Command-line flags instead of editing `config.py`: `--fullscreen`, `--coin-op`, `--cabinet`, `--data-dir`, `--bot`, `--show-fps`
- [x] Fix `SyntaxWarning`s from `place is 1`-style comparisons
- [x] README: how to run it for development, with controls
- [ ] README: cabinet setup on Raspberry Pi OS with uv and a systemd service (written, still needs testing on a Pi)

## Phase 2: Safety net

Tests come before the refactor, so the refactor has something to check it against.

- [x] `ruff` for linting and formatting
- [x] Headless smoke test: run with no display and no audio (`SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`), let the bot play a few thousand frames, and assert there's no crash. A second run with an idle paddle goes through game over, name entry and high scores.
- [x] Unit tests for pure logic:
  - `scores`: ranking, `get_place`, `get_penalty`, bonuses
  - `coins`
  - level parsing
- [x] Run the checks on GitHub Actions

## Phase 3: Clean-code refactor

A golden trace of two scripted games (`tests/golden/`) checked that every step left the gameplay unchanged.

- [x] Move to a `src/madlove/` package with `scenes/`, `sprites/`, `hud.py` and `audio.py`, and a `madlove` command (`uv run madlove`). Input stays in `controls.py`, since `input.py` would shadow Python's `input()`.
- [x] Replace the globals (`score`, the fonts, `time_passed`, the state in `coins` and `scores`) with an explicit game-state object: `game.Game`
- [x] Remove the import-time side effects and the circular import between the menus and the game
- [x] Fix the known bugs: the upload queue went with Firebase, the ball's default velocity is drawn per ball, and `datetime.utcnow()` is gone
- [x] Store high scores as JSON instead of pickle (no migration needed, since no 2019 score file survived)
- [x] Remove the Firebase code

## Phase 4: Web build (WebAssembly)

Use [pygbag](https://github.com/pygame-web/pygbag), which compiles CPython and pygame-ce to WebAssembly and packages the game as a static site. Check its current docs before starting.

- [x] Make `Game.run()` an `async` function that calls `await asyncio.sleep(0)` once per frame
- [x] Build with pygbag 0.9.3 (`web/build.py`; Python 3.12 in the browser) and convert the WAV sound effects to OGG
- [x] Save high scores in browser storage (`localStorage`, key `madlove.highscores`)
- [x] Default to free mode (already the default since Phase 1). The exit menu is off in the browser.
- [ ] Touch controls for phones (the 480×640 portrait layout already suits phones)
- [ ] "Click to start" screen, because browsers block audio until the player interacts. pygbag's default template waits for a click, but only shows a grey page, so it needs a custom template that says what to do.
- [ ] Polish the page: hide the focus outline around the game, and drop the "leave site?" question when reloading
- [ ] Deploy to GitHub Pages, next to the JS prototype at `stefanavra.github.io`
- [ ] Optionally also publish on itch.io
- [ ] Release `v2.0.0`

### CRT look

The original cabinet showed the game on a CRT, fed with analog composite video from the Pi. The web version should recreate that look with a shader. Expect some experimenting.

- [ ] Choose where the shader runs, e.g. a WebGL post-processing pass over pygbag's canvas in a custom HTML template
- [ ] Experiment with the effects, comparing against the teaser video and photos of the cabinet:
  - scanlines and the phosphor mask
  - composite artefacts: colour bleed, blur, dot crawl
  - screen curvature, vignette, bloom and glow
  - slight flicker or jitter
- [ ] Look at existing CRT and NTSC shaders (e.g. the libretro collection) for reference, and check their licences before reusing any code
- [ ] Add a switch to turn the effect off, and check performance on phones

## Phase 5: Optional extras

- [ ] Online leaderboard behind a small API (the Firebase admin SDK can't run in a browser and would expose credentials)
- [ ] Attract mode: a demo played by the bot
