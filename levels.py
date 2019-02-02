TILE_MAP = (15, 32)
TILE = (32, 20)

_levels = {
    1: {
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
    0: {
        'bricks': ['               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '           b   ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               ',
                   '               '],
    }
}


class Level:
    def __init__(self, no):
        global _levels
        self.no = no
        self.bricks = _levels.get(no).get('bricks')

