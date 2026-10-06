import config


def test_add_coin(coins):
    coins.add_coin()
    coins.add_coin()
    assert coins.get_credit() == 2


def test_consume_coin_turns_a_credit_into_three_lives(coins):
    coins.add_coin()
    coins.consume_coin()
    assert coins.get_credit() == 0
    assert coins.get_lives() == 3


def test_consume_coin_refills_lives_instead_of_adding(coins):
    coins.add_coin()
    coins.add_life(2)
    coins.consume_coin()
    assert coins.get_lives() == 3


def test_consume_coin_without_credit_does_nothing(coins):
    coins.consume_coin()
    assert coins.get_credit() == 0
    assert coins.get_lives() == 0


def test_add_and_lose_lives(coins):
    coins.add_life()
    coins.add_life(2)
    assert coins.get_lives() == 3
    coins.lose_life()
    assert coins.get_lives() == 2


def test_lives_do_not_go_below_zero(coins):
    coins.lose_life()
    assert coins.get_lives() == 0


def test_free_mode_always_has_a_credit(coins, monkeypatch):
    monkeypatch.setattr(config, 'FREE_MODE', True)
    coins.handle_free_mode()
    assert coins.get_credit() == 1
    coins.handle_free_mode()
    assert coins.get_credit() == 1


def test_coin_op_mode_gives_no_free_credit(coins, monkeypatch):
    monkeypatch.setattr(config, 'FREE_MODE', False)
    coins.handle_free_mode()
    assert coins.get_credit() == 0
