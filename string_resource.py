import random


__strings = {
    'lost_life': 'YOU LOST A CIG!\nPRESS START TO LIGHT UP\nANOTHER ONE',
    'stage_text': 'STAGE: {}',
    'lives_text': 'SMOKES: {}',
    'game_over': 'GAME OVER\nCANCER FAILED\n YOUR BODY IS A TEMPLE',
    'metastasis': 'METASTASIS UNLOCKED',
    'finished': 'YOU KILLED THESE LUNGS!',
    'copyright': '© 2019 GURKIMAN, AVRA',
    'combo': 'COMBO X{}',
    'highscores_title': 'HIGHSCORES'
}

__facts = {
    0: 'Smoking clogs the arteries and causes heart attacks and strokes.',
    1: 'Smoking can cause a slow and painful death.',
    2: 'Smoking kills.',
    3: 'Smoking causes lung, oral and laryngeal cancer.',
    4: 'Smoking causes heart disease.',
    5: 'At least four of the actors who played the Marlboro Man have died of smoking-related diseases.',
    6: '67% of Indonesia\'s male popularity smokes.',
    7: 'The Marlboro Man is still used in Japan, where smoking is widespread in the male population.',
    8: 'Philip Morris (the company that sells Marlboro) is known to sponsor legal costs in lawsuits, if a country'
       ' happens to sue another country over anti-smoking laws.'
}

__combos = {
    25: 'super combo!',
    50: 'ultra combo!',
    100: 'holy moly!'
}

fact_order = [i for i in range(len(__facts) - 1)]
random.shuffle(fact_order)
current_fact = 0


def get_string(name):
    return __strings.get(name)


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
