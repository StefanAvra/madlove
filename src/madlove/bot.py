import math
import random

from madlove import config, utils

INACCURACY = 0.4  # how far off the ball the bot aims, as a share of the paddle width


def _gradient(i):
    # fixed pseudo-random slope in [-1, 1] for each lattice point
    return random.Random(i).uniform(-1, 1)


def _noise1(x):
    """smooth 1D gradient noise (like Perlin noise), replaces noise.pnoise1"""
    i = math.floor(x)
    t = x - i
    fade = t * t * t * (t * (t * 6 - 15) + 10)
    return (1 - fade) * _gradient(i) * t + fade * _gradient(i + 1) * (t - 1)


class Bot:
    """moves the paddle towards the first ball, slightly off target, and launches sticky balls at random"""

    def __init__(self):
        self.step = 0.0

    def play(self, player, balls):
        """returns whether to move left and right"""
        self.step += 0.001
        self.step %= 1
        left = False
        right = False
        ball_to_follow = balls.sprites()[0]
        trigger_range_offset = utils.interp(ball_to_follow.rect.y, [0, config.PLAYER_Y - 10], [400, 0])
        trigger_range = (player.rect.centerx - trigger_range_offset / 2, player.rect.centerx + trigger_range_offset / 2)

        for ball in balls:
            if ball.sticky and random.randint(0, 50) == 11:
                ball.sticky = False

        if not trigger_range[0] < ball_to_follow.rect.centerx < trigger_range[1]:
            offset = utils.interp(
                _noise1(self.step), [0, 1], [-player.rect.width * INACCURACY, player.rect.width * INACCURACY]
            )
            # print(offset)
            if player.rect.centerx > ball_to_follow.rect.centerx + offset:
                left = True
            else:
                right = True

        return left, right
