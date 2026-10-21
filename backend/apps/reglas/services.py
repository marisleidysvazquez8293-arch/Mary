"""
ReglasEngineService — exclusion masks and NOM-083 spatial rules (PASO 3).

Core API is numpy-oriented so unit tests run without PostGIS/GEE.
Optional GIS backends (shapely / geopandas / rasterio / GEE) are hooked via
clear stubs for PASO 4+ wiring.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

# IDs Tabla 4.1 (tesis): agua/pozos están en bloque ecológico
WATER_IDS = frozenset({"ECO_01"})
WELLS_IDS = frozenset({"ECO_02"})
AERODROME_IDS = frozenset({"SOC_01"})
URBAN_IDS = frozenset({"SOC_02"})
DEFAULT_BUFFER_M = 500.0
DEFAULT_AERODROME_WARNING_M = 13_000.0


@dataclass(frozen=True)
class RestrictionLayer:
    """One active restriction contributing to the exclusion product ∏ c_j."""

    id_criterio: str
    tipo_restriccion: str  # normativa | modelo | advertencia
    mask: np.ndarray  # bool or {0,1}; True/1 = allowed, False/0 = excluded
    parametros: Mapping[str, Any] = field(default_factory=dict)
    hard_exclude: bool = True  # False for advertencia unless configured


@dataclass
class WarningZone:
    id_criterio: str
    radius_m: float
    message: str
    cell_mask: np.ndarray | None = None  # True where warning applies


@dataclass
class ExclusionResult:
    """Conjunction mask and metadata."""

    exclusion_mask: np.ndarray  # True = allowed (passes all hard restrictions)
    product: np.ndarray  # float ∏ c_j in {0,1} (or continuous if soft)
    warnings: list[WarningZone] = field(default_factory=list)
    applied_criteria: list[str] = field(default_factory=list)
    buffers_applied_m: dict[str, float] = field(default_factory=dict)


class ReglasEngineService:
    """
    Build exclusion / warning surfaces from active rules.

    Exclusion: M = ∏ c_j over hard (normativa/modelo) restrictions where
    c_j ∈ {0,1}. Advertencias (e.g. aerodrome <13 km) are collected as
    warnings unless parametros_json.hard_exclude is True.
    """

    def __init__(self, default_srid: int = 32613):
        self.default_srid = default_srid

    # ------------------------------------------------------------------
    # Parameter helpers (from Regla.parametros_json)
    # ------------------------------------------------------------------

    @staticmethod
    def buffer_meters(parametros: Mapping[str, Any] | None, default: float = DEFAULT_BUFFER_M) -> float:
        if not parametros:
            return default
        if "buffer_m" in parametros:
            return float(parametros["buffer_m"])
        return default

    @staticmethod
    def aerodrome_warning_radius_m(parametros: Mapping[str, Any] | None) -> float:
        if not parametros:
            return DEFAULT_AERODROME_WARNING_M
        if "warning_radius_m" in parametros:
            return float(parametros["warning_radius_m"])
        return DEFAULT_AERODROME_WARNING_M

    @staticmethod
    def is_hard_exclusion(tipo_restriccion: str, parametros: Mapping[str, Any] | None) -> bool:
        """Advertencia is soft unless parametros.hard_exclude is set."""
        params = parametros or {}
        if "hard_exclude" in params:
            return bool(params["hard_exclude"])
        return tipo_restriccion != "advertencia"

    # ------------------------------------------------------------------
    # Core conjunction
    # ------------------------------------------------------------------

    def build_exclusion_mask(
        self,
        layers: Sequence[RestrictionLayer],
        *,
        shape: tuple[int, int] | None = None,
    ) -> ExclusionResult:
        """
        Conjunction of active hard restrictions: product ∏ c_j.

        Soft layers (advertencia) contribute to ``warnings`` only.
        """
        if not layers:
            if shape is None:
                raise ValueError("shape required when layers is empty")
            ones = np.ones(shape, dtype=bool)
            return ExclusionResult(
                exclusion_mask=ones,
                product=ones.astype(float),
            )

        ref = np.asarray(layers[0].mask)
        if shape is None:
            shape = ref.shape
        product = np.ones(shape, dtype=float)
        warnings: list[WarningZone] = []
        applied: list[str] = []
        buffers: dict[str, float] = {}

        for layer in layers:
            mask = np.asarray(layer.mask, dtype=float)
            if mask.shape != shape:
                raise ValueError(
                    f"Shape mismatch for {layer.id_criterio}: {mask.shape} != {shape}"
                )
            # Normalize to {0,1}
            c_j = (mask > 0).astype(float)
            hard = layer.hard_exclude and self.is_hard_exclusion(
                layer.tipo_restriccion, layer.parametros
            )
            applied.append(layer.id_criterio)

            buf = self.buffer_meters(layer.parametros, default=0.0)
            if buf > 0 and layer.id_criterio in (WATER_IDS | WELLS_IDS | URBAN_IDS):
                buffers[layer.id_criterio] = buf
            elif "buffer_m" in (layer.parametros or {}):
                buffers[layer.id_criterio] = float(layer.parametros["buffer_m"])

            if hard:
                product *= c_j
            else:
                # Soft: warning where restriction fails (c_j == 0)
                warn_mask = c_j < 0.5
                radius = self.aerodrome_warning_radius_m(layer.parametros)
                if layer.id_criterio in AERODROME_IDS:
                    msg = (
                        f"Aeródromo/aeropuerto a <{radius/1000:.0f} km: "
                        "requiere estudio de riesgo aviario (NOM-083 §6.1.1)."
                    )
                else:
                    msg = f"Advertencia activa para {layer.id_criterio}."
                warnings.append(
                    WarningZone(
                        id_criterio=layer.id_criterio,
                        radius_m=radius if layer.id_criterio in AERODROME_IDS else buf,
                        message=msg,
                        cell_mask=warn_mask,
                    )
                )

        exclusion_mask = product > 0.5
        return ExclusionResult(
            exclusion_mask=exclusion_mask,
            product=product,
            warnings=warnings,
            applied_criteria=applied,
            buffers_applied_m=buffers,
        )

    def apply_distance_buffer_mask(
        self,
        distance_raster_m: np.ndarray,
        buffer_m: float,
    ) -> np.ndarray:
        """
        Binary allowance from a distance-to-feature raster.

        Cells with distance >= buffer_m are allowed (True / 1).
        Typical use: water (GEO_01) and wells (GEO_02) with buffer_m=500.
        """
        dist = np.asarray(distance_raster_m, dtype=float)
        return dist >= float(buffer_m)

    def build_layers_from_distance_rasters(
        self,
        specs: Iterable[Mapping[str, Any]],
    ) -> list[RestrictionLayer]:
        """
        Build RestrictionLayer list from distance rasters + rule metadata.

        Each spec keys:
          id_criterio, tipo_restriccion, distance_m (ndarray),
          parametros (dict, optional), hard_exclude (optional bool)
        """
        layers: list[RestrictionLayer] = []
        for spec in specs:
            params = dict(spec.get("parametros") or {})
            buffer_m = self.buffer_meters(params, default=DEFAULT_BUFFER_M)
            # Aerodrome: warning radius, not hard 500 m buffer
            if spec["id_criterio"] in AERODROME_IDS:
                radius = self.aerodrome_warning_radius_m(params)
                # Allowed outside radius; inside = warning zone (c_j=0 inside)
                mask = np.asarray(spec["distance_m"], dtype=float) >= radius
                params.setdefault("warning_radius_m", radius)
            else:
                mask = self.apply_distance_buffer_mask(spec["distance_m"], buffer_m)
                params.setdefault("buffer_m", buffer_m)

            tipo = spec.get("tipo_restriccion", "normativa")
            hard = spec.get("hard_exclude")
            if hard is None:
                hard = self.is_hard_exclusion(tipo, params)

            layers.append(
                RestrictionLayer(
                    id_criterio=spec["id_criterio"],
                    tipo_restriccion=tipo,
                    mask=mask,
                    parametros=params,
                    hard_exclude=hard,
                )
            )
        return layers

    # ------------------------------------------------------------------
    # GIS / GEE hooks (stubs)
    # ------------------------------------------------------------------

    def buffer_geometries_stub(
        self,
        geometries: Any,
        distance_m: float,
        *,
        srid: int | None = None,
    ) -> Any:
        """
        TODO: buffer vector features with shapely/geopandas in EPSG:32613.

        Expected: GeoSeries/list of shapely geometries → buffered polygons.
        Requires optional deps: shapely, geopandas.
        """
        raise NotImplementedError(
            "buffer_geometries_stub: install shapely/geopandas and rasterize "
            f"buffers ({distance_m} m, srid={srid or self.default_srid})."
        )

    def rasterize_mask_stub(
        self,
        geometries: Any,
        transform: Any,
        shape: tuple[int, int],
    ) -> np.ndarray:
        """TODO: rasterio.features.rasterize → bool mask."""
        raise NotImplementedError(
            "rasterize_mask_stub: requires rasterio for vector→raster masks."
        )

    def gee_exclusion_hook_stub(self, asset_ids: Sequence[str], region: Any) -> np.ndarray:
        """
        TODO / GEE hook: compute exclusion product on Google Earth Engine.

        Keep local numpy path for CI; swap to ee.Image operations in production.
        """
        raise NotImplementedError(
            f"gee_exclusion_hook_stub: not configured (assets={list(asset_ids)})."
        )

    # ------------------------------------------------------------------
    # ORM convenience (optional; requires Django DB)
    # ------------------------------------------------------------------

    def active_rule_params_from_orm(self, version: str = "1.0.0") -> list[dict[str, Any]]:
        """Load active Criterio + Regla parametros for the given version."""
        from apps.reglas.models import Criterio

        out: list[dict[str, Any]] = []
        qs = Criterio.objects.filter(activo=True).prefetch_related("reglas")
        for crit in qs:
            regla = crit.reglas.filter(version=version).first()
            if regla is None:
                regla = crit.reglas.order_by("-version").first()
            out.append(
                {
                    "id_criterio": crit.id_criterio,
                    "tipo_restriccion": crit.tipo_restriccion,
                    "bloque": crit.bloque,
                    "parametros": dict(regla.parametros_json) if regla else {},
                    "version": regla.version if regla else None,
                }
            )
        return out
