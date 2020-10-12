# MadLove

In 2018 Gurkiman posted a short animation of a breakout-style video game in which a lung was destroyed by a cigarette. When Avra asked him if this game was real, he replied "of course not". That's when the idea was born. After a quick prototype we decided to make a real arcade game.

The original MadLove Game comes with a custom built 80s style arcade cabinet with a real CRT monitor, arcade buttons and stick. And of course it is coin operated. Seasoned players are able to enter their name on the top 10 high scores list.
Avra developed the game in Python using Pygame. It features graphics by Gurkiman and Music by Ozzed.
The project premiered at the Rundgang of the State Academy of Fine Arts Stuttgart 19th - 21st of July 2019. In addition, the game was displayed in two bars in Stuttgart and was also playable in Dresden at Terz festival. The local press reported about the project. ([Stadtkind Stuttgart](https://www.stadtkind-stuttgart.de/ein-spielautomat-wandert-durch-stuttgarter-bars/), [Tagblatt](https://www.tagblatt.de/Nachrichten/In-Level-1-wird-die-Lunge-pulverisiert-427241.html))

Game Design by Gurkiman & Avra

Programmed by Avra

Graphic Design by Gurkiman


## Usage

The code is not an installable package. It was designed to run on a Raspberry Pi 3 with a resolution of 480 x 640 output through composite video. A boot script would configure the necessary settings and then run ```killyourlungs.py``` in Python 3. It is not designed to run outside the cabinet although by taking care of the dependencies it would work.

## Features
- **High scores**: players that reach a top ten high score can enter their name. It will be saved to local storage, so high scores will be kept even if powering off. Although their is code for a feature that syncs the high score list to a Firebase DB, this feature has been dropped and was never used.
- **Coin acceptor**: if the game is not running in free mode, players will have to enter a coin (0.50 €, configurable) to start the game. When the player is out of lives a countdown will appear during which the player can insert a coin to refill their lives and stay in the game.
- **8-bit aesthetics**: analog video on CRT monitor, low resolution graphics, 8 bit colour depth. (*Technically it's running on 480p for smoother gameplay.*)
- **Pause screen**: This is probably the first arcade cabinet to feature a dedicated pause button. We thought it would be good to let the smokers have a break. 
