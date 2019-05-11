
__credit = 0
__life_to_credit_ratio = 3


def coins_to_lives():
    """resets credit and returns amount of lives to add in-game"""
    global __credit
    add_lives = __credit * __life_to_credit_ratio
    __credit = 0
    return add_lives


def get_credit():
    """returns credit amount without resetting"""
    return __credit


def add_coin():
    global __credit
    __credit += 1


