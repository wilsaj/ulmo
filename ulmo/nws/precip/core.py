import math

import numpy as np


def _hrap_to_lat_lon(hrap_x, hrap_y):
    """adapted from nctoasc.c by Ken Pavelle"""
    raddeg = 57.29577951
    earth_radius = 6371.2
    stdlon = 105.0
    mesh_len = 4.7625
    tlat = 60.0 / raddeg

    x = hrap_x - 401.0
    y = hrap_y - 1601.0

    rr = x**2 + y**2
    gi = ((earth_radius * (1 + math.sin(tlat))) / mesh_len)
    gi = gi**2
    lat = np.arcsin((gi-rr)/(gi+rr)) * raddeg
    ang = np.arctan2(y, x) * raddeg
    #ang = np.arctan2(x, y) * raddeg
    if ang.shape:
        ang[ang < 0] += 360.0
    elif ang < 0:
        ang += 360.0

    lon = 270 + stdlon - ang
    if lon.shape:
        lon[lon < 0] += 360
        lon[lon > 360] -= 360

    return lat, -1 * lon


