"""
GeeService — integración Google Earth Engine para SADE (adquisición).

Inicialización con cuenta de servicio vía entorno. Si faltan credenciales,
el módulo NO falla al importar: opera en modo degradado documentado.

CRS:
  - GEE / visor web: EPSG:4326 (lon/lat)
  - Análisis PostGIS / CLP: EPSG:32613 (UTM 13N)

Capas iniciales (catálogo tesis / fuentes públicas GEE):
  - DEM SRTM (pendiente / elevación)
  - Sentinel-2 y Landsat (cobertura / NDVI proxy)
  - JRC Global Surface Water (cuerpos de agua → ECO_01)
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

logger = logging.getLogger(__name__)

# ROI región Valles de Jalisco (aprox. Ameca y municipios vecinos), EPSG:4326
# [west, south, east, north]
ROI_VALLES_BBOX_4326: tuple[float, float, float, float] = (
    -104.55,
    20.25,
    -103.45,
    21.15,
)

ROI_VALLES_CENTER_4326: tuple[float, float] = (-104.05, 20.55)

# Catálogo de capas GEE expuestas al frontend (id estable → asset / composición)
GEE_LAYER_CATALOG: list[dict[str, Any]] = [
    {
        "id": "dem_srtm",
        "nombre": "Elevación SRTM 30 m",
        "descripcion": "NASA SRTM Digital Elevation — base para pendiente (GEO).",
        "coleccion": "USGS/SRTMGL1_003",
        "tipo": "elevation",
        "criterios_relacionados": ["GEO_04", "GEO_07"],
        "vis_params": {
            "min": 800,
            "max": 2800,
            "palette": ["006633", "E5FFCC", "662A00", "D8D8D8", "FFFFFF"],
        },
        "estado": "disponible",
    },
    {
        "id": "pendiente_srtm",
        "nombre": "Pendiente derivada de SRTM",
        "descripcion": "ee.Terrain.slope sobre SRTM (grados). Pendiente GEE.",
        "coleccion": "USGS/SRTMGL1_003",
        "tipo": "slope",
        "criterios_relacionados": ["GEO_04"],
        "vis_params": {
            "min": 0,
            "max": 40,
            "palette": ["ffffff", "ffff00", "ff0000"],
        },
        "estado": "disponible",
    },
    {
        "id": "sentinel2_ndvi",
        "nombre": "Sentinel-2 NDVI (mediana anual)",
        "descripcion": "Cobertura vegetal / proxy ecosistémico (ECO_03).",
        "coleccion": "COPERNICUS/S2_SR_HARMONIZED",
        "tipo": "ndvi",
        "criterios_relacionados": ["ECO_03", "SOC_04"],
        "vis_params": {
            "min": 0,
            "max": 0.8,
            "palette": ["brown", "yellow", "green"],
        },
        "estado": "disponible",
    },
    {
        "id": "landsat8_rgb",
        "nombre": "Landsat 8 RGB (mediana)",
        "descripcion": "Cobertura óptica de referencia (contexto territorial).",
        "coleccion": "LANDSAT/LC08/C02/T1_L2",
        "tipo": "rgb",
        "criterios_relacionados": [],
        "vis_params": {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 0, "max": 3000},
        "estado": "disponible",
    },
    {
        "id": "gsw_occurrence",
        "nombre": "JRC Global Surface Water — occurrence",
        "descripcion": "Presencia de agua superficial (ECO_01 / NOM-083).",
        "coleccion": "JRC/GSW1_4/GlobalSurfaceWater",
        "tipo": "water",
        "criterios_relacionados": ["ECO_01", "ECO_03"],
        "vis_params": {
            "bands": ["occurrence"],
            "min": 0,
            "max": 100,
            "palette": ["ffffff", "0000ff"],
        },
        "estado": "disponible",
    },
]


class GeeDegradedMode(RuntimeError):
    """Operación GEE solicitada sin credenciales / sin ee inicializado."""


@dataclass
class GeeStatus:
    available: bool
    mode: str  # "ready" | "degraded"
    message: str
    project: str | None = None
    credentials_source: str | None = None


@dataclass
class MapIdResult:
    layer_id: str
    mapid: str
    token: str
    tile_url_template: str
    vis_params: dict[str, Any] = field(default_factory=dict)
    degraded: bool = False
    detail: str = ""


class GeeService:
    """
    Cliente GEE con inicialización perezosa y modo degradado.

    Variables de entorno (cualquiera basta):
      GOOGLE_APPLICATION_CREDENTIALS  — ruta a JSON de cuenta de servicio
      GEE_SERVICE_ACCOUNT             — email de la cuenta
      GEE_PRIVATE_KEY / GEE_PRIVATE_KEY_PATH — PEM o ruta al JSON/PEM
      GEE_PROJECT                     — proyecto GCP (opcional, ee.Initialize)
    """

    _ee = None  # módulo earthengine, si importable
    _initialized = False
    _init_error: str | None = None
    _credentials_source: str | None = None

    def __init__(self, *, auto_init: bool = True):
        if auto_init:
            self.ensure_initialized()

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------

    @classmethod
    def ensure_initialized(cls) -> GeeStatus:
        if cls._initialized and cls._ee is not None:
            return GeeStatus(
                available=True,
                mode="ready",
                message="Google Earth Engine inicializado.",
                project=os.environ.get("GEE_PROJECT") or None,
                credentials_source=cls._credentials_source,
            )
        try:
            import ee  # type: ignore
        except ImportError as exc:
            cls._init_error = (
                "Paquete earthengine-api no instalado. "
                "pip install earthengine-api"
            )
            logger.warning("GEE degradado: %s (%s)", cls._init_error, exc)
            return cls._degraded_status()

        cls._ee = ee
        creds, source = cls._resolve_credentials()
        if creds is None:
            cls._init_error = (
                "Sin credenciales GEE. Configure GOOGLE_APPLICATION_CREDENTIALS "
                "o GEE_SERVICE_ACCOUNT + GEE_PRIVATE_KEY[_PATH]. "
                "Ver backend/.env.example."
            )
            logger.info("GEE en modo degradado: %s", cls._init_error)
            return cls._degraded_status()

        try:
            project = os.environ.get("GEE_PROJECT") or None
            if project:
                ee.Initialize(creds, project=project)
            else:
                ee.Initialize(creds)
            cls._initialized = True
            cls._credentials_source = source
            cls._init_error = None
            logger.info("ee.Initialize OK (source=%s)", source)
            return GeeStatus(
                available=True,
                mode="ready",
                message="Google Earth Engine inicializado.",
                project=project,
                credentials_source=source,
            )
        except Exception as exc:  # noqa: BLE001 — no tumbar el proceso Django
            cls._init_error = f"ee.Initialize falló: {exc}"
            cls._initialized = False
            logger.exception("GEE degradado tras fallo de Initialize")
            return cls._degraded_status()

    @classmethod
    def _degraded_status(cls) -> GeeStatus:
        return GeeStatus(
            available=False,
            mode="degraded",
            message=cls._init_error or "GEE no disponible.",
            project=os.environ.get("GEE_PROJECT") or None,
            credentials_source=cls._credentials_source,
        )

    @classmethod
    def _resolve_credentials(cls) -> tuple[Any | None, str | None]:
        """Devuelve (credentials, etiqueta_fuente) o (None, None)."""
        try:
            import ee  # type: ignore
            from google.oauth2 import service_account as sa
        except ImportError:
            return None, None

        # 1) GOOGLE_APPLICATION_CREDENTIALS → JSON path
        gac = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        if gac and Path(gac).is_file():
            try:
                creds = ee.ServiceAccountCredentials(None, key_file=gac)
                return creds, f"GOOGLE_APPLICATION_CREDENTIALS:{gac}"
            except Exception:
                try:
                    creds = sa.Credentials.from_service_account_file(
                        gac,
                        scopes=["https://www.googleapis.com/auth/earthengine"],
                    )
                    return creds, f"GOOGLE_APPLICATION_CREDENTIALS:{gac}"
                except Exception as exc:
                    logger.warning("No se pudo cargar GAC %s: %s", gac, exc)

        email = os.environ.get("GEE_SERVICE_ACCOUNT", "").strip()
        key_path = os.environ.get("GEE_PRIVATE_KEY_PATH", "").strip()
        key_inline = os.environ.get("GEE_PRIVATE_KEY", "").strip()

        # 2) Email + JSON path
        if email and key_path and Path(key_path).is_file():
            try:
                if key_path.endswith(".json"):
                    creds = ee.ServiceAccountCredentials(email, key_file=key_path)
                else:
                    # PEM file
                    pem = Path(key_path).read_text(encoding="utf-8")
                    info = {
                        "type": "service_account",
                        "client_email": email,
                        "private_key": pem.replace("\\n", "\n"),
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    creds = sa.Credentials.from_service_account_info(
                        info,
                        scopes=["https://www.googleapis.com/auth/earthengine"],
                    )
                return creds, f"GEE_SERVICE_ACCOUNT+PATH:{key_path}"
            except Exception as exc:
                logger.warning("Credenciales path fallaron: %s", exc)

        # 3) Email + private key inline (PEM o JSON string)
        if email and key_inline:
            try:
                if key_inline.lstrip().startswith("{"):
                    info = json.loads(key_inline)
                    creds = sa.Credentials.from_service_account_info(
                        info,
                        scopes=["https://www.googleapis.com/auth/earthengine"],
                    )
                else:
                    info = {
                        "type": "service_account",
                        "client_email": email,
                        "private_key": key_inline.replace("\\n", "\n"),
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    creds = sa.Credentials.from_service_account_info(
                        info,
                        scopes=["https://www.googleapis.com/auth/earthengine"],
                    )
                return creds, "GEE_SERVICE_ACCOUNT+GEE_PRIVATE_KEY"
            except Exception as exc:
                logger.warning("Credenciales inline fallaron: %s", exc)

        return None, None

    @property
    def is_ready(self) -> bool:
        st = self.ensure_initialized()
        return st.available and self._initialized

    def status(self) -> dict[str, Any]:
        st = self.ensure_initialized()
        return {
            "available": st.available,
            "mode": st.mode,
            "message": st.message,
            "project": st.project,
            "credentials_source": st.credentials_source,
            "roi_valles_bbox_4326": list(ROI_VALLES_BBOX_4326),
            "roi_center_4326": list(ROI_VALLES_CENTER_4326),
            "analisis_crs": "EPSG:32613",
            "gee_crs": "EPSG:4326",
            "capas_catalogo": len(GEE_LAYER_CATALOG),
        }

    # ------------------------------------------------------------------
    # Geometría ROI
    # ------------------------------------------------------------------

    def roi_geometry(self, bbox: Sequence[float] | None = None) -> Any:
        """ee.Geometry.Rectangle en EPSG:4326."""
        if not self.is_ready:
            raise GeeDegradedMode(self._init_error or "GEE degradado")
        ee = self._ee
        b = list(bbox or ROI_VALLES_BBOX_4326)
        # ee.Geometry.Rectangle([west, south, east, north])
        return ee.Geometry.Rectangle(b, proj="EPSG:4326", geodesic=False)

    def point_geometry(self, lon: float, lat: float) -> Any:
        if not self.is_ready:
            raise GeeDegradedMode(self._init_error or "GEE degradado")
        return self._ee.Geometry.Point([float(lon), float(lat)])

    # ------------------------------------------------------------------
    # Colecciones / imágenes
    # ------------------------------------------------------------------

    def build_layer_image(self, layer_id: str) -> Any:
        """Construye ee.Image (o RGB composite) para un id del catálogo."""
        if not self.is_ready:
            raise GeeDegradedMode(self._init_error or "GEE degradado")
        ee = self._ee
        meta = self.get_layer_meta(layer_id)
        if meta is None:
            raise ValueError(f"Capa GEE desconocida: {layer_id}")
        tipo = meta["tipo"]
        region = self.roi_geometry()

        if tipo == "elevation":
            return ee.Image(meta["coleccion"]).clip(region)
        if tipo == "slope":
            dem = ee.Image(meta["coleccion"])
            return ee.Terrain.slope(dem).clip(region)
        if tipo == "water":
            return (
                ee.Image(meta["coleccion"]).select("occurrence").clip(region)
            )
        if tipo == "ndvi":
            col = (
                ee.ImageCollection(meta["coleccion"])
                .filterBounds(region)
                .filterDate("2023-01-01", "2024-01-01")
                .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
            )

            def _ndvi(img):
                return img.normalizedDifference(["B8", "B4"]).rename("NDVI")

            return col.map(_ndvi).median().clip(region)
        if tipo == "rgb":
            col = (
                ee.ImageCollection(meta["coleccion"])
                .filterBounds(region)
                .filterDate("2023-01-01", "2024-01-01")
            )
            return col.median().clip(region)
        raise ValueError(f"Tipo de capa no soportado: {tipo}")

    @staticmethod
    def get_layer_meta(layer_id: str) -> dict[str, Any] | None:
        for row in GEE_LAYER_CATALOG:
            if row["id"] == layer_id:
                return dict(row)
        return None

    def list_layers(self, *, include_tiles: bool = True) -> list[dict[str, Any]]:
        """Catálogo + TileURL XYZ (o plantilla degradada)."""
        out: list[dict[str, Any]] = []
        ready = self.is_ready
        for meta in GEE_LAYER_CATALOG:
            row = dict(meta)
            row["gee_ready"] = ready
            if include_tiles:
                try:
                    mid = self.get_map_id(meta["id"])
                    row["tile_url_template"] = mid.tile_url_template
                    row["mapid"] = mid.mapid
                    row["token"] = mid.token
                    row["degraded"] = mid.degraded
                except Exception as exc:  # noqa: BLE001
                    row["tile_url_template"] = None
                    row["error"] = str(exc)
                    row["degraded"] = True
            out.append(row)
        return out

    # ------------------------------------------------------------------
    # Map ID / tiles XYZ
    # ------------------------------------------------------------------

    def get_map_id(
        self,
        layer_id: str,
        vis_params: Mapping[str, Any] | None = None,
    ) -> MapIdResult:
        meta = self.get_layer_meta(layer_id)
        if meta is None:
            raise ValueError(f"Capa GEE desconocida: {layer_id}")
        vis = dict(vis_params or meta.get("vis_params") or {})

        if not self.is_ready:
            # Plantilla documentada; el frontend puede mostrar aviso degradado
            return MapIdResult(
                layer_id=layer_id,
                mapid="",
                token="",
                tile_url_template=(
                    "https://earthengine.googleapis.com/v1/projects/"
                    "{project}/maps/{mapid}/tiles/{z}/{x}/{y}"
                ),
                vis_params=vis,
                degraded=True,
                detail=self._init_error or "GEE degradado",
            )

        image = self.build_layer_image(layer_id)
        map_dict = image.getMapId(vis)
        mapid = map_dict.get("mapid") or map_dict.get("mapId") or ""
        token = map_dict.get("token") or ""
        # URL clásica GEE tiles (compatible Leaflet/OpenLayers XYZ)
        if "tile_fetcher" in map_dict and hasattr(
            map_dict["tile_fetcher"], "url_format"
        ):
            template = map_dict["tile_fetcher"].url_format
        else:
            template = (
                f"https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}"
                f"?token={token}"
            )
        return MapIdResult(
            layer_id=layer_id,
            mapid=str(mapid),
            token=str(token),
            tile_url_template=template,
            vis_params=vis,
            degraded=False,
        )

    def get_tile_url_template(self, layer_id: str) -> str:
        return self.get_map_id(layer_id).tile_url_template

    # ------------------------------------------------------------------
    # Consulta de celda (reduceRegion) — híbrido
    # ------------------------------------------------------------------

    def reduce_region_at(
        self,
        lon: float,
        lat: float,
        *,
        scale_m: float = 30.0,
        layer_ids: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """
        Muestrea capas GEE en un punto (lon, lat EPSG:4326) con reduceRegion.
        En modo degradado devuelve valores None y bandera degraded=True.
        """
        ids = list(layer_ids) if layer_ids else [c["id"] for c in GEE_LAYER_CATALOG]
        base = {
            "lon": float(lon),
            "lat": float(lat),
            "crs": "EPSG:4326",
            "scale_m": scale_m,
            "degraded": not self.is_ready,
            "valores": {},
        }
        if not self.is_ready:
            base["detail"] = self._init_error
            base["valores"] = {lid: None for lid in ids}
            return base

        ee = self._ee
        point = self.point_geometry(lon, lat)
        valores: dict[str, Any] = {}
        for lid in ids:
            try:
                img = self.build_layer_image(lid)
                # Una banda: first; RGB: mean de bandas seleccionadas
                reduced = img.reduceRegion(
                    reducer=ee.Reducer.first(),
                    geometry=point,
                    scale=scale_m,
                    maxPixels=1e6,
                )
                valores[lid] = reduced.getInfo()
            except Exception as exc:  # noqa: BLE001
                valores[lid] = {"error": str(exc)}
        base["valores"] = valores
        return base

    def ficha_consulta_celda(
        self,
        *,
        lon: float | None = None,
        lat: float | None = None,
        x: float | None = None,
        y: float | None = None,
        escenario: Any | None = None,
        scale_m: float = 30.0,
    ) -> dict[str, Any]:
        """
        Ficha híbrida: reduceRegion GEE + (opcional) consulta escenario PostGIS/demo.

        Incluye S, clase, factores, restricciones NOM-083, advertencia aeródromo.
        """
        # Convertir UTM 32613 → 4326 aproximado si solo vienen x/y
        if (lon is None or lat is None) and x is not None and y is not None:
            lon, lat = _utm13n_to_lonlat(float(x), float(y))
        if lon is None or lat is None:
            raise ValueError("Indique lat/lon (4326) o x/y (32613)")

        gee_sample = self.reduce_region_at(lon, lat, scale_m=scale_m)
        ficha: dict[str, Any] = {
            "fuente": "gee+hibrido",
            "coordenadas": {
                "lon": lon,
                "lat": lat,
                "crs_gee": "EPSG:4326",
                "crs_analisis": "EPSG:32613",
            },
            "gee": gee_sample,
            "suitability_S": None,
            "clase": None,
            "factores": [],
            "restricciones_nom083": [],
            "advertencias": [],
            "degraded": gee_sample.get("degraded", False),
        }

        # Restricciones derivadas de GSW (agua) — NOM-083 / ECO_01
        gsw = (gee_sample.get("valores") or {}).get("gsw_occurrence") or {}
        occurrence = None
        if isinstance(gsw, dict):
            occurrence = gsw.get("occurrence")
        if occurrence is not None and float(occurrence) > 0:
            ficha["restricciones_nom083"].append(
                {
                    "id_criterio": "ECO_01",
                    "norma": "NOM-083-SEMARNAT-2003",
                    "motivo": (
                        f"Global Surface Water occurrence={occurrence}: "
                        "posible cuerpo de agua / zona inundable; verificar buffer 500 m."
                    ),
                    "valor_gee": occurrence,
                }
            )

        # Pendiente alta (proxy GEO_04)
        slope = (gee_sample.get("valores") or {}).get("pendiente_srtm") or {}
        slope_val = None
        if isinstance(slope, dict):
            # SRTM slope band often named 'slope'
            slope_val = slope.get("slope") or next(iter(slope.values()), None)
        if slope_val is not None and float(slope_val) > 30:
            ficha["restricciones_nom083"].append(
                {
                    "id_criterio": "GEO_04",
                    "norma": "NOM-083 / criterio modelo",
                    "motivo": f"Pendiente elevada ({slope_val}°).",
                    "valor_gee": slope_val,
                }
            )

        # Híbrido: enriquecer con escenario local si se pasa
        if escenario is not None:
            try:
                from apps.escenarios.services import EscenarioExecutionService

                local = EscenarioExecutionService().consultar_celda(
                    escenario, lon=lon, lat=lat
                )
                ficha["suitability_S"] = local.get("suitability")
                ficha["clase"] = {
                    "code": local.get("class_code"),
                    "label": local.get("class_label"),
                }
                ficha["factores"] = local.get("factores") or []
                for adv in local.get("advertencias") or []:
                    ficha["advertencias"].append(adv)
                for r in local.get("restricciones") or []:
                    ficha["restricciones_nom083"].append(
                        {**r, "fuente": "escenario_local"}
                    )
            except Exception as exc:  # noqa: BLE001
                ficha["hibrido_error"] = str(exc)

        # Advertencia aeródromo (SOC_01) — placeholder si no hay capa GEE aún
        if not any(
            a.get("id_criterio") == "SOC_01" for a in ficha["advertencias"]
        ):
            ficha["advertencias"].append(
                {
                    "id_criterio": "SOC_01",
                    "message": (
                        "Verificar distancia a aeródromo (<13 km requiere "
                        "estudio de riesgo aviario; no excluye)."
                    ),
                    "fuente": "regla_advertencia",
                }
            )

        return ficha


def _utm13n_to_lonlat(x: float, y: float) -> tuple[float, float]:
    """
    Conversión aproximada UTM 13N → WGS84 (sin pyproj; suficiente para demos).
    Para producción preferir pyproj/GDAL.
    """
    # Fórmulas simplificadas centradas en la zona Valles
    lon0 = -105.0  # meridiano central UTM 13N
    # aproximación lineal local alrededor de Ameca
    lon = lon0 + (x - 500_000.0) / 92_000.0
    lat = (y - 0.0) / 110_540.0  # ~1° lat ≈ 110.54 km
    # Ajuste empírico: y≈2_280_000 → lat≈20.6
    lat = 20.55 + (y - 2_280_000.0) / 110_540.0
    lon = -104.05 + (x - 500_000.0) / 95_000.0
    return lon, lat


_singleton: GeeService | None = None


def get_gee_service() -> GeeService:
    """Singleton de proceso (safe: no lanza si degradado)."""
    global _singleton
    if _singleton is None:
        _singleton = GeeService(auto_init=True)
    return _singleton
