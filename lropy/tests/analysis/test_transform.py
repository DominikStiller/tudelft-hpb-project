from math import sqrt
from unittest import TestCase

import numpy as np

from lropy.analysis.transform import cart2track


class TestTransform(TestCase):
    def test_cart2track_1(self):
        acc = np.array([1, 2, 3])
        vel = np.array([0, 3, 0])
        pos = np.array([5, 0, 0])

        radial, along, cross = cart2track(acc, vel, pos)

        self.assertAlmostEqual(radial, 1)
        self.assertAlmostEqual(along, 2)
        self.assertAlmostEqual(cross, 3)

    def test_cart2track_2(self):
        acc = np.array([0, 4, 4])
        vel = np.array([3, 3, 0])
        pos = np.array([0, 5, 5])

        radial, along, cross = cart2track(acc, vel, pos)

        self.assertAlmostEqual(radial, sqrt(2) * 4)
        self.assertAlmostEqual(along, 0)
        self.assertAlmostEqual(cross, 0)

    def test_cart2track_3(self):
        rng = np.random.default_rng()
        for _ in range(10):
            acc = rng.uniform(0, 5, (3))
            vel = rng.uniform(0, 5, (3))
            pos = rng.uniform(0, 5, (3))

            radial, along, cross = cart2track(acc, vel, pos)

            self.assertAlmostEqual(
                np.linalg.norm(acc),
                np.linalg.norm(np.array([radial, along, cross])),
            )
