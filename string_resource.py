__strings = {
    'lost_life': 'YOU LOST A CIG!\nPRESS START TO LIGHT UP\nANOTHER ONE',
    'stage_text': 'STAGE: {}',
    'lives_text': 'SMOKES: {}',
    'game_over': 'GAME OVER\nCANCER FAILED\n YOUR BODY IS A TEMPLE',
    'metastasis': 'METASTASIS UNLOCKED',
    'finished': 'YOU KILLED THESE LUNGS!',
    'copyright': '© 2019 GURKIMAN, AVRA',
    'combo': 'COMBO BONUS X{}'
}


def get_string(name):
    return __strings.get(name)
