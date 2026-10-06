import pytest

from madlove.coins import Wallet


@pytest.fixture
def wallet():
    return Wallet()


def test_add_coin(wallet):
    wallet.add_coin()
    wallet.add_coin()
    assert wallet.credit == 2


def test_consume_coin_turns_a_credit_into_three_lives(wallet):
    wallet.add_coin()
    wallet.consume_coin()
    assert wallet.credit == 0
    assert wallet.lives == 3


def test_consume_coin_refills_lives_instead_of_adding(wallet):
    wallet.add_coin()
    wallet.add_life(2)
    wallet.consume_coin()
    assert wallet.lives == 3


def test_consume_coin_without_credit_does_nothing(wallet):
    wallet.consume_coin()
    assert wallet.credit == 0
    assert wallet.lives == 0


def test_add_and_lose_lives(wallet):
    wallet.add_life()
    wallet.add_life(2)
    assert wallet.lives == 3
    wallet.lose_life()
    assert wallet.lives == 2


def test_lives_do_not_go_below_zero(wallet):
    wallet.lose_life()
    assert wallet.lives == 0


def test_free_credit_tops_up_to_one(wallet):
    wallet.give_free_credit()
    assert wallet.credit == 1
    wallet.give_free_credit()
    assert wallet.credit == 1


def test_free_credit_keeps_inserted_coins(wallet):
    wallet.add_coin()
    wallet.add_coin()
    wallet.give_free_credit()
    assert wallet.credit == 2
