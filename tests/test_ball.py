import random

from madlove.sprites.ball import Ball


def test_each_ball_draws_its_own_default_velocity():
    random.seed(2019)
    velocities = {Ball().velocity for _ in range(20)}
    assert len(velocities) > 1
    assert all(-3 <= x <= 3 and y == -3 for x, y in velocities)
