import sound

__credit = 0
__life_to_credit_ratio = 3


def consume_coin():
    """resets credit and returns amount of lives to add in-game"""
    global __credit
    add_lives = 0
    if __credit > 0:
        add_lives = __life_to_credit_ratio
        __credit -= 1
    return add_lives


def get_credit():
    """returns credit amount without resetting"""
    return __credit


def add_coin():
    global __credit
    __credit += 1
    sound.sfx_lib.get('coin').play()


