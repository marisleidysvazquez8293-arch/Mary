"""Tests GEE — mocks / modo degradado (sin credenciales reales)."""
from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

import apps.adquisicion.services.gee_service as gee_mod
from apps.adquisicion.services.gee_service import (
    GEE_LAYER_CATALOG,
    ROI_VALLES_BBOX_4326,
    GeeService,
)
from apps.usuarios.roles import ANALISTA_TERRITORIAL, AUDITOR


class GeeServiceDegradedTests(TestCase):
    def setUp(self):
        # Reset class state between tests
        GeeService._ee = None
        GeeService._initialized = False
        GeeService._init_error = None
        GeeService._credentials_source = None
        gee_mod._singleton = None

    def test_import_does_not_crash_without_creds(self):
        import os

        cleaned = {
            k: v
            for k, v in os.environ.items()
            if not (k.startswith("GEE_") or k == "GOOGLE_APPLICATION_CREDENTIALS")
        }
        with patch.dict("os.environ", cleaned, clear=True):
            svc = GeeService(auto_init=True)
            st = svc.status()
            self.assertEqual(st["mode"], "degraded")
            self.assertFalse(st["available"])
            self.assertEqual(st["gee_crs"], "EPSG:4326")
            self.assertEqual(st["analisis_crs"], "EPSG:32613")

    def test_catalog_contract(self):
        ids = {c["id"] for c in GEE_LAYER_CATALOG}
        self.assertIn("dem_srtm", ids)
        self.assertIn("pendiente_srtm", ids)
        self.assertIn("sentinel2_ndvi", ids)
        self.assertIn("landsat8_rgb", ids)
        self.assertIn("gsw_occurrence", ids)
        self.assertEqual(len(ROI_VALLES_BBOX_4326), 4)
        west, south, east, north = ROI_VALLES_BBOX_4326
        self.assertLess(west, east)
        self.assertLess(south, north)

    def test_list_layers_degraded_has_tile_template(self):
        GeeService._initialized = False
        GeeService._ee = None
        GeeService._init_error = "test degraded"
        svc = GeeService(auto_init=False)

        with patch.object(GeeService, "is_ready", new_callable=PropertyMock) as ready:
            ready.return_value = False
            mid = svc.get_map_id("dem_srtm")
            capas = []
            for meta in GEE_LAYER_CATALOG:
                row = dict(meta)
                row["tile_url_template"] = svc.get_map_id(
                    meta["id"]
                ).tile_url_template
                capas.append(row)
        self.assertEqual(len(capas), len(GEE_LAYER_CATALOG))
        self.assertTrue(mid.degraded)
        self.assertIn("{z}", mid.tile_url_template)

    def test_ficha_consulta_celda_degraded(self):
        svc = GeeService(auto_init=False)
        GeeService._initialized = False
        GeeService._init_error = "sin creds"

        with patch.object(GeeService, "is_ready", new_callable=PropertyMock) as ready:
            ready.return_value = False
            ficha = svc.ficha_consulta_celda(lon=-104.05, lat=20.55)
        self.assertTrue(ficha["degraded"])
        self.assertIn("restricciones_nom083", ficha)
        self.assertIn("advertencias", ficha)
        self.assertTrue(
            any(a.get("id_criterio") == "SOC_01" for a in ficha["advertencias"])
        )

    def test_get_map_id_mocked_ready(self):
        svc = GeeService(auto_init=False)
        fake_image = MagicMock()
        fake_image.getMapId.return_value = {
            "mapid": "abc123",
            "token": "tok",
        }

        with patch.object(GeeService, "is_ready", new_callable=PropertyMock) as ready:
            ready.return_value = True
            with patch.object(svc, "build_layer_image", return_value=fake_image):
                mid = svc.get_map_id("dem_srtm")
        self.assertFalse(mid.degraded)
        self.assertEqual(mid.mapid, "abc123")
        self.assertIn("abc123", mid.tile_url_template)
        self.assertIn("{z}", mid.tile_url_template)


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class GeeAPIContractTests(TestCase):
    def setUp(self):
        GeeService._ee = None
        GeeService._initialized = False
        GeeService._init_error = "test"
        GeeService._credentials_source = None
        gee_mod._singleton = None

        User = get_user_model()
        self.client = APIClient()
        self.user = User.objects.create_user("gee_user", password="x")
        g = Group.objects.create(name=ANALISTA_TERRITORIAL)
        self.user.groups.add(g)
        self.auditor = User.objects.create_user("gee_aud", password="x")
        ga = Group.objects.create(name=AUDITOR)
        self.auditor.groups.add(ga)

    def test_status_unauthenticated(self):
        r = self.client.get("/api/gee/status/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(r.data["mode"], ("ready", "degraded"))
        self.assertIn("roi_valles_bbox_4326", r.data)

    def test_capas_and_tiles_and_consulta(self):
        self.client.force_authenticate(self.user)
        c = self.client.get("/api/gee/capas/?tiles=1")
        self.assertEqual(c.status_code, 200, c.content)
        self.assertGreaterEqual(len(c.data["capas"]), 5)
        self.assertEqual(c.data["crs_gee"], "EPSG:4326")

        layer_id = c.data["capas"][0]["id"]
        t = self.client.get(f"/api/gee/capas/{layer_id}/tiles/")
        self.assertEqual(t.status_code, 200, t.content)
        self.assertIn("tile_url_template", t.data)

        q = self.client.get(
            "/api/gee/consulta-celda/",
            {"lat": 20.55, "lon": -104.05},
        )
        self.assertEqual(q.status_code, 200, q.content)
        self.assertIn("advertencias", q.data)
        self.assertIn("gee", q.data)

        p = self.client.post(
            "/api/gee/consulta-celda/",
            {"lat": 20.55, "lon": -104.05, "scale_m": 30},
            format="json",
        )
        self.assertEqual(p.status_code, 200, p.content)

    def test_escenarios_still_alive(self):
        """Endpoints PASO 4 no se rompen con GEE."""
        r = self.client.get("/api/health/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["paso"], 4)

    def test_unknown_layer_404(self):
        self.client.force_authenticate(self.auditor)
        r = self.client.get("/api/gee/capas/no_existe/tiles/")
        self.assertEqual(r.status_code, 404)
