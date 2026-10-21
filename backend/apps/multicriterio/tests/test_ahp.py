"""
Pruebas AHPService — Apéndice B (tesis SADE).

Las matrices crudas de 15 expertos no están en el extracto DOCX.
Se usan:
  1) Matrices derivadas a_ij = w_i/w_j de pesos publicados (CR≈0, recuperan w).
  2) Caso sintético con CR ≥ 0.10 y advertencia explícita.
  3) Semilla load_initial_rules: suma de 21 pesos globales == 1 ± 0.0001.
"""
from __future__ import annotations

import unittest

import numpy as np
from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.multicriterio.models import ConjuntoPesosAHP, PesoCriterio
from apps.multicriterio.services import AHPService, SAATY_RI
from apps.multicriterio.services.ahp_service import AHPService as AHPServiceDirect
from apps.multicriterio.tests.fixtures.apendice_b_pesos import (
    BLOQUE_WEIGHTS,
    CR_AGREGADA,
    IDS_21,
    PESOS_GLOBALES_21,
    PESOS_LOCALES_ECO,
    PESOS_LOCALES_GEO,
    PESOS_LOCALES_SOC,
)
from apps.reglas.data.initial_rules import DEFAULT_AHP_NOMBRE


class AHPServiceUnitTests(unittest.TestCase):
    def setUp(self):
        self.ahp = AHPService(cr_threshold=0.10)

    def test_import_compatible(self):
        self.assertIs(AHPService, AHPServiceDirect)

    def test_reconstruct_reciprocal_directional(self):
        # v(i sobre j) direccional (no recíproca)
        directional = np.array(
            [
                [1.0, 3.0, 5.0],
                [1.0, 1.0, 2.0],  # espejo de (0,1) sería 1/3; aquí 1 → a01=3
                [1.0, 1.0, 1.0],
            ],
            dtype=float,
        )
        # Forzamos espejos explícitos: v10=1, v01=3 → a01=3; v20=1,v02=5 → a02=5; v21=1,v12=2 → a12=2
        directional = np.array(
            [
                [1.0, 3.0, 5.0],
                [1.0, 1.0, 2.0],
                [1.0, 1.0, 1.0],
            ]
        )
        # a_ij = v_ij/v_ji → a01=3/1=3, a02=5/1=5, a12=2/1=2
        rec = self.ahp.reconstruct_reciprocal(directional)
        self.assertAlmostEqual(rec[0, 1], 3.0)
        self.assertAlmostEqual(rec[1, 0], 1.0 / 3.0)
        self.assertAlmostEqual(rec[0, 2], 5.0)
        self.assertAlmostEqual(rec[2, 0], 0.2)
        self.ahp.validate_reciprocal(rec)

    def test_apendice_b_block_weights_via_consistent_matrix(self):
        """Pesos de bloque B.3 recuperados desde matriz a_ij=w_i/w_j."""
        w = [
            BLOQUE_WEIGHTS["geohidrologico"],
            BLOQUE_WEIGHTS["ecologico"],
            BLOQUE_WEIGHTS["socioeconomico"],
        ]
        m = self.ahp.matrix_from_weights(w)
        result = self.ahp.consistency_ratio(m)
        np.testing.assert_allclose(result.weights, w, atol=1e-8)
        self.assertLess(result.consistency_ratio, 1e-8)
        self.assertTrue(result.is_consistent)
        # CR agregada tesis ≈ 0.002 (nuestra fixture es CR≈0 por construcción)
        self.assertLess(result.consistency_ratio, CR_AGREGADA["criterios"] + 0.01)

    def test_apendice_b_eco_local_weights(self):
        m = self.ahp.matrix_from_weights(PESOS_LOCALES_ECO)
        result = self.ahp.consistency_ratio(m)
        np.testing.assert_allclose(result.weights, PESOS_LOCALES_ECO, atol=1e-6)
        self.assertAlmostEqual(result.weights.sum(), 1.0, places=8)
        globals_ = self.ahp.global_weights(result.weights, BLOQUE_WEIGHTS["ecologico"])
        expected = [p * BLOQUE_WEIGHTS["ecologico"] for p in PESOS_LOCALES_ECO]
        np.testing.assert_allclose(globals_, expected, atol=1e-6)
        # ECO_01 (agua) debe ser el mayor local
        self.assertEqual(int(np.argmax(result.weights)), 0)

    def test_apendice_b_geo_and_soc_local_weights(self):
        for local in (PESOS_LOCALES_GEO, PESOS_LOCALES_SOC):
            m = self.ahp.matrix_from_weights(local)
            result = self.ahp.consistency_ratio(m)
            np.testing.assert_allclose(result.weights, np.asarray(local) / np.sum(local), atol=1e-6)
            self.assertLess(result.consistency_ratio, 1e-6)

    def test_global_21_sum_from_fixture(self):
        self.assertEqual(len(PESOS_GLOBALES_21), 21)
        self.assertEqual(len(IDS_21), 21)
        self.assertAlmostEqual(sum(PESOS_GLOBALES_21), 1.0, delta=0.0001)

    def test_aij_geometric_mean(self):
        m1 = np.array([[1, 2, 4], [0.5, 1, 2], [0.25, 0.5, 1]], dtype=float)
        m2 = np.array([[1, 4, 6], [0.25, 1, 2], [1 / 6, 0.5, 1]], dtype=float)
        agg = self.ahp.aggregate_aij([m1, m2])
        self.assertAlmostEqual(agg[0, 1], np.sqrt(8), places=6)
        self.assertAlmostEqual(agg[0, 1] * agg[1, 0], 1.0, places=6)
        result = self.ahp.consistency_ratio(agg)
        self.assertAlmostEqual(result.weights.sum(), 1.0, places=6)

    def test_cr_ge_010_warning_and_raise(self):
        # Matriz deliberadamente inconsistente (recíproca pero CR alta)
        bad = np.array(
            [
                [1, 9, 1 / 9],
                [1 / 9, 1, 9],
                [9, 1 / 9, 1],
            ],
            dtype=float,
        )
        soft = self.ahp.validate_cr(bad, raise_on_fail=False)
        self.assertFalse(soft.is_consistent)
        self.assertGreaterEqual(soft.consistency_ratio, 0.10)
        self.assertIn("ADVERTENCIA", soft.advertencia_cr)
        self.assertIn("CR=", soft.advertencia_cr)
        with self.assertRaises(ValueError) as ctx:
            self.ahp.validate_cr(bad, threshold=0.10, raise_on_fail=True)
        self.assertIn("ADVERTENCIA", str(ctx.exception))

    def test_diagnose_panel_flags_inconsistency(self):
        # Un experto consistente + dos inconsistentes → % > 50%
        good = self.ahp.matrix_from_weights([0.5, 0.3, 0.2])
        bad = np.array(
            [
                [1, 9, 1 / 9],
                [1 / 9, 1, 9],
                [9, 1 / 9, 1],
            ],
            dtype=float,
        )
        report = self.ahp.diagnose_panel([good, bad, bad])
        self.assertEqual(report.n_expertos, 3)
        self.assertEqual(report.n_inconsistentes, 2)
        self.assertTrue(report.advertencia_consenso)
        self.assertIn("Advertencia de consenso", report.mensaje)
        self.assertAlmostEqual(report.pesos_agregados.sum(), 1.0, places=6)

    def test_consistent_classic_3x3(self):
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
        self.assertLess(result.consistency_ratio, 0.10)
        self.assertEqual(result.random_index, SAATY_RI[3])

    def test_ic_formula(self):
        self.assertAlmostEqual(self.ahp.consistency_index(3.0, 3), 0.0)
        self.assertAlmostEqual(self.ahp.consistency_index(3.096, 3), 0.048, places=3)


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class AHPSeedIntegrationTests(TestCase):
    def test_load_initial_rules_global_weights_sum(self):
        call_command("load_initial_rules")
        ahp = ConjuntoPesosAHP.objects.get(nombre=DEFAULT_AHP_NOMBRE)
        pesos = list(
            PesoCriterio.objects.filter(conjunto=ahp)
            .order_by("criterio__id_criterio")
            .values_list("peso_global", flat=True)
        )
        self.assertEqual(len(pesos), 21)
        self.assertAlmostEqual(sum(pesos), 1.0, delta=0.0001)
        # CR del Apéndice B cargados en el conjunto
        self.assertAlmostEqual(ahp.cr_geohidro, 0.0035, places=4)
        self.assertAlmostEqual(ahp.cr_ecol, 0.0020, places=4)
        self.assertAlmostEqual(ahp.cr_socio, 0.0047, places=4)


if __name__ == "__main__":
    unittest.main()
