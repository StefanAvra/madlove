"""Points, the combo multiplier, bonuses and the high-score list."""

import dataclasses
import json
from datetime import UTC, datetime

POINTS = {'hit_brick': 10, 'killed_brick': 20, 'phagocyte': 15, 'powerup': 85}
BONUSES = {'time_bonus': 300, 'no_continue': 20000, 'all_pus': 100000, 'clear': 20000, 'perfect': 1000000}
COMBO_TIMEOUT = 1000  # milliseconds without a hit until the multiplier drops back


@dataclasses.dataclass
class Entry:
    name: str
    score: int
    date: str | None = None  # when it was played, ISO 8601 in UTC
    free_mode: bool | None = None  # whether it was played without coins


DEFAULT_HIGHSCORES = [
    Entry('Errol', 323),
    Entry('Scabbers', 444),
    Entry('Severus', 400),
    Entry('Irma', 333),
    Entry('Granger', 500),
    Entry('Grawp', 44),
    Entry('Umbridge', 77),
    Entry('Rosmerta', 555),
    Entry('Krum', 2111),
    Entry('Elphias', 8),
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
    """the top ten, saved as JSON in a store from madlove.storage"""

    def __init__(self, store):
        self.store = store
        self.entries = list(DEFAULT_HIGHSCORES)

    def load(self):
        """reads the saved list. without a readable one, keeps the current list and saves it"""
        try:
            self.entries = [Entry(**entry) for entry in json.loads(self.store.read())]
            print('high scores loaded.')
        except (OSError, ValueError, TypeError) as error:
            print(f'HIGHSCORES COULD NOT BE LOADED: {error}')
            self.sort()
            self.save()
        self.sort()

    def save(self):
        self.store.write(
            json.dumps([dataclasses.asdict(entry) for entry in self.entries], indent=2, ensure_ascii=False)
        )
        print('high scores saved.')

    def sort(self):
        self.entries = sorted(self.entries, key=lambda entry: entry.score, reverse=True)[:10]

    def add(self, name, score, free_mode):
        self.entries.append(Entry(name, score, datetime.now(UTC).isoformat(timespec='seconds'), free_mode))
        self.sort()

    def highest(self):
        self.load()
        return self.entries[0].score

    def lowest(self):
        self.load()
        return self.entries[-1].score

    def place(self, new):
        """returns the place a new score would get, as a label ('1ST') and a number. 11 means not listed.
        a tie ranks below the score that was there first"""
        place = 1 + sum(entry.score >= new for entry in self.entries)
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
