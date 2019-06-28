import sound


__credit = 0
__life_to_credit_ratio = 3
__lives = 0


def consume_coin():
    """resets credit and returns amount of lives to add in-game"""
    global __credit
    global __lives
    if __credit > 0:
        __lives = __life_to_credit_ratio
        __credit -= 1


def get_credit():
    """returns credit amount without resetting"""
    return __credit


def add_coin():
    global __credit
    __credit += 1
    sound.sfx_lib.get('coin').play()


def get_lives():
    return __lives


def add_life(add=1):
    global __lives
    __lives += add


def lose_life():
    global __lives
    __lives -= 1
    if __lives < 0:
        __lives = 0


