import pickle

import pytest

from madlove import scores
from madlove.scores import Combo, HighScores

TOP_TEN = [(f'P{place}', 1000 - place * 100) for place in range(1, 11)]  # 900, 800, ... 0


@pytest.fixture
def highscores(tmp_path):
    table = HighScores(str(tmp_path))
    table.entries = list(TOP_TEN)
    return table


@pytest.fixture
def combo():
    return Combo()


@pytest.mark.parametrize(
    'new, expected',
    [
        (5000, ('1ST', 1)),
        (850, ('2ND', 2)),
        (750, ('3RD', 3)),
        (650, ('4TH', 4)),
        (50, ('10TH', 10)),
    ],
)
def test_place(highscores, new, expected):
    assert highscores.place(new) == expected


def test_place_ranks_a_tie_below_the_existing_score(highscores):
    assert highscores.place(900) == ('2ND', 2)


def test_place_below_the_top_ten_has_no_label(highscores):
    assert highscores.place(0) == ('', 11)


@pytest.mark.parametrize(
    'score, expected',
    [
        (0, (0, 1)),
        (500, (-50, 1)),
        (999, (-99, 1)),
        (12345, (-1224, 12)),
        (100000, (-10000, 100)),
    ],
)
def test_get_penalty(score, expected):
    assert scores.get_penalty(score) == expected


@pytest.mark.parametrize('score', [1500, 12345, 98765, 1234567])
def test_get_penalty_is_a_multiple_of_the_step(score):
    # the penalty is counted down in steps on the continue screen
    penalty, step = scores.get_penalty(score)
    assert penalty % step == 0
    assert -penalty <= score * 0.1


def test_get_bonus():
    assert scores.get_bonus('time_bonus') == 300
    assert scores.get_bonus('no_continue') == 20000
    assert scores.get_bonus('all_pus') == 100000
    assert scores.get_bonus('clear') == 20000
    assert scores.get_bonus('perfect') == 1000000
    assert scores.get_bonus('unknown') is None


@pytest.mark.parametrize(
    'reason, points',
    [('hit_brick', 10), ('killed_brick', 20), ('phagocyte', 15), ('powerup', 85)],
)
def test_points(combo, reason, points):
    assert combo.points(reason) == points


def test_points_use_the_multiplier(combo):
    for _ in range(3):
        combo.hit()
    assert combo.points('killed_brick') == 60
    assert combo.points('killed_brick', no_combo=True) == 20


def test_combo(combo):
    assert combo.value == 1
    assert not combo.is_combo()
    combo.hit()
    assert combo.value == 1
    assert not combo.is_combo()
    combo.hit()
    assert combo.value == 2
    assert combo.is_combo()


def test_multiplier_resets_after_a_second_without_hits(combo):
    combo.hit()
    combo.hit()
    combo.update(600)
    assert combo.value == 2
    combo.update(600)
    assert combo.value == 1


def test_a_hit_restarts_the_multiplier_timer(combo):
    combo.hit()
    combo.update(900)
    combo.hit()
    combo.update(900)
    assert combo.value == 2


def test_reset(combo):
    combo.hit()
    combo.hit()
    combo.reset()
    assert combo.value == 1


def test_new_combo_reports_each_change_once(combo):
    assert combo.new_combo() is None
    combo.hit()
    combo.hit()
    # returns the previous multiplier when it changed, then None until the next change
    assert combo.new_combo() == 0
    assert combo.new_combo() is None
    combo.hit()
    assert combo.new_combo() == 2
    assert combo.new_combo() is None


def test_add_keeps_the_best_ten(highscores):
    highscores.add('NEW', 850, free_mode=True)
    names = [entry[0] for entry in highscores.entries]
    assert len(names) == 10
    assert names[:3] == ['P1', 'NEW', 'P2']
    assert 'P10' not in names


def test_add_records_metadata(highscores):
    highscores.add('NEW', 5000, free_mode=False)
    name, score, date, free_mode = highscores.entries[0]
    assert (name, score) == ('NEW', 5000)
    assert date
    assert free_mode is False


def test_save_and_load(highscores):
    highscores.save()
    highscores.entries = []
    highscores.load()
    assert highscores.entries == TOP_TEN


def test_load_without_a_file_keeps_and_saves_the_list(highscores):
    highscores.entries = list(reversed(TOP_TEN)) + [('LOW', -1)]
    highscores.load()
    assert highscores.entries == TOP_TEN
    with open(highscores.path, 'rb') as f:
        assert pickle.load(f) == TOP_TEN


def test_new_list_starts_with_the_defaults(tmp_path):
    table = HighScores(str(tmp_path))
    table.load()
    assert table.entries == sorted(scores.DEFAULT_HIGHSCORES, key=lambda entry: entry[1], reverse=True)


def test_highest_and_lowest(highscores):
    highscores.save()
    assert highscores.highest() == 900
    assert highscores.lowest() == 0
