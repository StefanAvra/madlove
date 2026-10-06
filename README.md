# MadLove

[![CI](https://github.com/StefanAvra/madlove/actions/workflows/ci.yml/badge.svg)](https://github.com/StefanAvra/madlove/actions/workflows/ci.yml)

In 2018 Gurkiman posted a short animation of a breakout-style video game in which a lung was destroyed by a cigarette. When Avra asked him if this game was real, he replied "of course not". That's when the idea was born. After a quick [prototype](https://stefanavra.github.io/kill-yo-lungs-js/) we decided to make a real arcade game.

The original MadLove Game comes with a custom built 80s style arcade cabinet with a real CRT monitor, arcade buttons and stick. And of course it is coin operated. Seasoned players are able to enter their name on the top 10 high scores list.
Avra developed the game in Python using Pygame. It features graphics by Gurkiman and Music by Ozzed.
The project premiered at the Rundgang of the State Academy of Fine Arts Stuttgart 19th - 21st of July 2019. In addition, the game was displayed in two bars in Stuttgart and was also playable in Dresden at Terz festival. The local press reported about the project. ([Stadtkind Stuttgart](https://web.archive.org/web/20201001202834/https://www.stadtkind-stuttgart.de/ein-spielautomat-wandert-durch-stuttgarter-bars/), [Tagblatt](https://www.pressreader.com/germany/haller-tagblatt/20190830/282754883372114))

Game Design by Gurkiman & Avra

Programmed by Avra

Graphic Design by Gurkiman

Music by [Ozzed](https://ozzed.net/) under Creative Commons license (CC BY-SA):
- "About Ducks"
- "Boktipset från helvetet"
- "Here Comes the 8-Bit Empire"
- "8-Bit Party"


[Teaser Video on Youtube](https://www.youtube.com/watch?v=CY5pmC3nwCw)


## Running the game

You need [uv](https://docs.astral.sh/uv/getting-started/installation/), which installs the right Python version and the dependencies into a project-local virtual environment (`.venv`).

```sh
git clone https://github.com/StefanAvra/madlove.git
cd madlove
uv run madlove
```

The game opens in a 480 × 640 window in free play mode. Options:

| Option | Effect |
|---|---|
| `--fullscreen` | Run in fullscreen, scaled to fit the screen |
| `--coin-op` | Require coins to play (press `1` to insert one) |
| `--cabinet` | Arcade cabinet settings: same as `--fullscreen --coin-op` |
| `--data-dir PATH` | Where high scores are saved (default: your platform's app data folder) |
| `--bot` | Let the bot play |
| `--show-fps` | Show frames per second |
| `--version` | Print the version |

### Controls

| Action | Keyboard | Arcade cabinet |
|---|---|---|
| Move the paddle | ← → | Stick |
| Navigate menus, change letters of your name | ↑ ↓ | Stick |
| Start a game | Space / Enter | Start button |
| Launch the ball, confirm your name | Space | Action button |
| Smoke break (pause) | Esc | Start button |
| Insert coin | 1 | Coin acceptor |
| Toggle music | M | — |

Debug keys during a game: `B` adds a ball, `N` clears the level, `H` gives the shooting power-up, `O`/`P` slow down/speed up the balls, `F` shows FPS and ball velocity, `,` toggles the bot.

### Development

```sh
uv run pytest            # tests, including a headless run of the whole game
uv run ruff check .      # lint
uv run ruff format .     # format
```

GitHub Actions runs all three on every push. To make `git blame` skip formatting-only commits, run `git config blame.ignoreRevsFile .git-blame-ignore-revs` once.

The code lives in `src/madlove/`: `game.py` has the main loop and the `Game` object that holds the state of a running game, `scenes/` has one module per screen, and `sprites/` has the ball, paddle, bricks and the rest.

The smoke test plays two scripted games and compares every scene change, with its frame and score, against `tests/golden/`. If a change to the gameplay is intended, regenerate the traces with `MADLOVE_UPDATE_GOLDEN=1 uv run pytest tests/test_smoke.py` and say why in the commit message.

### Web version

The browser version is built with [pygbag](https://github.com/pygame-web/pygbag), which runs Python and pygame-ce as WebAssembly. It plays in free mode, saves high scores in the browser's local storage and has no exit menu.

```sh
uv run --group web python web/build.py --serve         # build it and play it at http://127.0.0.1:8000
uv run --group web python web/build.py --serve --lan   # also playable on phones in the same Wi-Fi
uv run --group web python web/build.py                 # only build it, into build/madlove/build/web
```

The page is `web/madlove.tmpl`, with its styles and scripts in `web/static/`. While the game loads, it shows the rotating cabinet. Then it asks for a click, tap or key press, because browsers only play sound after the player has interacted with the page. The page loads the Python runtime from pygbag's CDN, so building and playing need an internet connection.

On touch screens, the page shows the cabinet's control panel below the game, or on both sides of it in landscape: the stick, Start / Pause and Action. It works like the cabinet's joystick, so every screen behaves as on the cabinet. Add `?touch=1` to the address to show it anywhere, or `?touch=0` to hide it.

### Raspberry Pi cabinet

The game was designed to run on a Raspberry Pi 3 with a 480 × 640 picture on a CRT over composite video. The original SD card, with its boot script and display settings, is lost. These steps are a starting point and **have not yet been tested on a Pi**.

1. Install the 64-bit Raspberry Pi OS Lite. pygame-ce publishes ready-made packages for 64-bit ARM only.
2. Set up composite output and the resolution in `/boot/firmware/config.txt`.
3. Install uv and the game:

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   git clone https://github.com/StefanAvra/madlove.git ~/madlove
   cd ~/madlove
   uv sync
   ```

   Recent Raspberry Pi OS versions don't allow `pip install` into the system Python. uv installs everything into `~/madlove/.venv` instead.
4. Start the game at boot with a systemd service. Save this as `/etc/systemd/system/madlove.service`, replacing `pi` with your user name:

   ```ini
   [Unit]
   Description=MadLove arcade game
   After=multi-user.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/madlove
   ExecStart=/home/pi/.local/bin/uv run --frozen madlove --cabinet
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Then enable it with `sudo systemctl enable --now madlove`.

## Versions

See [CHANGELOG.md](CHANGELOG.md). `v1.0.0` is the build that premiered at the Rundgang in July 2019, `v1.1.0` the one that toured afterwards. Plans for the future are in [ROADMAP.md](ROADMAP.md).

## Features
- **High scores**: players that reach a top ten high score can enter their name. It will be saved to local storage, so high scores will be kept even if powering off. An online high score list synced to Firebase was written in 2019 but never used; its code was removed in version 2.
- **Coin acceptor**: if the game is not running in free mode, players will have to enter a coin (0.50 €, configurable) to start the game. When the player is out of lives a countdown will appear during which the player can insert a coin to refill their lives and stay in the game.
- **8-bit aesthetics**: analog video on CRT monitor, low resolution graphics, 8 bit colour depth. (*Technically it's running on 480p for smoother gameplay.*)
- **Pause screen**: This is probably the first arcade cabinet to feature a dedicated pause button. We thought it would be good to let the smokers have a break. 
