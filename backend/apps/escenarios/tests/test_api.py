"""API tests for PASO 4 — sqlite, no PostGIS/GEE."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.escenarios.hashing import hash_configuracion, hash_resultado
from apps.escenarios.models import Escenario
from apps.escenarios.services import EscenarioExecutionService
from apps.multicriterio.models import ConjuntoPesosAHP
from apps.usuarios.roles import ADMINISTRADOR_TECNICO, ANALISTA_TERRITORIAL, AUDITOR


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class EscenarioAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        self.analista = User.objects.create_user("analista", password="x")
        g = Group.objects.create(name=ANALISTA_TERRITORIAL)
        self.analista.groups.add(g)

        self.auditor = User.objects.create_user("auditor", password="x")
        Group.objects.create(name=AUDITOR)
        self.auditor.groups.add(Group.objects.get(name=AUDITOR))

        self.admin_tech = User.objects.create_user("admin_tech", password="x")
        Group.objects.create(name=ADMINISTRADOR_TECNICO)
        self.admin_tech.groups.add(Group.objects.get(name=ADMINISTRADOR_TECNICO))

        self.conjunto = ConjuntoPesosAHP.objects.create(
            nombre="Test AHP",
            descripcion="test",
            cr_geohidro=0.0,
            cr_ecol=0.0,
            cr_socio=0.0,
            es_agregado_grupo=False,
        )

    def test_health_unauthenticated(self):
        r = self.client.get("/api/health/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "ok")

    def test_ejecutar_and_persist_hashes(self):
        self.client.force_authenticate(self.analista)
        payload = {
            "nombre": "E0 demo",
            "version_reglas_usada": "1.0.0",
            "conjunto_pesos_id": self.conjunto.pk,
            "parametros_ejecucion": {
                "demo_seed": 7,
                "shape": [6, 6],
                "n_criteria": 3,
                "weights": [0.5, 0.3, 0.2],
            },
            "weights_from_db": False,
        }
        r = self.client.post("/api/escenarios/ejecutar/", payload, format="json")
        self.assertIn(r.status_code, (200, 201), r.content)
        self.assertTrue(r.data["hash_configuracion"])
        self.assertTrue(r.data["hash_resultado"])
        esc = Escenario.objects.get(pk=r.data["id"])
        expected_cfg = hash_configuracion(
            version_reglas_usada="1.0.0",
            conjunto_pesos_id=self.conjunto.pk,
            parametros_ejecucion=esc.parametros_ejecucion,
        )
        self.assertEqual(esc.hash_configuracion, expected_cfg)
        self.assertEqual(esc.hash_resultado, hash_resultado(esc.resultados_json))
        self.assertIn("class_counts", esc.resultados_json)
        self.assertIn("geojson", esc.resultados_json)

    def test_reejecutar_reproduces_hash(self):
        self.client.force_authenticate(self.analista)
        svc = EscenarioExecutionService()
        out = svc.execute(
            nombre="repeat",
            version_reglas_usada="1.0.0",
            conjunto_pesos=self.conjunto,
            parametros_ejecucion={
                "demo_seed": 99,
                "shape": [5, 5],
                "weights": [0.4, 0.4, 0.2],
            },
            weights_from_db=False,
        )
        first_hash = out.escenario.hash_resultado
        r = self.client.post(f"/api/escenarios/{out.escenario.pk}/reejecutar/")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertTrue(r.data["config_unchanged"])
        self.assertTrue(r.data["resultado_reproducido"])
        self.assertEqual(r.data["hash_resultado_nuevo"], first_hash)

    def test_sensibilidad_e0_e8_jaccard(self):
        self.client.force_authenticate(self.analista)
        r = self.client.post(
            "/api/escenarios/sensibilidad/",
            {
                "version_reglas_usada": "1.0.0",
                "conjunto_pesos_id": self.conjunto.pk,
                "parametros_ejecucion": {
                    "demo_seed": 1,
                    "shape": [6, 6],
                    "weights": [0.34, 0.33, 0.33],
                },
                "persist": False,
            },
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(len(r.data["experiments"]), 9)
        self.assertEqual(r.data["experiments"][0]["id"], "E0")
        self.assertEqual(r.data["experiments"][-1]["id"], "E8")
        self.assertGreater(len(r.data["pairwise_jaccard"]), 0)
        # E0 vs E0 not in pairs; every jaccard in [0,1]
        for pair in r.data["pairwise_jaccard"]:
            self.assertGreaterEqual(pair["jaccard"], 0.0)
            self.assertLessEqual(pair["jaccard"], 1.0)

    def test_geojson_and_tilejson(self):
        self.client.force_authenticate(self.auditor)
        svc = EscenarioExecutionService()
        out = svc.execute(
            nombre="map",
            version_reglas_usada="1.0.0",
            conjunto_pesos=self.conjunto,
            parametros_ejecucion={"demo_seed": 3, "shape": [4, 4], "weights": [1, 0, 0]},
            weights_from_db=False,
        )
        g = self.client.get(f"/api/escenarios/{out.escenario.pk}/geojson/")
        self.assertEqual(g.status_code, 200, g.content)
        self.assertEqual(g.data["type"], "FeatureCollection")
        self.assertGreater(len(g.data["features"]), 0)
        self.assertEqual(g.data["sade_audit"]["hash_configuracion"], out.escenario.hash_configuracion)

        t = self.client.get(f"/api/escenarios/{out.escenario.pk}/tilejson/")
        self.assertEqual(t.status_code, 200, t.content)
        self.assertEqual(t.data["tilejson"], "3.0.0")
        self.assertEqual(t.data["sade"]["status"], "stub")
        self.assertIn("geojson", t.data["sade"])

    def test_auditor_cannot_execute(self):
        self.client.force_authenticate(self.auditor)
        r = self.client.post(
            "/api/escenarios/ejecutar/",
            {
                "nombre": "x",
                "conjunto_pesos_id": self.conjunto.pk,
                "parametros_ejecucion": {"weights": [1, 0, 0]},
            },
            format="json",
        )
        self.assertEqual(r.status_code, 403)

    def test_same_config_idempotent_hash(self):
        self.client.force_authenticate(self.admin_tech)
        payload = {
            "nombre": "A",
            "version_reglas_usada": "1.0.0",
            "conjunto_pesos_id": self.conjunto.pk,
            "parametros_ejecucion": {
                "demo_seed": 11,
                "shape": [4, 4],
                "weights": [0.2, 0.3, 0.5],
            },
            "weights_from_db": False,
        }
        r1 = self.client.post("/api/escenarios/ejecutar/", payload, format="json")
        payload["nombre"] = "B"  # name change should still hit same config hash
        r2 = self.client.post("/api/escenarios/ejecutar/", payload, format="json")
        self.assertEqual(r1.data["hash_configuracion"], r2.data["hash_configuracion"])
        self.assertEqual(r1.data["id"], r2.data["id"])
        self.assertEqual(Escenario.objects.count(), 1)


class HashingUnitTests(TestCase):
    def test_hash_stable(self):
        a = hash_configuracion(
            version_reglas_usada="1.0.0",
            conjunto_pesos_id=1,
            parametros_ejecucion={"b": 2, "a": 1},
        )
        b = hash_configuracion(
            version_reglas_usada="1.0.0",
            conjunto_pesos_id=1,
            parametros_ejecucion={"a": 1, "b": 2},
        )
        self.assertEqual(a, b)
