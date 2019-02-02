import random

inaccuracy = 5
update_interval = 1
__left = False
__right = False
_step = 0

# todo: to smooth bot movement. perlin noise?


def play(player, balls):
    global __left
    global __right
    global _step

    _step += 1
    if (_step % update_interval) == 0:
        __left = False
        __right = False
        _step = 0
        offset = random.randint(-inaccuracy, inaccuracy)
        if player.rect.centerx > balls.sprites()[0].rect.centerx + offset:
            __left = True
        else:
            __right = True

    return __left, __right
