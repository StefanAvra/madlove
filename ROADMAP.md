# Roadmap

Plan for polishing MadLove after its 2019 run: make it runnable anywhere, put tests and a clean structure in place, and ship a web version.

## Known issues

- **Fact 8 is never shown.** The facts before each level skip the last one, about lawsuits, because its lines are up to 33 characters, wider than the screen. Re-wrap it to show it.
- **Scene modules import each other.** Scenes switch to each other, so for example `scenes/title.py` and `scenes/highscores.py` import one another. This works because they only look up the classes when switching, but adding module-level code that uses another scene would break it.

## Small changes

Not tied to a phase.

- [ ] **Let falling power-ups land before a level ends.** When the last brick goes, the level ends right away, even while a power-up is still falling. That power-up is neither caught nor missed, so the all-power-ups bonus (100,000 points) is still paid for it: missing one only cancels the bonus when it falls off the screen (`sprites/powerup.py`). The level should end once every falling power-up has been caught or missed. This changes the gameplay, so the golden traces may need regenerating, with the reason in the commit message.
- [x] **Debug keys only with `--debug`.** `B`, `N`, `H`, `O`/`P`, `,` and `F` during a game, and `C` and `H` on the title screen. `M` (music) stays for everyone.

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
- [x] Touch controls for phones: the cabinet's control panel (stick, Start / Pause, Action) below the game, working as a virtual joystick
- ~~Optional second touch mode: the paddle follows your finger, with its speed capped at the stick's, and a tap launches the ball~~ Not needed: the stick works well on phones
- [x] "Click to start" screen, because browsers block audio until the player interacts: our own page (`web/madlove.tmpl`) with the rotating cabinet while loading
- [x] Polish the page: no focus outline around the game, no "leave site?" question when reloading
- [ ] Test the touch controls on real phones: fine on a Pixel 7 Pro (Android), still to test on an iPhone SE 2020 (iOS Safari) once the game is on Pages
- [x] The phone froze and got hot with the game left open in a tab (Pixel 7 Pro, Brave, 2026-10-07, with the CRT shader). Nothing stopped when the page went away, and SDL's sound kept running on the main thread even when silent. Now the game, its sound and the CRT pass stop while the page is hidden or has lost focus (`madlove_page.active` in `web/static/madlove.js`), and a running level comes back in the smoke break. The CRT also drew every picture twice on 120 Hz screens, and now draws only after the game has. Confirmed on the phone
- [x] Deploy to GitHub Pages, next to the JS prototype: https://stefanavra.github.io/madlove/, published by the CI workflow on every push to master
- ~~Optionally also publish on itch.io~~ Skipped
- [x] Name all four Ozzed tracks in the README, as CC BY-SA attribution asks
- [ ] Release `v2.0.0`

### CRT look

The original cabinet showed the game on a CRT, fed with analog composite video from the Pi. The web version should recreate that look with a shader. Expect some experimenting.

- [x] Choose where the shader runs: a WebGL canvas over pygbag's canvas (`web/static/crt.js`). pygame-ce has no shaders, and in the browser it draws on the CPU. SDL draws with WebGL2, so the page asks it to keep its picture (`preserveDrawingBuffer`) and reads it as a texture every frame
- [ ] Experiment with the effects, comparing against the teaser video and photos of the cabinet:
  - [x] scanlines and the phosphor mask: vertical scanlines, because the tube stood on its side. Both are measured in game pixels, one scanline per column and one mask stripe per row, so they look the same on every screen, and fade out where the screen has under about 2 pixels per game pixel
  - composite artefacts: colour bleed, blur, dot crawl
  - [x] screen curvature and vignette
  - bloom and glow
  - slight flicker or jitter
- [x] Look at existing CRT and NTSC shaders (e.g. the libretro collection) for reference, and check their licences before reusing any code. zfast_crt_geo (GPL-2.0-or-later), the fastest in the libretro forum's benchmarks with one texture read per pixel. crt-geom-mini (MIT), the permissive alternative, is ported too, for comparing (`?crt=geom`)
- [x] Add a switch to turn the effect off: `?crt=0`
- [ ] Check performance on phones, and whether the scanlines shimmer there (480 lines across about 2.4 device pixels each)

## Phase 5: Optional extras

- [ ] Online leaderboard behind a small API (the Firebase admin SDK can't run in a browser and would expose credentials)
- [ ] Attract mode: a demo played by the bot
