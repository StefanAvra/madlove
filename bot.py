import noise
import numpy
import random

inaccuracy = 0.4
_step = 0.0


def play(player, balls):
    global _step

    _step += 0.001
    _step %= 1
    left = False
    right = False
    ball_to_follow = balls.sprites()[0]
    trigger_range_offset = numpy.interp(ball_to_follow.rect.y, [0, 620], [400, 0])
    trigger_range = (player.rect.centerx - trigger_range_offset/2, player.rect.centerx + trigger_range_offset/2)

    for ball in balls:
        if ball.sticky and random.randint(0, 50) == 11:
            ball.sticky = False

    if not trigger_range[0] < ball_to_follow.rect.centerx < trigger_range[1]:
        offset = numpy.interp(noise.pnoise1(_step), [0, 1],
                              [-player.rect.width * inaccuracy, player.rect.width * inaccuracy])
        print(offset)
        if player.rect.centerx > ball_to_follow.rect.centerx + offset:
            left = True
        else:
            right = True

    return left, right
