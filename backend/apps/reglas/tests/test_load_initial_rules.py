"""Tests de idempotencia y conteo de load_initial_rules (Tabla 4.1)."""
from __future__ import annotations

from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.multicriterio.models import ConjuntoPesosAHP, PesoCriterio
from apps.reglas.data.initial_rules import (
    CR_BLOQUES,
    CRITERIOS_SEED,
    DEFAULT_AHP_NOMBRE,
    PESOS_GLOBALES,
)
from apps.reglas.models import Criterio, Regla


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class LoadInitialRulesTests(TestCase):
    def test_seed_structure_matches_thesis(self):
        self.assertEqual(len(CRITERIOS_SEED), 21)
        self.assertEqual(
            sum(1 for c in CRITERIOS_SEED if c["bloque"] == "geohidrologico"), 7
        )
        self.assertEqual(
            sum(1 for c in CRITERIOS_SEED if c["bloque"] == "ecologico"), 4
        )
        self.assertEqual(
            sum(1 for c in CRITERIOS_SEED if c["bloque"] == "socioeconomico"), 10
        )
        self.assertAlmostEqual(sum(PESOS_GLOBALES.values()), 1.0, places=3)

    def test_command_loads_exactly_21_and_is_idempotent(self):
        call_command("load_initial_rules")
        self.assertEqual(Criterio.objects.count(), 21)
        self.assertEqual(Regla.objects.count(), 21)
        self.assertEqual(
            Criterio.objects.filter(bloque="geohidrologico").count(), 7
        )
        self.assertEqual(Criterio.objects.filter(bloque="ecologico").count(), 4)
        self.assertEqual(
            Criterio.objects.filter(bloque="socioeconomico").count(), 10
        )

        ahp = ConjuntoPesosAHP.objects.get(nombre=DEFAULT_AHP_NOMBRE)
        self.assertAlmostEqual(ahp.cr_geohidro, CR_BLOQUES["cr_geohidro"])
        self.assertAlmostEqual(ahp.cr_ecol, CR_BLOQUES["cr_ecol"])
        self.assertAlmostEqual(ahp.cr_socio, CR_BLOQUES["cr_socio"])
        self.assertEqual(PesoCriterio.objects.filter(conjunto=ahp).count(), 21)
        self.assertAlmostEqual(
            sum(PesoCriterio.objects.filter(conjunto=ahp).values_list(
                "peso_global", flat=True
            )),
            1.0,
            places=3,
        )

        # Idempotencia
        call_command("load_initial_rules")
        self.assertEqual(Criterio.objects.count(), 21)
        self.assertEqual(Regla.objects.count(), 21)
        self.assertEqual(ConjuntoPesosAHP.objects.filter(nombre=DEFAULT_AHP_NOMBRE).count(), 1)
        self.assertEqual(PesoCriterio.objects.filter(conjunto=ahp).count(), 21)

        # IDs canónicos
        ids = set(Criterio.objects.values_list("id_criterio", flat=True))
        expected = {c["id_criterio"] for c in CRITERIOS_SEED}
        self.assertEqual(ids, expected)
        self.assertIn("ECO_01", ids)
        self.assertIn("SOC_10", ids)
        self.assertNotIn("ECO_07", ids)  # ya no hay 7 ecológicos
        self.assertTrue(
            Criterio.objects.get(id_criterio="SOC_07").nombre.startswith("Vida útil")
        )
        self.assertTrue(
            Criterio.objects.get(id_criterio="ECO_01").nombre.startswith(
                "Cuerpos de agua"
            )
        )
