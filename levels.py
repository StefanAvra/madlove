TILE_MAP = (15, 32)
TILE = (32, 20)

_levels = {
    0: {
        'bricks':  ['               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '   bb     bb   ',
                    '  bbbb   bbbb  ',
                    ' bbbbbb bbbbbb ',
                    ' bbbbb   bbbbb ',
                    ' bbbbbb bbbbbb ',
                    '  b bb   bb b  ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               ',
                    '               '],
    },
    1: {}
}


class Level:
    def __init__(self, no):
        global _levels
        self.no = no
        self.bricks = _levels.get(no).get('bricks')

