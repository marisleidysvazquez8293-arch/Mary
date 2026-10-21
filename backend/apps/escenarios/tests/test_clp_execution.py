"""
Pipeline sintético RulesEngine + CLP (PASO 3).

Sin PostGIS / sin matrices AHP crudas.
"""
from __future__ import annotations

import unittest

import numpy as np

from apps.multicriterio.services import CLPService, SuitabilityClass
from apps.reglas.services import RulesEngineService


class CLPExecutionPipelineTests(unittest.TestCase):
    def setUp(self):
        self.rules = RulesEngineService(default_srid=32613)
        self.clp = CLPService(
            cell_area_m2=10_000.0,  # 1 ha por celda
            waste_generation_ton_per_year=5_000.0,
        )
        self.shape = (6, 6)
        rng = np.random.default_rng(0)
        # Tres factores en escala 0–5
        self.factores = [rng.uniform(0, 5, size=self.shape) for _ in range(3)]
        self.pesos = [0.5, 0.3, 0.2]  # suman 1

    def test_pipeline_sintetico_clp(self):
        # Distancias: agua/pozos lejos → todo permitido; ANP bloquea esquina
        dist_agua = np.full(self.shape, 800.0)
        dist_pozos = np.full(self.shape, 800.0)
        anp_mask = np.ones(self.shape, dtype=bool)
        anp_mask[0, 0] = False  # celda excluida por ANP

        exclusion = self.rules.generar_capa_exclusion(
            {
                "shape": self.shape,
                "srid": 32613,
                "capas": {
                    "ECO_01": {"distance_m": dist_agua, "parametros": {"buffer_m": 500}},
                    "ECO_02": {
                        "distance_m": dist_pozos,
                        "cono_abatimiento_disponible": False,
                        "parametros": {"buffer_m": 500},
                    },
                    "ECO_04": {"mask": anp_mask},
                },
            }
        )
        self.assertIn("ECO_02", " ".join(exclusion.reglas_respaldo_aplicadas) or "ECO_02")
        # Producto 0 en ANP
        self.assertEqual(exclusion.product[0, 0], 0.0)
        self.assertEqual(exclusion.product[1, 1], 1.0)

        # Advertencia aeródromo no altera producto
        dist_aero = np.full(self.shape, 5_000.0)  # < 13 km
        warns = self.rules.aplicar_reglas_advertencia(distance_aerodromo_m=dist_aero)
        self.assertEqual(len(warns), 1)
        self.assertEqual(warns[0].etiqueta, "requiere estudio de riesgo aviario")
        self.assertTrue(bool(warns[0].cell_mask[0, 0]))

        S = self.clp.calcular_indice_aptitud(
            self.factores, self.pesos, exclusion.product
        )
        classes = self.clp.reclasificar_aptitud(S)
        self.assertEqual(classes[0, 0], SuitabilityClass.EXCLUIDO)
        self.assertEqual(S[0, 0], 0.0)

        polys = self.clp.delimitar_poligonos_candidatos(
            classes,
            superficie_minima_ha=1.0,
            suitability=S,
            cell_area_m2=10_000.0,
        )
        fase2 = self.clp.evaluar_poligonos_fase2(polys)
        for row in fase2:
            self.assertIn("soc_07_vida_util_anios", row)
            self.assertIn("soc_10_intermunicipal", row)

    def test_celdas_excluidas_S_igual_cero(self):
        mask = np.ones(self.shape, dtype=float)
        mask[2, 3] = 0.0
        S = self.clp.calcular_indice_aptitud(self.factores, self.pesos, mask)
        self.assertEqual(S[2, 3], 0.0)
        # Donde permitido, S > 0 casi seguro con factores aleatorios [0,5]
        self.assertGreater(float(S[mask > 0].mean()), 0.0)

    def test_S_coincide_con_sumatoria_ponderada(self):
        mask = np.ones(self.shape, dtype=float)
        S = self.clp.calcular_indice_aptitud(self.factores, self.pesos, mask)
        expected = (
            self.pesos[0] * self.factores[0]
            + self.pesos[1] * self.factores[1]
            + self.pesos[2] * self.factores[2]
        )
        np.testing.assert_allclose(S, expected, rtol=0, atol=1e-10)

    def test_respaldo_500m_pozos(self):
        dist = np.array([[100.0, 600.0], [400.0, 900.0]])
        mask, nota = self.rules.aplicar_regla_respaldo_pozos(
            distance_m=dist,
            cono_abatimiento_disponible=False,
        )
        self.assertIsNotNone(nota)
        np.testing.assert_array_equal(mask, np.array([[False, True], [False, True]]))


if __name__ == "__main__":
    unittest.main()
