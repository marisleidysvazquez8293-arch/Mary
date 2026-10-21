"""
Scenario execution, repeatability, and sensitivity E0–E8 (PASO 4).

Uses ReglasEngineService + CLPService. Spatial inputs may be:
  - provided in parametros_ejecucion["criteria_rasters"] / ["distance_rasters"]
  - or synthetic deterministic grids from parametros_ejecucion["demo_seed"]
    (default) so CI/API tests need no PostGIS/GEE.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

import numpy as np
from django.db import transaction
from django.utils import timezone as dj_timezone

from apps.escenarios.hashing import hash_configuracion, hash_resultado
from apps.escenarios.models import Escenario
from apps.multicriterio.models import ConjuntoPesosAHP, PesoCriterio
from apps.multicriterio.services import (
    CLASS_LABELS,
    CLPService,
    SuitabilityClass,
)
from apps.reglas.services import ReglasEngineService  # alias de RulesEngineService

# Sensitivity experiment labels E0 (baseline) … E8
SENSITIVITY_IDS = tuple(f"E{i}" for i in range(9))


@dataclass
class ExecutionOutput:
    escenario: Escenario
    created: bool
    class_map: list[list[int]]
    suitability: list[list[float]]


@dataclass
class ReexecuteOutput:
    escenario: Escenario
    hash_configuracion: str
    hash_resultado_anterior: str
    hash_resultado_nuevo: str
    config_unchanged: bool
    resultado_reproducido: bool


@dataclass
class SensitivityPair:
    scenario_a: str
    scenario_b: str
    jaccard: float
    intersection_cells: int
    union_cells: int


@dataclass
class SensitivityReport:
    baseline_id: str
    experiments: list[dict[str, Any]]
    pairwise_jaccard: list[SensitivityPair]
    notes: str = (
        "E0 = baseline weights; E1–E8 = ± perturbations of block/criterion weights. "
        "Jaccard computed on cells with class >= Apto con restricciones."
    )


def _now():
    return dj_timezone.now()


def _as_float_grid(data: Any) -> np.ndarray:
    arr = np.asarray(data, dtype=float)
    if arr.ndim != 2:
        raise ValueError("Raster must be 2-D")
    return arr


class EscenarioExecutionService:
    """Run ReglasEngine + CLP and persist Escenario with audit hashes."""

    def __init__(
        self,
        reglas_engine: ReglasEngineService | None = None,
        clp: CLPService | None = None,
    ):
        self.reglas = reglas_engine or ReglasEngineService()
        self.clp = clp or CLPService(cell_area_m2=100.0)

    # ------------------------------------------------------------------
    # Synthetic / input rasters
    # ------------------------------------------------------------------

    def build_demo_inputs(
        self,
        *,
        shape: tuple[int, int] = (8, 8),
        seed: int = 42,
        n_criteria: int = 3,
    ) -> tuple[list[np.ndarray], list[dict[str, Any]]]:
        """Deterministic criteria + distance rasters for repeatable demos/tests."""
        rng = np.random.default_rng(seed)
        h, w = shape
        criteria = [rng.random((h, w)) for _ in range(n_criteria)]
        # Distance-like fields (metres) for water / wells / aerodrome
        yy, xx = np.mgrid[0:h, 0:w]
        dist_water = np.hypot(yy - 1, xx - 1) * 200.0  # ~0–2 km scale
        dist_wells = np.hypot(yy - h + 2, xx - w + 2) * 200.0
        dist_aero = np.hypot(yy - h / 2, xx - w / 2) * 3000.0
        distance_specs = [
            {
                "id_criterio": "ECO_01",
                "tipo_restriccion": "normativa",
                "distance_m": dist_water,
                "parametros": {"buffer_m": 500},
            },
            {
                "id_criterio": "ECO_02",
                "tipo_restriccion": "normativa",
                "distance_m": dist_wells,
                "parametros": {"buffer_m": 500},
            },
            {
                "id_criterio": "SOC_01",
                "tipo_restriccion": "advertencia",
                "distance_m": dist_aero,
                "parametros": {"warning_radius_m": 13_000},
            },
        ]
        return criteria, distance_specs

    def _resolve_inputs(
        self, parametros: Mapping[str, Any]
    ) -> tuple[list[np.ndarray], list[dict[str, Any]], list[float]]:
        params = dict(parametros or {})
        weights = params.get("weights")
        if params.get("criteria_rasters"):
            criteria = [_as_float_grid(r) for r in params["criteria_rasters"]]
        else:
            shape = tuple(params.get("shape", (8, 8)))
            seed = int(params.get("demo_seed", 42))
            n_crit = int(params.get("n_criteria", 3))
            criteria, _ = self.build_demo_inputs(
                shape=shape, seed=seed, n_criteria=n_crit
            )

        if params.get("distance_rasters"):
            distance_specs = params["distance_rasters"]
        else:
            shape = criteria[0].shape
            seed = int(params.get("demo_seed", 42))
            _, distance_specs = self.build_demo_inputs(
                shape=shape, seed=seed, n_criteria=len(criteria)
            )

        if weights is None:
            weights = [1.0 / len(criteria)] * len(criteria)
        weights = [float(w) for w in weights]
        if len(weights) != len(criteria):
            raise ValueError("weights length must match criteria_rasters")
        return criteria, distance_specs, weights

    def weights_from_conjunto(self, conjunto: ConjuntoPesosAHP, n: int) -> list[float]:
        pesos = list(
            PesoCriterio.objects.filter(conjunto=conjunto).order_by("id")
        )
        if not pesos:
            return [1.0 / n] * n
        globals_ = [float(p.peso_global) for p in pesos[:n]]
        if len(globals_) < n:
            # pad with equal share of remainder
            rem = n - len(globals_)
            pad = (1.0 - sum(globals_)) / rem if rem else 0.0
            globals_.extend([pad] * rem)
        s = sum(globals_) or 1.0
        return [g / s for g in globals_[:n]]

    def run_engine(
        self,
        parametros: Mapping[str, Any],
        *,
        weights_override: Sequence[float] | None = None,
    ) -> dict[str, Any]:
        """Execute spatial pipeline; return serializable resultados_json + maps."""
        criteria, distance_specs, weights = self._resolve_inputs(parametros)
        if weights_override is not None:
            weights = [float(w) for w in weights_override]
            if len(weights) != len(criteria):
                raise ValueError("weights_override length mismatch")

        layers = self.reglas.build_layers_from_distance_rasters(distance_specs)
        exclusion = self.reglas.build_exclusion_mask(layers)
        clp_result = self.clp.compute(
            criteria,
            weights,
            exclusion.product,
            delineate=True,
        )

        candidates = [
            {
                "candidate_id": c.candidate_id,
                "class_label": c.class_label,
                "mean_suitability": c.mean_suitability,
                "area_m2": c.area_m2,
                "useful_life_years": c.useful_life_years,
                "intermunicipal": c.intermunicipal,
                "municipalities": c.municipalities,
                "geometry_wkt": c.geometry_wkt,
                "attributes": c.attributes,
            }
            for c in clp_result.candidates
        ]

        # Compact GeoJSON-ready features from class cells (point centroids stub)
        features = self._class_map_to_geojson_features(
            clp_result.class_map, clp_result.suitability
        )

        resultados = {
            "class_counts": clp_result.class_counts,
            "class_map": clp_result.class_map.astype(int).tolist(),
            "suitability": np.round(clp_result.suitability, 6).tolist(),
            "exclusion_product": exclusion.product.astype(float).tolist(),
            "warnings": [
                {
                    "id_criterio": w.id_criterio,
                    "radius_m": w.radius_m,
                    "message": w.message,
                }
                for w in exclusion.warnings
            ],
            "buffers_applied_m": exclusion.buffers_applied_m,
            "applied_criteria": exclusion.applied_criteria,
            "weights_used": weights,
            "candidates": candidates,
            "geojson": {
                "type": "FeatureCollection",
                "features": features,
            },
            "class_labels": dict(CLASS_LABELS),
        }
        return resultados

    @staticmethod
    def _class_map_to_geojson_features(
        class_map: np.ndarray,
        suitability: np.ndarray,
        *,
        cell_size_m: float = 100.0,
        origin_x: float = 500_000.0,
        origin_y: float = 2_300_000.0,
    ) -> list[dict[str, Any]]:
        """
        Emit one Polygon feature per cell (EPSG:32613-ish synthetic grid).

        Full dissolve/polygonize is TODO (rasterio/shapely); cell polygons are
        enough for v1 map preview.
        """
        cm = np.asarray(class_map)
        s = np.asarray(suitability, dtype=float)
        h, w = cm.shape
        features: list[dict[str, Any]] = []
        for i in range(h):
            for j in range(w):
                code = int(cm[i, j])
                x0 = origin_x + j * cell_size_m
                y0 = origin_y + (h - 1 - i) * cell_size_m
                ring = [
                    [x0, y0],
                    [x0 + cell_size_m, y0],
                    [x0 + cell_size_m, y0 + cell_size_m],
                    [x0, y0 + cell_size_m],
                    [x0, y0],
                ]
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": [ring]},
                        "properties": {
                            "class_code": code,
                            "class_label": CLASS_LABELS.get(code, str(code)),
                            "suitability": float(s[i, j]),
                            "row": i,
                            "col": j,
                        },
                    }
                )
        return features

    # ------------------------------------------------------------------
    # Persist / re-execute
    # ------------------------------------------------------------------

    @transaction.atomic
    def execute(
        self,
        *,
        nombre: str,
        version_reglas_usada: str,
        conjunto_pesos: ConjuntoPesosAHP,
        parametros_ejecucion: Mapping[str, Any] | None = None,
        weights_from_db: bool = True,
    ) -> ExecutionOutput:
        params = dict(parametros_ejecucion or {})
        params.setdefault("demo_seed", 42)
        params.setdefault("shape", [8, 8])

        # Resolve weights into params for hash stability
        criteria_preview, _, default_w = self._resolve_inputs(params)
        if weights_from_db and "weights" not in params:
            params["weights"] = self.weights_from_conjunto(
                conjunto_pesos, len(criteria_preview)
            )
        elif "weights" not in params:
            params["weights"] = default_w

        cfg_hash = hash_configuracion(
            version_reglas_usada=version_reglas_usada,
            conjunto_pesos_id=conjunto_pesos.pk,
            parametros_ejecucion=params,
        )

        existing = Escenario.objects.filter(hash_configuracion=cfg_hash).first()
        resultados = self.run_engine(params)
        res_hash = hash_resultado(resultados)

        if existing:
            existing.nombre = nombre
            existing.version_reglas_usada = version_reglas_usada
            existing.conjunto_pesos = conjunto_pesos
            existing.hash_resultado = res_hash
            existing.fecha_ejecucion = _now()
            existing.parametros_ejecucion = params
            existing.resultados_json = resultados
            existing.save()
            esc = existing
            created = False
        else:
            esc = Escenario.objects.create(
                nombre=nombre,
                version_reglas_usada=version_reglas_usada,
                conjunto_pesos=conjunto_pesos,
                hash_configuracion=cfg_hash,
                hash_resultado=res_hash,
                fecha_ejecucion=_now(),
                parametros_ejecucion=params,
                resultados_json=resultados,
            )
            created = True

        return ExecutionOutput(
            escenario=esc,
            created=created,
            class_map=resultados["class_map"],
            suitability=resultados["suitability"],
        )

    @transaction.atomic
    def reexecute(self, escenario: Escenario) -> ReexecuteOutput:
        """Re-run with stored config; compare resultado hashes for audit."""
        prev_res = escenario.hash_resultado
        cfg = hash_configuracion(
            version_reglas_usada=escenario.version_reglas_usada,
            conjunto_pesos_id=escenario.conjunto_pesos_id,
            parametros_ejecucion=escenario.parametros_ejecucion,
        )
        config_unchanged = cfg == escenario.hash_configuracion

        resultados = self.run_engine(escenario.parametros_ejecucion)
        new_res = hash_resultado(resultados)

        escenario.hash_resultado = new_res
        escenario.fecha_ejecucion = _now()
        escenario.resultados_json = resultados
        # Keep hash_configuracion stable (audit identity)
        escenario.save(
            update_fields=[
                "hash_resultado",
                "fecha_ejecucion",
                "resultados_json",
            ]
        )
        return ReexecuteOutput(
            escenario=escenario,
            hash_configuracion=escenario.hash_configuracion,
            hash_resultado_anterior=prev_res,
            hash_resultado_nuevo=new_res,
            config_unchanged=config_unchanged,
            resultado_reproducido=bool(prev_res) and prev_res == new_res,
        )

    # ------------------------------------------------------------------
    # Sensitivity E0–E8 + Jaccard
    # ------------------------------------------------------------------

    @staticmethod
    def jaccard_binary(a: np.ndarray, b: np.ndarray) -> tuple[float, int, int]:
        a_b = np.asarray(a, dtype=bool).ravel()
        b_b = np.asarray(b, dtype=bool).ravel()
        inter = int(np.logical_and(a_b, b_b).sum())
        union = int(np.logical_or(a_b, b_b).sum())
        if union == 0:
            return 1.0, 0, 0
        return inter / union, inter, union

    def _apto_mask(self, class_map: np.ndarray) -> np.ndarray:
        return np.asarray(class_map) >= int(SuitabilityClass.APTO_CON_RESTRICCIONES)

    def sensitivity_e0_e8(
        self,
        *,
        version_reglas_usada: str,
        conjunto_pesos: ConjuntoPesosAHP,
        parametros_ejecucion: Mapping[str, Any] | None = None,
        persist: bool = False,
    ) -> SensitivityReport:
        """
        E0 baseline; E1–E8 weight perturbations (±20% on cycling criteria,
        renormalized). Returns Jaccard pairwise vs E0 and among experiments.
        """
        base_params = dict(parametros_ejecucion or {})
        base_params.setdefault("demo_seed", 42)
        base_params.setdefault("shape", [8, 8])
        criteria, _, base_weights = self._resolve_inputs(base_params)
        if "weights" not in base_params:
            base_params["weights"] = self.weights_from_conjunto(
                conjunto_pesos, len(criteria)
            ) if conjunto_pesos.pesos.exists() else base_weights

        experiments: list[dict[str, Any]] = []
        masks: dict[str, np.ndarray] = {}

        for idx, eid in enumerate(SENSITIVITY_IDS):
            params = dict(base_params)
            w = np.array(params["weights"], dtype=float)
            if idx > 0:
                # Perturb criterion (idx-1) % n by ±20% alternating sign
                k = (idx - 1) % len(w)
                factor = 1.2 if idx % 2 == 1 else 0.8
                w = w.copy()
                w[k] *= factor
                w = w / w.sum()
                params["weights"] = w.tolist()
                params["sensitivity_id"] = eid
                params["perturbation"] = {"index": k, "factor": factor}

            resultados = self.run_engine(params)
            class_map = np.asarray(resultados["class_map"])
            masks[eid] = self._apto_mask(class_map)
            entry = {
                "id": eid,
                "weights": params["weights"],
                "class_counts": resultados["class_counts"],
                "hash_resultado": hash_resultado(resultados),
            }
            if persist:
                out = self.execute(
                    nombre=f"Sensibilidad {eid}",
                    version_reglas_usada=version_reglas_usada,
                    conjunto_pesos=conjunto_pesos,
                    parametros_ejecucion=params,
                    weights_from_db=False,
                )
                entry["escenario_id"] = out.escenario.pk
                entry["hash_configuracion"] = out.escenario.hash_configuracion
            experiments.append(entry)

        pairs: list[SensitivityPair] = []
        ids = list(masks.keys())
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                jac, inter, union = self.jaccard_binary(masks[a], masks[b])
                pairs.append(
                    SensitivityPair(
                        scenario_a=a,
                        scenario_b=b,
                        jaccard=round(jac, 6),
                        intersection_cells=inter,
                        union_cells=union,
                    )
                )

        return SensitivityReport(
            baseline_id="E0",
            experiments=experiments,
            pairwise_jaccard=pairs,
        )

    def tilejson_contract(self, escenario: Escenario, request_base: str = "") -> dict[str, Any]:
        """
        TileJSON-like stub contract for future XYZ/PMTiles stack.

        v1 points clients at the GeoJSON endpoint instead of real tiles.
        """
        base = request_base.rstrip("/")
        return {
            "tilejson": "3.0.0",
            "name": escenario.nombre,
            "description": (
                "SADE suitability classes — tiling stub. Use geojson URL until "
                "XYZ/COG tiles are provisioned."
            ),
            "version": "1.0.0",
            "attribution": "SADE Valles de Jalisco",
            "scheme": "xyz",
            "tiles": [
                f"{base}/api/escenarios/{escenario.pk}/tiles/{{z}}/{{x}}/{{y}}.png"
            ],
            "minzoom": 8,
            "maxzoom": 16,
            "bounds": [-104.5, 20.0, -103.5, 21.2],
            "center": [-104.0, 20.6, 10],
            "vector_layers": [],
            "sade": {
                "status": "stub",
                "geojson": f"{base}/api/escenarios/{escenario.pk}/geojson/",
                "hash_configuracion": escenario.hash_configuracion,
                "hash_resultado": escenario.hash_resultado,
                "crs_analysis": "EPSG:32613",
            },
        }
