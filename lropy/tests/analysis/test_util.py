from unittest import TestCase

import pandas as pd

from lropy.analysis.util import get_closest_before, get_closest_after


class TestUtil(TestCase):
    def test_get_closest_before(self):
        df = pd.DataFrame([[1], [2], [3], [4]], index=[0, 1.3, 4.5, 5.6])

        # Single rows
        self.assertEqual(get_closest_before(df, -3)[0], 1)
        self.assertEqual(get_closest_before(df, 0)[0], 1)
        self.assertEqual(get_closest_before(df, 0.5)[0], 1)
        self.assertEqual(get_closest_before(df, 1.3)[0], 2)
        self.assertEqual(get_closest_before(df, 4.51)[0], 3)
        self.assertEqual(get_closest_before(df, 100)[0], 4)

        # Multiple rows
        self.assertListEqual(list(get_closest_before(df, [0.5, 0.5, 0.5])[0]), [1, 1, 1])
        self.assertListEqual(list(get_closest_before(df, [0.5, 1.3, 4.51])[0]), [1, 2, 3])
        self.assertListEqual(list(get_closest_before(df, [-3, 100])[0]), [1, 4])

    def test_get_closest_after(self):
        df = pd.DataFrame([[1], [2], [3], [4]], index=[0, 1.3, 4.5, 5.6])

        # Single rows
        self.assertEqual(get_closest_after(df, -3)[0], 1)
        self.assertEqual(get_closest_after(df, 0)[0], 1)
        self.assertEqual(get_closest_after(df, 0.5)[0], 2)
        self.assertEqual(get_closest_after(df, 1.3)[0], 2)
        self.assertEqual(get_closest_after(df, 4.51)[0], 4)
        self.assertEqual(get_closest_after(df, 100)[0], 4)

        # Multiple rows
        self.assertListEqual(list(get_closest_after(df, [0.5, 0.5, 0.5])[0]), [2, 2, 2])
        self.assertListEqual(list(get_closest_after(df, [0.5, 1.3, 4.51])[0]), [2, 2, 4])
        self.assertListEqual(list(get_closest_after(df, [-3, 100])[0]), [1, 4])
