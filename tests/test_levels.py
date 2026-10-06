import os

import pytest

from madlove import config, levels

LEVEL_NOS = sorted(levels._levels)
BRICK_TYPES = 'bwr'


def count_bricks(rows):
    return sum(tile in BRICK_TYPES for row in rows for tile in row)


def test_total_levels():
    assert levels.get_total_levels() == len(LEVEL_NOS)
    assert LEVEL_NOS == list(range(len(LEVEL_NOS)))


@pytest.mark.parametrize('no', LEVEL_NOS)
def test_level_data(no):
    level = levels.Level(no)
    assert level.no == no
    assert level.bricks
    assert level.powerups
    assert level.bonus_time > 0


@pytest.mark.parametrize('no', LEVEL_NOS)
def test_tile_map_fits(no):
    rows = levels.Level(no).bricks
    width, height = levels.TILE_MAP
    assert len(rows) <= height
    assert len({len(row) for row in rows}) == 1, 'rows have different widths'
    assert len(rows[0]) <= width
    assert set(''.join(rows)) <= set(' ' + BRICK_TYPES)
    assert count_bricks(rows) > 0


@pytest.mark.parametrize('no', LEVEL_NOS)
def test_powerups_drop(no):
    # a power-up drops when the number of destroyed bricks reaches its key
    level = levels.Level(no)
    for destroyed, pu in level.powerups.items():
        assert 1 <= destroyed <= count_bricks(level.bricks)
        image = 'pack' if pu['pu_type'] == 'pack' else f'pu_{pu["pu_type"]}'
        assert os.path.isfile(config.asset('graphics', f'{image}.png'))


@pytest.mark.parametrize('no', LEVEL_NOS)
def test_game_scene_builds_every_brick(game, no):
    from madlove import killyourlungs

    scene = killyourlungs.GameScene(game, no)
    assert scene.total_bricks == count_bricks(levels.Level(no).bricks)
    assert all(0 <= brick.rect.left and brick.rect.right <= config.WIDTH for brick in scene.bricks)
