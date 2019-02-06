import config
import operator
import pickle

highscores = [('Errol', 323), ('Scabbers', 444), ('Severus', 400), ('Irma', 333), ('Granger', 500), ('Grawp', 44), ('Umbridge', 77), ('Rosmerta', 555),
              ('Krum', 2111), ('Elphias', 8)]

multiplier = 1


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


def increase_score(reason='hit_brick'):
    if reason == 'hit_brick':
        add = 10
    elif reason == 'killed_brick':
        add = 20
    elif reason == 'phagocyte':
        add = 15
    elif reason == 'powerup':
        add = 85
    return add * multiplier

