TILE_MAP = (17, 62)
TILE = (25, 7)
TILE_PADDING = 3

_levels = {
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
                   '     r     r     ',
                   '     rr   rr     ',
                   '    rrr   rrr    ',
                   '    rrr   rrr    ',
                   '    rrr   rrr    ',
                   '    rrrr rrrr    ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrr   rrrrr  ',
                   '  rrrrr   rrrrr  ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrrr rrrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   '  rr         rr  ',
                   '  r           r  ',
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
                   '                 '],
        'name': 'The Lungs',
        'powerups': {
            'pack': 1,
            'shoot': 1,
            'metastasis': 3,
            'longer': 2,
            'shorter': 1
        },
        'bonus_time': 120
    },
    1: {
        'bricks': ['                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '      w   w     ',
                   '     www www    ',
                   '    wwwwwwwww   ',
                   '    wwwwwwwww   ',
                   '    wwwwwwwww   ',
                   '    wwwwwwwww   ',
                   '     wwwwwww    ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '      wwwww     ',
                   '     wwwwwww    ',
                   '    wwwwwwwww   ',
                   '    wwwwwwwww   ',
                   '    wwwwwwwww   ',
                   '    wwwwwwwww   ',
                   '     www www    ',
                   '      w   w     ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                ',
                   '                '],
        'name': 'The Bone'
    },
    2: {
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
                   '                 ',
                   '                 ',
                   '                 ',
                   '                 ',
                   '      r   r      ',
                   '   rr rr rr rr   ',
                   '  rrrrrr rrrrrr  ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rr  rrrrrrr  rr ',
                   ' r   rrrrrrr   r ',
                   ' r   rrrrrrr   r ',
                   ' rr  rrrrrrr  rr ',
                   ' rr  rrrrrrr  rr ',
                   '  rr rrrrrrr rr  ',
                   '  rr rrrrrrr rr  ',
                   '   r  rrrrr  r   ',
                   '      rrrrr      ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '       rrr       ',
                   '        r        ',
                   '        r        ',
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
                   '                 '],
        'name': 'The Ovary'
    },
    3: {
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
                   '      rrrrrrr    ',
                   '     rrrrrrrrr   ',
                   '    rrrrrrrrrrr  ',
                   '    rrrrrrrrrrr  ',
                   '    rrr     rrr  ',
                   '   rrr       rrr ',
                   '   rrr       rrr ',
                   '   rr         rr ',
                   '   rr         rr ',
                   '   rr         rr ',
                   '   rr         rr ',
                   '   rr         rr ',
                   '   rrr       rrr ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '    rr       rr  ',
                   '   rrr       rrr ',
                   '   rr         rr ',
                   '   rr         rr ',
                   '   rr         rr ',
                   '   rr         rr ',
                   '   rr         rr ',
                   '   rr        rrr ',
                   '    rr      rrr  ',
                   '    rr   rrrrrr  ',
                   '    rr   rrrrrr  ',
                   '     r   rrrrr   ',
                   '         rrrr    ',
                   '         rr      ',
                   '         rr      ',
                   '         r       ',
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
        'name': 'The Large Bowel'
    },
    4: {
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
                   '                 ',
                   '    rrr   rrr    ',
                   '   rrrr   rrrr   ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrr   rrrrr  ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   ' rrrrrr   rrrrrr ',
                   '  rrrrr   rrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '   rrrrr rrrrr   ',
                   '   rrrr   rrrr   ',
                   '    rrr   rrr    ',
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
                   '                 ',
                   '                 '],
        'name': 'The Kidneys'
    },
    5: {
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
                   '                 ',
                   '                 ',
                   '                 ',
                   '     r     r     ',
                   '   rrrr   rrrr   ',
                   '   rrrr   rrrr   ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrr rrrrrr  ',
                   '  rrrrrrrrrrrrr  ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   ' rrrrrrrrrrrrrrr ',
                   '  rrrrrrrrrrrrr  ',
                   '  rrrrrrrrrrrrr  ',
                   '  rrrrrrrrrrrrr  ',
                   '   rrrrrrrrrrr   ',
                   '   rrrrrrrrrrr   ',
                   '    rrrrrrrrr    ',
                   '    rrrrrrrrr    ',
                   '     rrrrrrr     ',
                   '     rrrrrrr     ',
                   '      rrrrr      ',
                   '      rrrrr      ',
                   '       rrr       ',
                   '       rrr       ',
                   '        r        ',
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
        'name': 'The Heart'
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
