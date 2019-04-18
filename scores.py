import config
import operator
import pickle

highscores = [('Errol', 323), ('Scabbers', 444), ('Severus', 400), ('Irma', 333), ('Granger', 500), ('Grawp', 44),
              ('Umbridge', 77), ('Rosmerta', 555),
              ('Krum', 2111), ('Elphias', 8)]

__multiplier = 0
__decrease_timer = 0
__last_multi = 0

def load_highscores():
    global highscores
    with open(config.HIGHSCORE_FILE, 'rb') as f:
        highscores = pickle.load(f)
        highscores = sorted(highscores, key=lambda t: t[1], reverse=True)
        highscores = highscores[:10]


def highest_score():
    return max(highscores.items(), key=operator.itemgetter(1))


def update_highscores(new_score=None):
    global highscores
    if new_score:
        highscores.append(new_score)
    highscores = sorted(highscores, key=lambda t: t[1], reverse=True)
    highscores = highscores[:10]


def save_highscores():
    with open(config.HIGHSCORE_FILE, 'wb') as f:
        pickle.dump(highscores, f)


def increase_score(reason='hit_brick', no_combo=False):
    if no_combo:
        multi = 1
    else:
        multi = max(__multiplier, 1)
    if reason == 'hit_brick':
        add = 10
    elif reason == 'killed_brick':
        add = 20
    elif reason == 'phagocyte':
        add = 15
    elif reason == 'powerup':
        add = 85
    print('{} * {}'.format(add, multi))
    return add * multi


def increase_multiplier():
    global __multiplier
    global __decrease_timer
    __multiplier += 1
    __decrease_timer = 0


def decrease_multiplier(time_passed):
    # call this in game loop
    global __decrease_timer
    global __multiplier
    if __multiplier > 0:
        __decrease_timer += time_passed
        if __decrease_timer > 1000:
            __decrease_timer = 0
            __multiplier = 0


def is_combo():
    return __multiplier >= 2


def get_combo():
    return max(__multiplier, 1)


def get_new_combo():
    # this returns a new combo multiplier only once
    global __last_multi
    if __last_multi != __multiplier:
        return_multi = __last_multi
    else:
        return_multi = None
    __last_multi = __multiplier
    return return_multi

