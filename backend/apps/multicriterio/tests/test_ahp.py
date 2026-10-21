"""Unit tests for AHPService — pure numpy, no PostGIS."""
from __future__ import annotations

import unittest

import numpy as np

from apps.multicriterio.services import AHPService, SAATY_RI


class AHPServiceTests(unittest.TestCase):
    def setUp(self):
        self.ahp = AHPService(cr_threshold=0.10)

    def test_consistent_3x3_matrix(self):
        # Classic consistent (approx) matrix
        a = np.array(
            [
                [1, 3, 5],
                [1 / 3, 1, 2],
                [1 / 5, 1 / 2, 1],
            ],
            dtype=float,
        )
        result = self.ahp.consistency_ratio(a)
        self.assertEqual(result.n, 3)
        self.assertAlmostEqual(result.weights.sum(), 1.0, places=6)
        self.assertTrue(result.weights[0] > result.weights[1] > result.weights[2])
        self.assertLess(result.consistency_ratio, 0.10)
        self.assertTrue(result.is_consistent)
        self.assertEqual(result.random_index, SAATY_RI[3])

    def test_equal_judgments_perfectly_consistent(self):
        # All criteria equally preferred → ones matrix, CR=0, equal weights
        a = np.ones((4, 4), dtype=float)
        result = self.ahp.consistency_ratio(a)
        self.assertAlmostEqual(result.consistency_ratio, 0.0, places=8)
        np.testing.assert_allclose(result.weights, np.full(4, 0.25), atol=1e-8)

    def test_validate_cr_raises_on_inconsistent(self):
        # Deliberately inconsistent
        a = np.array(
            [
                [1, 9, 1 / 9],
                [1 / 9, 1, 9],
                [9, 1 / 9, 1],
            ],
            dtype=float,
        )
        with self.assertRaises(ValueError) as ctx:
            self.ahp.validate_cr(a, threshold=0.10)
        self.assertIn("CR=", str(ctx.exception))

    def test_aggregate_aij_geometric_mean(self):
        m1 = np.array([[1, 2, 4], [0.5, 1, 2], [0.25, 0.5, 1]], dtype=float)
        m2 = np.array([[1, 4, 6], [0.25, 1, 2], [1 / 6, 0.5, 1]], dtype=float)
        agg = self.ahp.aggregate_aij([m1, m2])
        # Element (0,1) = sqrt(2*4) = sqrt(8)
        self.assertAlmostEqual(agg[0, 1], np.sqrt(8), places=6)
        self.assertAlmostEqual(agg[0, 1] * agg[1, 0], 1.0, places=6)
        result = self.ahp.consistency_ratio(agg)
        self.assertAlmostEqual(result.weights.sum(), 1.0, places=6)

    def test_non_reciprocal_rejected(self):
        bad = np.array([[1, 2], [2, 1]], dtype=float)  # should be 0.5
        with self.assertRaises(ValueError):
            self.ahp.principal_eigenvector(bad)

    def test_ic_formula(self):
        # IC = (λmax - n) / (n - 1)
        self.assertAlmostEqual(self.ahp.consistency_index(3.0, 3), 0.0)
        self.assertAlmostEqual(self.ahp.consistency_index(3.096, 3), 0.048, places=3)


if __name__ == "__main__":
    unittest.main()
