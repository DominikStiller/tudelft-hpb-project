from unittest import TestCase

from lropy.analysis.io import _get_column_name


class TestIO(TestCase):
    def test_get_column_name(self):
        expected = {
            "Relative position of LRO w.r.t. Moon": "pos",
            "Relative position of Vehicle w.r.t. Earth": "pos",
            "Relative velocity of LRO w.r.t. Moon": "vel",
            "Relative velocity of Vehicle w.r.t. Earth": "vel",
            "Kepler elements of LRO w.r.t. Moon": "kepler",
            "Altitude of LRO w.r.t. Moon": "h",
            "Relative position of Sun w.r.t. Moon": "pos_sun",
            "Relative position of Earth w.r.t. Moon": "pos_earth",
            "Spherical position angle latitude angle of LRO w.r.t. Moon": "lat_moon",
            "Spherical position angle longitude angle of LRO w.r.t. Moon": "lon_moon",
            "Single acceleration in inertial frame of type spherical harmonic gravity , acting on LRO, exerted by Moon": "acc_grav_moon",
            "Single acceleration in inertial frame of type spherical harmonic gravity , acting on LRO, exerted by Earth": "acc_grav_earth",
            "Single acceleration in inertial frame of type central gravity , acting on LRO, exerted by Sun": "acc_grav_sun",
            "Single acceleration in inertial frame of type radiation pressure acceleration, acting on LRO, exerted by Sun": "acc_rp_sun",
            "Single acceleration in inertial frame of type cannonball radiation pressure , acting on LRO, exerted by Sun": "acc_rp_sun",
            "Single acceleration in inertial frame of type panelled radiation pressure acceleration , acting on LRO, exerted by Sun": "acc_rp_sun",
            "Single acceleration in inertial frame of type radiation pressure acceleration, acting on Vehicle, exerted by Earth": "acc_rp_earth",
            "Received irradiance at LRO due to Sun": "irr_sun",
            "Received fraction of irradiance at LRO due to Sun": "occ_sun",
            "Single acceleration in inertial frame of type radiation pressure acceleration, acting on LRO, exerted by Moon": "acc_rp_moon",
            "Received irradiance at LRO due to Moon": "irr_moon",
            "Number of visible source panels of Moon as seen from LRO": "panels_vis_moon",
            "Number of illuminated source panels of Moon as seen from LRO": "panels_ill_moon",
            "Number of visible and illuminated source panels of Moon as seen from LRO": "panels_vis_ill_moon",
            "Visible area of Earth as seen from Vehicle": "area_vis_earth",
            "Visible area of Moon as seen from LRO": "area_vis_moon",
        }
        for id, name in expected.items():
            self.assertEqual(name, _get_column_name(id))
