TILE_MAP = (17, 62)
TILE = (25, 7)
TILE_PADDING = 3

_levels = {
    2: {
        'bricks':  ['               ',
                    '               ',
                    ' bb   bbb   bb ',
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
                    '       b       ',
                    '     b         ',
                    '               ',
                    '          b    ',
                    ' bb  bb b   bb '],
    },
    0: {
        'bricks': ['                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '     b     b     ',
                   '     bb   bb     ',
                   '    bbb   bbb    ',
                   '    bbb   bbb    ',
                   '    bbb   bbb    ',
                   '    bbbb bbbb    ',
                   '   bbbbb bbbbb   ',
                   '   bbbbb bbbbb   ',
                   '   bbbbb bbbbb   ',
                   '   bbbbb bbbbb   ',
                   '   bbbbb bbbbb   ',
                   '   bbbbb bbbbb   ',
                   '  bbbbbb bbbbbb  ',
                   '  bbbbbb bbbbbb  ',
                   '  bbbbbb bbbbbb  ',
                   '  bbbbbb bbbbbb  ',
                   '  bbbbbb bbbbbb  ',
                   '  bbbbb   bbbbb  ',
                   '  bbbbb   bbbbb  ',
                   ' bbbbbb   bbbbbb ',
                   ' bbbbbb   bbbbbb ',
                   ' bbbbbb   bbbbbb ',
                   ' bbbbbb   bbbbbb ',
                   ' bbbbbb   bbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbbb bbbbbbb ',
                   ' bbbbbb   bbbbbb ',
                   '  bb         bb  ',
                   '  b           b  ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 '],
    },
    1: {
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
                   '               ',
                   '               ',
                   '          b    ',
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
        try:
            self.bricks = _levels.get(no).get('bricks')
        except AttributeError:
            print('Level {} not found.'.format(no))
