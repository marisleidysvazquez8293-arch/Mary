"""Unit tests for CLPService — reclassification and S formula."""
from __future__ import annotations

import unittest

import numpy as np

from apps.multicriterio.services import (
    CLASS_LABELS,
    CLPService,
    SuitabilityClass,
)


class CLPServiceTests(unittest.TestCase):
    def setUp(self):
        self.clp = CLPService(
            cell_area_m2=100.0,
            waste_generation_ton_per_year=10_000.0,
        )

    def test_suitability_formula(self):
        # 2 criteria, equal weights; exclusion zeros one cell
        x1 = np.array([[1.0, 0.5], [0.8, 0.2]])
        x2 = np.array([[1.0, 0.5], [0.8, 0.2]])
        weights = [0.5, 0.5]
        excl = np.array([[1.0, 1.0], [0.0, 1.0]])
        result = self.clp.compute([x1, x2], weights, excl)
        # weighted sum == x1 (identical)
        np.testing.assert_allclose(result.weighted_sum, x1)
        np.testing.assert_allclose(result.suitability, x1 * excl)
        self.assertEqual(
            result.class_map[1, 0], int(SuitabilityClass.EXCLUIDO)
        )

    def test_reclassify_six_classes(self):
        # values chosen for DEFAULT_BREAKS (0.2, 0.4, 0.6, 0.8)
        s = np.array(
            [
                [0.0, 0.10, 0.30],
                [0.50, 0.70, 0.90],
            ]
        )
        classes = self.clp.reclassify(s)
        self.assertEqual(classes[0, 0], SuitabilityClass.EXCLUIDO)
        self.assertEqual(classes[0, 1], SuitabilityClass.NO_APTO)  # 0.10 <= 0.20
        self.assertEqual(classes[0, 2], SuitabilityClass.NO_RECOMENDABLE)  # 0.30 <= 0.40
        self.assertEqual(classes[1, 0], SuitabilityClass.APTO_CON_RESTRICCIONES)  # 0.50
        self.assertEqual(classes[1, 1], SuitabilityClass.FAVORABLE)  # 0.70
        self.assertEqual(classes[1, 2], SuitabilityClass.OPTIMO)  # 0.90

    def test_class_counts_labels(self):
        s = np.array([[0.0, 0.9], [0.9, 0.0]])
        cm = self.clp.reclassify(s)
        counts = self.clp.class_counts(cm)
        self.assertEqual(set(counts), set(CLASS_LABELS.values()))
        self.assertEqual(counts["Excluido"], 2)
        self.assertEqual(counts["Óptimo"], 2)

    def test_weights_normalized(self):
        x = np.ones((2, 2))
        # weights 2 and 2 → same as 0.5/0.5
        out = self.clp.weighted_sum([x, x], [2.0, 2.0])
        np.testing.assert_allclose(out, np.ones((2, 2)))

    def test_delineate_candidates_intermunicipal(self):
        class_map = np.array(
            [
                [5, 5, 0],
                [5, 5, 0],
                [0, 0, 4],
            ],
            dtype=np.int8,
        )
        suitability = np.array(
            [
                [0.9, 0.85, 0.0],
                [0.88, 0.92, 0.0],
                [0.0, 0.0, 0.75],
            ]
        )
        munis = np.array(
            [
                ["A", "A", "A"],
                ["B", "B", "B"],
                ["B", "B", "B"],
            ]
        )
        cands = self.clp.delineate_candidates(
            class_map, suitability, municipality_labels=munis
        )
        self.assertEqual(len(cands), 2)
        big = next(c for c in cands if c.attributes["n_cells"] == 4)
        self.assertTrue(big.intermunicipal)
        self.assertEqual(set(big.municipalities), {"A", "B"})
        self.assertAlmostEqual(big.area_m2, 400.0)
        self.assertIsNotNone(big.useful_life_years)

    def test_favorable_band(self):
        s = np.array([[0.75]])
        self.assertEqual(
            self.clp.reclassify(s)[0, 0], SuitabilityClass.FAVORABLE
        )


if __name__ == "__main__":
    unittest.main()
