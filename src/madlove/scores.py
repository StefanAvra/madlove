"""Points, the combo multiplier, bonuses and the high-score list."""

import operator
import os
import pickle
from datetime import datetime

POINTS = {'hit_brick': 10, 'killed_brick': 20, 'phagocyte': 15, 'powerup': 85}
BONUSES = {'time_bonus': 300, 'no_continue': 20000, 'all_pus': 100000, 'clear': 20000, 'perfect': 1000000}
COMBO_TIMEOUT = 1000  # milliseconds without a hit until the multiplier drops back

DEFAULT_HIGHSCORES = [
    ('Errol', 323),
    ('Scabbers', 444),
    ('Severus', 400),
    ('Irma', 333),
    ('Granger', 500),
    ('Grawp', 44),
    ('Umbridge', 77),
    ('Rosmerta', 555),
    ('Krum', 2111),
    ('Elphias', 8),
]


class Combo:
    """the score multiplier, which grows with every hit and drops back after a second without one"""

    def __init__(self):
        self.multiplier = 0
        self.decrease_timer = 0
        self.last_multiplier = 0

    @property
    def value(self):
        return max(self.multiplier, 1)

    def is_combo(self):
        return self.multiplier >= 2

    def points(self, reason='hit_brick', no_combo=False):
        multi = 1 if no_combo else self.value
        add = POINTS[reason]
        print(f'{add} * {multi}')
        return add * multi

    def hit(self):
        self.multiplier += 1
        self.decrease_timer = 0

    def update(self, dt):
        """call this once per frame"""
        if self.multiplier > 0:
            self.decrease_timer += dt
            if self.decrease_timer > COMBO_TIMEOUT:
                self.decrease_timer = 0
                self.multiplier = 0

    def reset(self):
        self.multiplier = 0

    def new_combo(self):
        """returns the previous multiplier once after it changed, otherwise None"""
        if self.last_multiplier != self.multiplier:
            previous = self.last_multiplier
        else:
            previous = None
        self.last_multiplier = self.multiplier
        return previous


class HighScores:
    """the top ten, saved in the data folder"""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.path = os.path.join(data_dir, 'scores')
        self.entries = list(DEFAULT_HIGHSCORES)

    def load(self):
        """reads the saved list. without one, keeps the current list and saves it"""
        try:
            with open(self.path, 'rb') as f:
                self.entries = pickle.load(f)
                print('high scores loaded.')
        except OSError as error:
            print(f'HIGHSCORES COULD NOT BE LOADED: {error}')
            self.sort()
            self.save()
        self.sort()

    def save(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.path, 'wb') as f:
            pickle.dump(self.entries, f)
            print('highscores saved to local file')

    def sort(self):
        self.entries = sorted(self.entries, key=lambda t: t[1], reverse=True)[:10]

    def add(self, name, score, free_mode):
        self.entries.append((name, score, str(datetime.utcnow()), free_mode))
        self.sort()

    def highest(self):
        self.load()
        return self.entries[0][1]

    def lowest(self):
        self.load()
        return self.entries[-1][1]

    def place(self, new):
        """returns the place a new score would get, as a label ('1ST') and a number. 11 means not listed"""
        score_list = self.entries.copy()
        score_list.append(('$new', new))
        score_list.sort(key=operator.itemgetter(1), reverse=True)
        score_list = [score[0] for score in score_list]
        place = score_list.index('$new') + 1
        place_string = ''
        if place in [4, 5, 6, 7, 8, 9, 10]:
            place_string = f'{place}th'
        elif place == 1:
            place_string = '1st'
        elif place == 2:
            place_string = '2nd'
        elif place == 3:
            place_string = '3rd'
        return place_string.upper(), place


def get_penalty(score):
    penalty = score * 0.1
    if penalty > 100:
        convert_step = int(penalty / 100)
    else:
        convert_step = 1

    # the following is needed to avoid rounding issues
    factor = penalty / convert_step
    penalty = convert_step * int(factor)
    return -int(penalty), int(convert_step)


def get_bonus(bonus):
    return BONUSES.get(bonus)
