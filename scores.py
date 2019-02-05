import config
import operator
import pickle

highscores = [('a', 323), ('b', 444), ('c', 400), ('e', 333), ('f', 5), ('t', 44), ('u', 77), ('ooo', 555),
              ('hh', 2111), ('ppp', 8), ('LOL', 999999999999)]


def load_highscores():
    global highscores
    with open(config.HIGHSCORE_FILE, 'rb') as f:
        highscores = pickle.load(f)


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

