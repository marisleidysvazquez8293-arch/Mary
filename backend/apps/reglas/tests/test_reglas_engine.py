"""Unit tests for ReglasEngineService — numpy masks, no PostGIS."""
from __future__ import annotations

import unittest

import numpy as np

from apps.reglas.services import (
    DEFAULT_AERODROME_WARNING_M,
    ReglasEngineService,
    RestrictionLayer,
)


class ReglasEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ReglasEngineService()

    def test_conjunction_product(self):
        a = np.array([[1, 1], [0, 1]], dtype=float)
        b = np.array([[1, 0], [1, 1]], dtype=float)
        layers = [
            RestrictionLayer("ECO_01", "normativa", a, {"buffer_m": 500}),
            RestrictionLayer("ECO_02", "normativa", b, {"buffer_m": 500}),
        ]
        result = self.engine.build_exclusion_mask(layers)
        expected = np.array([[1, 0], [0, 1]], dtype=float)
        np.testing.assert_array_equal(result.product, expected)
        np.testing.assert_array_equal(result.exclusion_mask, expected.astype(bool))
        self.assertEqual(result.buffers_applied_m["ECO_01"], 500)
        self.assertEqual(result.buffers_applied_m["ECO_02"], 500)

    def test_water_wells_500m_buffer(self):
        # distance raster: cell centers at 0, 400, 600 m from feature
        dist = np.array([[0.0, 400.0, 600.0]])
        mask = self.engine.apply_distance_buffer_mask(dist, 500.0)
        np.testing.assert_array_equal(mask, np.array([[False, False, True]]))

    def test_aerodrome_warning_not_hard_exclusion(self):
        # Inside 13 km → warning; outside → ok. Soft advertencia.
        dist = np.array([[5_000.0, 14_000.0]])  # m
        layers = self.engine.build_layers_from_distance_rasters(
            [
                {
                    "id_criterio": "SOC_01",
                    "tipo_restriccion": "advertencia",
                    "distance_m": dist,
                    "parametros": {"warning_radius_m": 13_000},
                },
                {
                    "id_criterio": "ECO_01",
                    "tipo_restriccion": "normativa",
                    "distance_m": np.array([[600.0, 600.0]]),
                    "parametros": {"buffer_m": 500},
                },
            ]
        )
        result = self.engine.build_exclusion_mask(layers)
        # Soft warning does not zero the product
        np.testing.assert_array_equal(result.product, np.array([[1.0, 1.0]]))
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.warnings[0].id_criterio, "SOC_01")
        self.assertEqual(result.warnings[0].radius_m, DEFAULT_AERODROME_WARNING_M)
        np.testing.assert_array_equal(
            result.warnings[0].cell_mask, np.array([[True, False]])
        )

    def test_advertencia_hard_exclude_when_configured(self):
        dist = np.array([[5_000.0, 14_000.0]])
        layers = self.engine.build_layers_from_distance_rasters(
            [
                {
                    "id_criterio": "SOC_01",
                    "tipo_restriccion": "advertencia",
                    "distance_m": dist,
                    "parametros": {
                        "warning_radius_m": 13_000,
                        "hard_exclude": True,
                    },
                }
            ]
        )
        result = self.engine.build_exclusion_mask(layers)
        np.testing.assert_array_equal(result.product, np.array([[0.0, 1.0]]))
        self.assertEqual(result.warnings, [])

    def test_gis_stubs_raise(self):
        with self.assertRaises(NotImplementedError):
            self.engine.buffer_geometries_stub([], 500)
        with self.assertRaises(NotImplementedError):
            self.engine.gee_exclusion_hook_stub(["asset/1"], None)


if __name__ == "__main__":
    unittest.main()
