import random
import coins


__strings = {
    'lost_life': 'YOU LOST A CIG!\nPRESS START TO LIGHT UP\nANOTHER ONE',
    'stage_text': 'STAGE: {}',
    'lives_text': 'SMOKES: {}',
    'game_over': 'GAME OVER\nCANCER FAILED\n YOUR BODY IS A TEMPLE',
    'metastasis': 'METASTASIS UNLOCKED',
    'finished': 'yeah!',
    'copyright': '© 2019 GURKIMAN, AVRA',
    'combo': 'COMBO X{}',
    'highscores_title': 'HIGHSCORES',
    'start': 'press start',
    'coin': 'insert coin',
    'credit': 'credit(s): {}'
}

__facts = {
    0: 'Smoking clogs the arteries\nand causes heart attacks\nand strokes.',
    1: 'Smoking can cause a slow\nand painful death.',
    2: 'Smoking kills.',
    3: 'Smoking causes lung, oral\nand laryngeal cancer.',
    4: 'Smoking causes\nheart disease.',
    5: 'At least four of the actors\nwho played the iconic MadLove\nMan have died of\nsmoking-related diseases.',
    6: '67% of Indonesia\'s\nmale population smokes.',
    7: 'The MadLove Man is still used\nin Japan, where smoking is\nwidespread in the male\npopulation.',
    8: 'The company that sells MadLove\ntobacco is known to sponsor legal\ncosts in lawsuits, if a country\n'
       ' happens to sue another country\nover anti-smoking laws.'
}

__combos = {
    25: 'super combo!',
    50: 'ultra combo!',
    100: 'holy moly!'
}

__credit_views = {
    0: "A project by\nGurkiman\n&\nStefan 'Avra' Avramescu",
    1: """
Game Idea by Gurkiman

Game Design by
Gurkiman and Avra

Programmed by
Avra
Code published under MIT License

Graphic Designer
Gurkiman
""",
    2: """
Music by Ozzed

in-game Font
© 2012 The Press Start 2P Project Authors (cody@zone38.net),
with Reserved Font Name "Press Start 2P".
""",
    3: """
© 2019 Gurkiman, Avra
"""
}


fact_order = [i for i in range(len(__facts) - 1)]
random.shuffle(fact_order)
current_fact = 0


def get_string(name):
    return __strings.get(name).upper()


def get_fact(number=None):
    if number is None:
        global current_fact
        number = current_fact
        current_fact += 1
        if current_fact >= len(fact_order):
            current_fact = 0
    return __facts.get(fact_order[number]).upper()


def get_combo_msg(multi):
    return __combos.get(multi)


def get_credits(view_no):
    # todo: formatting
    return __credit_views.get(view_no)

