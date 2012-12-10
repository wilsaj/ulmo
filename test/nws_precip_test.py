import datetime

import geopy.distance
import numpy as np

from ulmo.nws import precip


def test_hrap_to_lat_lon():
    hrap_latlon_pairs = [
        # (hrap_x, hrap_y), (lat, lon)
        ((14, 10), (23.476933, -118.67131)),
        ((14, 823), (51.615555, -131.4471)),
        ((14.5, 10.5), (23.496319, -118.658440)),
        ((14.5, 587.5), (43.028732, -125.874435)),
        ((14.5, 822.5), (51.606331, -131.402908)),
        ((15.5, 373.5), (35.466969, -122.435051)),
        ((20.5, 293.5), (32.775543, -121.225700)),
        ((115.5, 502.5), (41.100899, -119.568840)),
        ((225.5, 227.5), (31.967602, -112.281555)),
        ((256.5, 771.5), (52.722473, -114.881836)),
        ((501.5, 756.5), (52.373867, -98.213417)),
        ((554.5, 357.5), (36.694935, -97.962898)),
        ((555.5, 20.5), (25.075483, -99.416855)),
        ((616.5, 61.5), (26.177685, -97.031487)),
        ((652.5, 396.5), (37.521507, -93.206070)),
        ((673.5, 11.5), (24.273355, -95.271919)),
        ((763.5, 50.5), (24.935785, -91.840866)),
        ((772.5, 739.5), (48.805065, -81.673103)),
        ((792.5, 398.5), (36.267193, -86.966217)),
        ((821.5, 207.5), (29.508913, -88.208382)),
        ((1064.5, 10.5), (20.761557, -82.355843)),
        ((1064.5, 822.5), (45.436882, -64.559708)),
        ((1065, 10), (20.741228, -82.346901)),
        ((1065, 823), (45.439083, -64.520226)),
    ]

    hrap_xy_pairs = [
            np.array(hrap_xy) for hrap_xy, hrap_latlon in hrap_latlon_pairs]
    hrap_x, hrap_y = np.array(hrap_xy_pairs).T
    known_latlons = [
            np.array(hrap_latlon) for hrap_xy, hrap_latlon in hrap_latlon_pairs]
    converted_latlons = [
            i for i in np.array(precip.core._hrap_to_lat_lon(hrap_x, hrap_y)).T]

    for hrap_xy, known_latlon, converted_latlon in zip(hrap_xy_pairs,
            known_latlons, converted_latlons):
        geopy.distance.VincentyDistance.ELLIPSOID = 'WGS-84'
        distance = geopy.distance.VincentyDistance(known_latlon, converted_latlon)
        assert distance.meters < 1
