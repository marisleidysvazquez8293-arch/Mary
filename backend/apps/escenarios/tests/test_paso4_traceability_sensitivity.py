"""Tests PASO 4: trazabilidad, sensibilidad Tabla 4.3, PDF, consulta celda."""
from __future__ import annotations

import io
import zipfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.escenarios.models import Escenario
from apps.escenarios.services import (
    EscenarioExecutionService,
    ScenarioTraceabilityService,
    SensitivityService,
)
from apps.escenarios.services.sensitivity import TABLA_43_BLOCK_PERTURBATIONS
from apps.multicriterio.models import ConjuntoPesosAHP
from apps.multicriterio.tests.fixtures.apendice_b_pesos import IDS_21
from apps.usuarios.roles import ANALISTA_TERRITORIAL, AUDITOR
from apps.visualizacion.services import LEYENDA_LEGAL, PdfExpedienteService


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class Paso4ServicesTests(TestCase):
    def setUp(self):
        self.conjunto = ConjuntoPesosAHP.objects.create(
            nombre="AHP test",
            descripcion="test",
            cr_geohidro=0.0035,
            cr_ecol=0.0020,
            cr_socio=0.0047,
            es_agregado_grupo=True,
        )
        self.exec = EscenarioExecutionService()
        out = self.exec.execute(
            nombre="E0 base",
            version_reglas_usada="1.0.0",
            conjunto_pesos=self.conjunto,
            parametros_ejecucion={
                "demo_seed": 5,
                "shape": [6, 6],
                "n_criteria": 21,
                "cell_area_m2": 10_000.0,
            },
            weights_from_db=False,
        )
        self.escenario = out.escenario

    def test_tabla_43_perturbations_cover_blocks_and_magnitudes(self):
        bloques = {b for _, b, _ in TABLA_43_BLOCK_PERTURBATIONS}
        deltas = {d for _, _, d in TABLA_43_BLOCK_PERTURBATIONS}
        self.assertEqual(bloques, {"geohidrologico", "ecologico", "socioeconomico"})
        self.assertTrue(0.10 in {abs(d) for d in deltas})
        self.assertTrue(0.20 in {abs(d) for d in deltas})
        self.assertEqual(len(TABLA_43_BLOCK_PERTURBATIONS), 6)

    def test_pesos_e1_e2_sum_one(self):
        svc = SensitivityService(execution_service=self.exec)
        e1 = svc.pesos_e1_iguales_en_bloque()
        e2 = svc.pesos_e2_iguales_21()
        self.assertEqual(len(e1), 21)
        self.assertAlmostEqual(sum(e1.values()), 1.0, places=6)
        self.assertAlmostEqual(sum(e2.values()), 1.0, places=6)
        # E1: iguales dentro de GEO
        geo = [e1[c] for c in IDS_21 if c.startswith("GEO_")]
        self.assertTrue(all(abs(g - geo[0]) < 1e-9 for g in geo))

    def test_hash_trazabilidad_and_zip(self):
        trace = ScenarioTraceabilityService()
        h = trace.generar_hash_configuracion(self.escenario)
        self.assertEqual(len(h), 64)
        h2 = trace.generar_hash_configuracion(self.escenario)
        self.assertEqual(h, h2)
        blob = trace.generar_paquete_reproducibilidad(self.escenario.pk)
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            names = set(zf.namelist())
        self.assertIn("config.json", names)
        self.assertIn("pesos_ahp.json", names)
        self.assertIn("capas_hashes.json", names)
        self.assertIn("software.json", names)

    def test_sensibilidad_e0_e8_jaccard_favorable_optimo(self):
        svc = SensitivityService(execution_service=self.exec)
        report = svc.ejecutar_analisis_sensibilidad(self.escenario, persist=False)
        self.assertEqual(len(report.experiments), 9)
        ids = [e["id"] for e in report.experiments]
        self.assertEqual(ids, [f"E{i}" for i in range(9)])
        self.assertGreater(len(report.jaccard_vs_e0), 0)
        for pair in report.jaccard_vs_e0:
            self.assertGreaterEqual(pair["jaccard"], 0.0)
            self.assertLessEqual(pair["jaccard"], 1.0)
        self.assertIn("celdas", report.zonas_estables_favorable_optimo)

    def test_jaccard_entre_escenarios(self):
        svc = SensitivityService(execution_service=self.exec)
        out2 = self.exec.execute(
            nombre="E0b",
            version_reglas_usada="1.0.0",
            conjunto_pesos=self.conjunto,
            parametros_ejecucion={
                "demo_seed": 5,
                "shape": [6, 6],
                "n_criteria": 21,
                "sensitivity_id": "copy",
            },
            weights_from_db=False,
        )
        # Misma config demo_seed → mismos resultados → Jaccard alto
        # (hash_config distinto por sensitivity_id)
        jac = svc.calcular_indice_jaccard(self.escenario, out2.escenario)
        self.assertIn("jaccard", jac)
        self.assertEqual(jac["clases"], ["Favorable", "Óptimo"])

    def test_pdf_incluye_leyenda_legal_y_hash(self):
        pdf = PdfExpedienteService().generar_pdf_expediente(self.escenario.pk)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1500)
        # Leyenda + hash van en metadatos Subject/Keywords (sin Flate)
        self.assertIn(b"Documento de apoyo a la toma de decisiones", pdf)
        self.assertIn(self.escenario.hash_configuracion[:16].encode(), pdf)
        self.assertEqual(
            LEYENDA_LEGAL,
            "Documento de apoyo a la toma de decisiones; no constituye una "
            "recomendación vinculante de sitio ni sustituye los estudios de "
            "impacto ambiental normativos",
        )

    def test_consulta_celda_21_factores(self):
        payload = self.exec.consultar_celda(self.escenario, row=1, col=1)
        self.assertEqual(len(payload["factores"]), 21)
        self.assertIn("restricciones", payload)
        self.assertIn("advertencias", payload)
        self.assertIn("class_label", payload)


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class Paso4APITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        self.analista = User.objects.create_user("analista4", password="x")
        g = Group.objects.create(name=ANALISTA_TERRITORIAL)
        self.analista.groups.add(g)
        self.auditor = User.objects.create_user("auditor4", password="x")
        ga = Group.objects.create(name=AUDITOR)
        self.auditor.groups.add(ga)
        self.conjunto = ConjuntoPesosAHP.objects.create(
            nombre="API AHP",
            descripcion="",
            cr_geohidro=0.0,
            cr_ecol=0.0,
            cr_socio=0.0,
        )
        self.exec = EscenarioExecutionService()
        out = self.exec.execute(
            nombre="API E0",
            version_reglas_usada="1.0.0",
            conjunto_pesos=self.conjunto,
            parametros_ejecucion={
                "demo_seed": 2,
                "shape": [5, 5],
                "n_criteria": 21,
            },
            weights_from_db=False,
        )
        self.escenario = out.escenario

    def test_endpoints_hash_zip_pdf_celda_sensibilidad(self):
        self.client.force_authenticate(self.analista)
        eid = self.escenario.pk

        h = self.client.get(f"/api/escenarios/{eid}/hash/")
        self.assertEqual(h.status_code, 200, h.content)
        self.assertEqual(len(h.data["hash_trazabilidad"]), 64)

        z = self.client.get(f"/api/escenarios/{eid}/reproducibilidad/")
        self.assertEqual(z.status_code, 200)
        self.assertEqual(z["Content-Type"], "application/zip")
        self.assertTrue(z.content[:2] == b"PK")

        p = self.client.get(f"/api/escenarios/{eid}/pdf/")
        self.assertEqual(p.status_code, 200)
        self.assertEqual(p["Content-Type"], "application/pdf")
        self.assertTrue(p.content.startswith(b"%PDF"))

        c = self.client.get(
            f"/api/escenarios/{eid}/consulta-celda/", {"row": 0, "col": 0}
        )
        self.assertEqual(c.status_code, 200, c.content)
        self.assertEqual(len(c.data["factores"]), 21)

        s = self.client.post(
            "/api/escenarios/sensibilidad/",
            {
                "conjunto_pesos_id": self.conjunto.pk,
                "version_reglas_usada": "1.0.0",
                "escenario_base_id": eid,
                "persist": False,
                "parametros_ejecucion": {
                    "demo_seed": 2,
                    "shape": [5, 5],
                },
            },
            format="json",
        )
        self.assertEqual(s.status_code, 200, s.content)
        self.assertEqual(len(s.data["experiments"]), 9)
        self.assertIn("jaccard_vs_e0", s.data)
