import random

_strings = {
    'lost_life': 'YOU LOST A CIG!\nPRESS START TO LIGHT UP\nANOTHER ONE',
    'stage_text': 'STAGE: {}',
    'lives_text': 'SMOKES: {}',
    'game_over': 'GAME OVER\nCANCER FAILED\n YOUR BODY IS A TEMPLE',
    'metastasis': 'METASTASIS UNLOCKED',
    'finished': 'Finished Level {}!',
    'finished_lines': 'score\ntime bonus\nlevel clear\nno continue\nall powerups\nperfect',
    'copyright': '© 2019 GURKIMAN, AVRA',
    'combo': 'COMBO X{}',
    'highscores_title': 'HIGHSCORES',
    'start': 'press start',
    'coin': 'insert coin',
    'credit': 'credit(s): {}',
    'zero_lives': 'you are out of\ncigarettes!\n go get some cigs!',
    'no_cigs': 'buy more cigs\nand keep playing\n\ncontinue?',
    'consume_coins': 'score \npenalty\ncredits \ncigs ',
    'reached_level': 'level',
    'cancer_stage': 'cancer stage:',
    'end_score': 'Score: ',
    'congrats': 'congratulations!\nyou placed {}!',
    'enter_name': 'enter name:',
    'pu_shorter': 'getting shorter',
    'pu_longer': 'bigger cig!',
    'pu_pack': 'extra cig{}!',
    'pu_heartattack': 'high risk of heart attack!',
    'pu_hotball': 'hot ball!',
    'pu_shoot': 'shooting!',
    'pu_metastasis': 'metastasis!',
    'heart_killing': 'heart attack!',
    'push_to_kill': 'push button to kill!',
}

_facts = {
    0: 'Smoking clogs the arteries\nand causes heart attacks\nand strokes.',
    1: 'Smoking can cause a slow\nand painful death.',
    2: 'Smoking kills.',
    3: 'Smoking causes lung, oral\nand laryngeal cancer.',
    4: 'Smoking causes\nheart disease.',
    5: 'At least four of the actors\nwho played the iconic MadLove\nMan have died of\nsmoking-related diseases.',
    6: '67% of Indonesia\'s\nmale population smokes.',
    7: 'The MadLove Man is still used\nin Japan, where smoking is\nwidespread in the male\npopulation.',
    8: 'The company that sells MadLove\ntobacco is known to sponsor legal\ncosts in lawsuits, if a country\n'
    ' happens to sue another country\nover anti-smoking laws.',
}

_combos = {25: 'super combo!', 50: 'ultra combo!', 100: 'holy moly!'}

_credit_views = {
    0: """A project by
Christian 'Gurkiman' Angele
&
Stefan 'Avra' Avramescu""",
    1: """Game Idea by Gurkiman

Game Design by
Gurkiman & Avra

Programmed by
Avra
Code published under
MIT License

Graphic Design by
Gurkiman""",
    2: """Music by Ozzed
"Boktipset fran helvetet"
"Here Comes the 8-Bit Empire"
"About Ducks"
"8-Bit Party"


SFX by
Juhani Junkala
"The Essential Retro
Video Game Sound
Effects Collection"
""",
    3: """In-Game Font
© 2012 The Press Start 2P
Project Authors,
with Reserved Font Name
"Press Start 2P" """,
    4: """Special Thanks

Uli Veit
Trung Bui
Jo Löhmann""",
    5: """© 2019 Gurkiman, Avra""",
}

_alphabet = [chr(char) for char in range(65, 91)]
for num in range(0, 10):
    _alphabet.append(str(num))
for char in ['.', '?', '!', '-', ' ']:
    _alphabet.append(char)


def get_str(name):
    return _strings.get(name).upper()


class Facts:
    """hands out the smoking facts in a random order, starting over after the last one"""

    def __init__(self):
        # the last fact is left out, because its lines are too wide for the screen
        self.order = list(range(len(_facts) - 1))
        random.shuffle(self.order)
        self.current = 0

    def next(self):
        number = self.order[self.current]
        self.current += 1
        if self.current >= len(self.order):
            self.current = 0
        return _facts[number].upper()


def get_combo_msg(multi):
    return _combos.get(multi)


def get_credits():
    d = {}
    for key, value in _credit_views.items():
        d.update({key: value.upper()})
    return d


def get_alphabet():
    return _alphabet
