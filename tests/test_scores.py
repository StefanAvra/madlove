import pickle

import pytest

from madlove import config

TOP_TEN = [(f'P{place}', 1000 - place * 100) for place in range(1, 11)]  # 900, 800, ... 0


@pytest.fixture
def top_ten(scores, monkeypatch):
    monkeypatch.setattr(scores, 'highscores', list(TOP_TEN))
    return scores


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
def test_get_place(top_ten, new, expected):
    assert top_ten.get_place(new) == expected


def test_get_place_ranks_a_tie_below_the_existing_score(top_ten):
    assert top_ten.get_place(900) == ('2ND', 2)


def test_get_place_below_the_top_ten_has_no_label(top_ten):
    assert top_ten.get_place(0) == ('', 11)


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
def test_get_penalty(scores, score, expected):
    assert scores.get_penalty(score) == expected


@pytest.mark.parametrize('score', [1500, 12345, 98765, 1234567])
def test_get_penalty_is_a_multiple_of_the_step(scores, score):
    # the penalty is counted down in steps on the continue screen
    penalty, step = scores.get_penalty(score)
    assert penalty % step == 0
    assert -penalty <= score * 0.1


def test_get_bonus(scores):
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
def test_increase_score(scores, reason, points):
    assert scores.increase_score(reason) == points


def test_increase_score_uses_the_multiplier(scores):
    for _ in range(3):
        scores.increase_multiplier()
    assert scores.increase_score('killed_brick') == 60
    assert scores.increase_score('killed_brick', no_combo=True) == 20


def test_combo(scores):
    assert scores.get_combo() == 1
    assert not scores.is_combo()
    scores.increase_multiplier()
    assert scores.get_combo() == 1
    assert not scores.is_combo()
    scores.increase_multiplier()
    assert scores.get_combo() == 2
    assert scores.is_combo()


def test_multiplier_resets_after_a_second_without_hits(scores):
    scores.increase_multiplier()
    scores.increase_multiplier()
    scores.decrease_multiplier(600)
    assert scores.get_combo() == 2
    scores.decrease_multiplier(600)
    assert scores.get_combo() == 1


def test_a_hit_restarts_the_multiplier_timer(scores):
    scores.increase_multiplier()
    scores.decrease_multiplier(900)
    scores.increase_multiplier()
    scores.decrease_multiplier(900)
    assert scores.get_combo() == 2


def test_reset_multiplier(scores):
    scores.increase_multiplier()
    scores.increase_multiplier()
    scores.reset_multiplier()
    assert scores.get_combo() == 1


def test_get_new_combo_reports_each_change_once(scores):
    assert scores.get_new_combo() is None
    scores.increase_multiplier()
    scores.increase_multiplier()
    # returns the previous multiplier when it changed, then None until the next change
    assert scores.get_new_combo() == 0
    assert scores.get_new_combo() is None
    scores.increase_multiplier()
    assert scores.get_new_combo() == 2
    assert scores.get_new_combo() is None


def test_update_highscores_keeps_the_best_ten(top_ten):
    top_ten.update_highscores(('NEW', 850))
    names = [entry[0] for entry in top_ten.highscores]
    assert len(names) == 10
    assert names[:3] == ['P1', 'NEW', 'P2']
    assert 'P10' not in names


def test_update_highscores_records_metadata(top_ten, monkeypatch):
    monkeypatch.setattr(config, 'FREE_MODE', False)
    top_ten.update_highscores(('NEW', 5000))
    name, score, date, free_mode = top_ten.highscores[0]
    assert (name, score) == ('NEW', 5000)
    assert date
    assert free_mode is False


def test_save_and_load_highscores(top_ten, monkeypatch):
    top_ten.save_highscores()
    monkeypatch.setattr(top_ten, 'highscores', [])
    top_ten.load_highscores()
    assert top_ten.highscores == TOP_TEN


def test_load_highscores_without_a_file_keeps_and_saves_the_defaults(scores, monkeypatch):
    monkeypatch.setattr(scores, 'highscores', list(reversed(TOP_TEN)) + [('LOW', -1)])
    scores.load_highscores()
    assert scores.highscores == TOP_TEN
    with open(config.HIGHSCORE_FILE, 'rb') as f:
        assert pickle.load(f) == TOP_TEN


def test_highest_and_lowest_score(top_ten):
    top_ten.save_highscores()
    assert top_ten.highest_score() == 900
    assert top_ten.lowest_score() == 0
