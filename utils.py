def interp(x, xp, fp):
    """linear interpolation between the points xp and fp, clamped to fp like numpy.interp"""
    (x0, x1), (y0, y1) = xp, fp
    if x <= x0:
        return y0
    if x >= x1:
        return y1
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


def invert_color(color):
    """returns the inverted RGB color, used for blinking text"""
    return tuple(255 - c for c in color)
