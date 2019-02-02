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
                   '     bbbbbb    ',
                   ' bbbbbbbbbb    ',
                   '     bbbbbb    ',
                   ' bbbbbbbbbbbb  ',
                   '    bbbbb   bb ',
                   '  bbbbbbbbbb   ',
                   '  b       b    ',
                   ' bbbbbbbbbbbbb ',
                   'bbbbbbbbbbbbbbb',
                   '     b b       ',
                   '  bbbbbbbbbbbb ',
                   '   bbb   bbbb  ',
                   '   bbbbb       ',
                   '    bb         ',
                   '   bbbb    b   ',
                   'bbbb  bb       ',
                   '  b      bbbb  ',
                   '     bbbb      ',
                   '   bb      bbb ',
                   '    bbbb       ',
                   ' bbbb   bbb    ',
                   ' bbbb     bb   ',
                   '      b        '],
    }
}


class Level:
    def __init__(self, no):
        global _levels
        self.no = no
        self.bricks = _levels.get(no).get('bricks')

