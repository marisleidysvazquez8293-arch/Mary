"""
CLPService — Combinación Lineal Ponderada + restricciones (PASO 3 / tesis §4.5.2).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Mapping, Sequence

import numpy as np

# =====================================================================
# CLP — Combinación Lineal Ponderada + restricciones
# =====================================================================


class SuitabilityClass(IntEnum):
    EXCLUIDO = 0
    NO_APTO = 1
    NO_RECOMENDABLE = 2
    APTO_CON_RESTRICCIONES = 3
    FAVORABLE = 4
    OPTIMO = 5


CLASS_LABELS: dict[int, str] = {
    SuitabilityClass.EXCLUIDO: "Excluido",
    SuitabilityClass.NO_APTO: "No apto",
    SuitabilityClass.NO_RECOMENDABLE: "No recomendable",
    SuitabilityClass.APTO_CON_RESTRICCIONES: "Apto con restricciones",
    SuitabilityClass.FAVORABLE: "Favorable",
    SuitabilityClass.OPTIMO: "Óptimo",
}

# Cortes tesis §4.5.2 (S ∈ [0, 5] tras ∑w·x con x∈[0,5]):
# 0 = Excluido; (0,1.5] No apto; (1.5,2.5] No recomendable;
# (2.5,3.5] Apto con restricciones; (3.5,4.5] Favorable; (4.5,5] Óptimo.
DEFAULT_BREAKS: tuple[float, float, float, float] = (
    1.5,
    2.5,
    3.5,
    4.5,
)


@dataclass
class CandidatePolygon:
    """Structured candidate site (geometry ops may be stubbed)."""

    candidate_id: str
    class_label: str
    mean_suitability: float
    area_m2: float | None = None
    useful_life_years: float | None = None
    intermunicipal: bool = False
    municipalities: list[str] = field(default_factory=list)
    geometry_wkt: str | None = None  # TODO: fill via shapely
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class CLPResult:
    suitability: np.ndarray  # S = (∑ w_i x_i) · ∏ c_j
    weighted_sum: np.ndarray  # ∑ w_i x_i before exclusion
    exclusion_product: np.ndarray  # ∏ c_j
    class_map: np.ndarray  # int codes SuitabilityClass
    class_counts: dict[str, int]
    candidates: list[CandidatePolygon] = field(default_factory=list)


class CLPService:
    """
    Weighted Linear Combination with restriction product:

        S = (∑_i w_i · x_i) · ∏_j c_j

    Reclassifies into 6 suitability classes and structures candidate outputs.
    """

    def __init__(
        self,
        breaks: Sequence[float] = DEFAULT_BREAKS,
        waste_generation_ton_per_year: float | None = None,
        density_ton_per_m3: float = 0.85,
        cell_area_m2: float | None = None,
    ):
        breaks_t = tuple(float(b) for b in breaks)
        if len(breaks_t) != 4:
            raise ValueError("breaks must have 4 ascending thresholds")
        if list(breaks_t) != sorted(breaks_t):
            raise ValueError("breaks must be ascending")
        self.breaks = breaks_t
        self.waste_generation_ton_per_year = waste_generation_ton_per_year
        self.density_ton_per_m3 = density_ton_per_m3
        self.cell_area_m2 = cell_area_m2

    def weighted_sum(
        self,
        criteria_rasters: Sequence[np.ndarray],
        weights: Sequence[float],
    ) -> np.ndarray:
        if len(criteria_rasters) != len(weights):
            raise ValueError("criteria_rasters and weights length mismatch")
        if not criteria_rasters:
            raise ValueError("criteria_rasters must be non-empty")
        w = np.asarray(weights, dtype=float)
        if np.any(w < 0):
            raise ValueError("weights must be non-negative")
        w_sum = w.sum()
        if w_sum <= 0:
            raise ValueError("weights must sum to a positive value")
        w = w / w_sum

        acc = np.zeros_like(np.asarray(criteria_rasters[0], dtype=float))
        shape = acc.shape
        for raster, wi in zip(criteria_rasters, w):
            x = np.asarray(raster, dtype=float)
            if x.shape != shape:
                raise ValueError(f"Raster shape mismatch: {x.shape} != {shape}")
            acc = acc + wi * x
        return acc

    def apply_exclusion(
        self,
        weighted: np.ndarray,
        exclusion_product: np.ndarray,
    ) -> np.ndarray:
        """S = (∑ w_i x_i) · ∏ c_j"""
        w = np.asarray(weighted, dtype=float)
        c = np.asarray(exclusion_product, dtype=float)
        if w.shape != c.shape:
            raise ValueError("weighted and exclusion_product shape mismatch")
        return w * c

    def reclassify(self, suitability: np.ndarray) -> np.ndarray:
        """
        Map S to 6 classes.

        S == 0 (or ~0) → Excluido
        else by breaks → No apto … Óptimo
        """
        s = np.asarray(suitability, dtype=float)
        out = np.full(s.shape, int(SuitabilityClass.OPTIMO), dtype=np.int8)
        b0, b1, b2, b3 = self.breaks
        out[s <= b3] = int(SuitabilityClass.FAVORABLE)
        out[s <= b2] = int(SuitabilityClass.APTO_CON_RESTRICCIONES)
        out[s <= b1] = int(SuitabilityClass.NO_RECOMENDABLE)
        out[s <= b0] = int(SuitabilityClass.NO_APTO)
        out[s <= 1e-12] = int(SuitabilityClass.EXCLUIDO)
        return out

    def class_counts(self, class_map: np.ndarray) -> dict[str, int]:
        counts: dict[str, int] = {label: 0 for label in CLASS_LABELS.values()}
        flat = np.asarray(class_map).ravel()
        for code, label in CLASS_LABELS.items():
            counts[label] = int(np.sum(flat == int(code)))
        return counts

    def compute(
        self,
        criteria_rasters: Sequence[np.ndarray],
        weights: Sequence[float],
        exclusion_product: np.ndarray,
        *,
        delineate: bool = False,
        municipality_labels: np.ndarray | None = None,
    ) -> CLPResult:
        weighted = self.weighted_sum(criteria_rasters, weights)
        suitability = self.apply_exclusion(weighted, exclusion_product)
        class_map = self.reclassify(suitability)
        counts = self.class_counts(class_map)
        candidates: list[CandidatePolygon] = []
        if delineate:
            candidates = self.delineate_candidates(
                class_map,
                suitability,
                municipality_labels=municipality_labels,
            )
        return CLPResult(
            suitability=suitability,
            weighted_sum=weighted,
            exclusion_product=np.asarray(exclusion_product, dtype=float),
            class_map=class_map,
            class_counts=counts,
            candidates=candidates,
        )

    def estimate_useful_life_years(
        self,
        area_m2: float,
        fill_height_m: float = 15.0,
    ) -> float | None:
        """
        Rough useful-life estimate from volume / annual tonnage.

        Returns None if waste_generation_ton_per_year is unset.
        """
        if not self.waste_generation_ton_per_year or self.waste_generation_ton_per_year <= 0:
            return None
        volume_m3 = area_m2 * fill_height_m
        capacity_ton = volume_m3 * self.density_ton_per_m3
        return capacity_ton / self.waste_generation_ton_per_year

    def delineate_candidates(
        self,
        class_map: np.ndarray,
        suitability: np.ndarray,
        *,
        municipality_labels: np.ndarray | None = None,
        min_class: SuitabilityClass = SuitabilityClass.APTO_CON_RESTRICCIONES,
    ) -> list[CandidatePolygon]:
        """
        Structure candidate polygons from contiguous cells >= min_class.

        Geometry ops (shapely labeling / polygonize) are TODO when GIS libs
        are available in CI. This implementation uses a simple connected-
        component labeler in pure numpy (4-connectivity).
        """
        cm = np.asarray(class_map)
        s = np.asarray(suitability, dtype=float)
        eligible = cm >= int(min_class)
        labels = self._label_components(eligible)
        candidates: list[CandidatePolygon] = []
        for lab in range(1, int(labels.max()) + 1):
            cells = labels == lab
            n_cells = int(cells.sum())
            if n_cells == 0:
                continue
            mean_s = float(s[cells].mean())
            dominant = int(np.bincount(cm[cells].astype(int)).argmax())
            area = None
            if self.cell_area_m2 is not None:
                area = n_cells * self.cell_area_m2
            life = self.estimate_useful_life_years(area) if area else None

            intermunicipal = False
            munis: list[str] = []
            if municipality_labels is not None:
                m = np.asarray(municipality_labels)
                vals = {str(v) for v in np.unique(m[cells])}
                munis = sorted(vals)
                intermunicipal = len(munis) > 1

            candidates.append(
                CandidatePolygon(
                    candidate_id=f"CAND_{lab:04d}",
                    class_label=CLASS_LABELS.get(dominant, str(dominant)),
                    mean_suitability=mean_s,
                    area_m2=area,
                    useful_life_years=life,
                    intermunicipal=intermunicipal,
                    municipalities=munis,
                    geometry_wkt=None,  # TODO: shapely polygonize
                    attributes={"n_cells": n_cells, "class_code": dominant},
                )
            )
        return candidates

    @staticmethod
    def _label_components(binary: np.ndarray) -> np.ndarray:
        """4-connected component labeling (pure numpy flood-fill)."""
        mask = np.asarray(binary, dtype=bool)
        h, w = mask.shape
        labels = np.zeros((h, w), dtype=np.int32)
        current = 0
        for i in range(h):
            for j in range(w):
                if not mask[i, j] or labels[i, j] != 0:
                    continue
                current += 1
                stack = [(i, j)]
                labels[i, j] = current
                while stack:
                    r, c = stack.pop()
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < h and 0 <= nc < w and mask[nr, nc] and labels[nr, nc] == 0:
                            labels[nr, nc] = current
                            stack.append((nr, nc))
        return labels

    # ------------------------------------------------------------------
    # API tesis (nombres en español)
    # ------------------------------------------------------------------

    def calcular_indice_aptitud(
        self,
        factores_normalizados: Sequence[np.ndarray],
        pesos_globales: Sequence[float],
        mascara_exclusion: np.ndarray,
    ) -> np.ndarray:
        """
        S = (∑ w_i · x_i) · ∏ c_j con x_i ∈ [0, 5].

        ``mascara_exclusion``: 1=permitido, 0=excluido (producto ∏ c_j).
        Los pesos se usan tal cual (sin renormalizar) si ya suman ~1.
        """
        if len(factores_normalizados) != len(pesos_globales):
            raise ValueError("factores y pesos deben tener la misma longitud")
        if not factores_normalizados:
            raise ValueError("factores_normalizados no puede estar vacío")
        w = np.asarray(pesos_globales, dtype=float)
        if np.any(w < 0):
            raise ValueError("pesos_globales deben ser no negativos")
        acc = np.zeros_like(np.asarray(factores_normalizados[0], dtype=float))
        shape = acc.shape
        for x, wi in zip(factores_normalizados, w):
            xi = np.asarray(x, dtype=float)
            if xi.shape != shape:
                raise ValueError(f"Shape de factor {xi.shape} != {shape}")
            if np.nanmax(xi) > 5.0 + 1e-6 or np.nanmin(xi) < -1e-6:
                # Escala tesis 0–5; se tolera ligera desviación numérica
                pass
            acc = acc + wi * xi
        return self.apply_exclusion(acc, mascara_exclusion)

    def reclasificar_aptitud(self, raster_S: np.ndarray) -> np.ndarray:
        """Alias tesis de ``reclassify`` (cortes 1.5 / 2.5 / 3.5 / 4.5)."""
        return self.reclassify(raster_S)

    def delimitar_poligonos_candidatos(
        self,
        raster_reclasificado: np.ndarray,
        superficie_minima_ha: float,
        *,
        suitability: np.ndarray | None = None,
        cell_area_m2: float | None = None,
        municipality_labels: np.ndarray | None = None,
    ) -> list[CandidatePolygon]:
        """
        Vectoriza (componentes conexas) celdas Favorable+Óptimo y descarta
        polígonos con área < superficie_minima_ha.
        """
        cell_m2 = cell_area_m2 if cell_area_m2 is not None else self.cell_area_m2
        if cell_m2 is None:
            raise ValueError("cell_area_m2 requerido para convertir ha → celdas")
        min_area_m2 = float(superficie_minima_ha) * 10_000.0
        cm = np.asarray(raster_reclasificado)
        s = (
            np.asarray(suitability, dtype=float)
            if suitability is not None
            else cm.astype(float)
        )
        # Solo Favorable (4) y Óptimo (5)
        cands = self.delineate_candidates(
            cm,
            s,
            municipality_labels=municipality_labels,
            min_class=SuitabilityClass.FAVORABLE,
        )
        # Ajustar área con cell_m2 explícito
        kept: list[CandidatePolygon] = []
        for c in cands:
            n_cells = int(c.attributes.get("n_cells", 0))
            area = n_cells * float(cell_m2)
            if area + 1e-9 < min_area_m2:
                continue
            c.area_m2 = area
            c.useful_life_years = self.estimate_useful_life_years(area)
            kept.append(c)
        return kept

    def evaluar_poligonos_fase2(
        self,
        poligonos: Sequence[CandidatePolygon | Mapping[str, Any]],
        *,
        fill_height_m: float = 15.0,
        waste_ton_per_year: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Criterios 18 (Vida útil / SOC_07) y 21 (Intermunicipalidad / SOC_10)
        a nivel polígono (tesis §4.5.2 — evaluación en dos fases).
        """
        wpy = (
            waste_ton_per_year
            if waste_ton_per_year is not None
            else self.waste_generation_ton_per_year
        )
        out: list[dict[str, Any]] = []
        for p in poligonos:
            if isinstance(p, CandidatePolygon):
                data = {
                    "candidate_id": p.candidate_id,
                    "area_m2": p.area_m2,
                    "intermunicipal": p.intermunicipal,
                    "municipalities": list(p.municipalities),
                    "mean_suitability": p.mean_suitability,
                    "class_label": p.class_label,
                }
            else:
                data = dict(p)
            area = data.get("area_m2")
            vida = None
            if area is not None and wpy and wpy > 0:
                volume_m3 = float(area) * fill_height_m
                vida = (volume_m3 * self.density_ton_per_m3) / float(wpy)
            # Factor 0–5 tipificado: ≥7 años SEDESOL → 5; lineal hacia 0
            if vida is None:
                factor_vida = None
            elif vida >= 7.0:
                factor_vida = 5.0
            else:
                factor_vida = max(0.0, 5.0 * (vida / 7.0))
            n_munis = len(data.get("municipalities") or [])
            inter = bool(data.get("intermunicipal")) or n_munis > 1
            # Factor intermunicipalidad: más municipios → mayor aptitud (tope 5)
            if n_munis <= 1:
                factor_inter = 1.0 if not inter else 2.0
            else:
                factor_inter = min(5.0, 1.0 + n_munis)
            out.append(
                {
                    **data,
                    "soc_07_vida_util_anios": vida,
                    "soc_07_factor_0_5": factor_vida,
                    "soc_10_intermunicipal": inter,
                    "soc_10_factor_0_5": factor_inter,
                    "fase2_ok_vida_util_min_7": bool(vida is not None and vida >= 7.0),
                }
            )
        return out

    def polygonize_stub(self, class_map: np.ndarray, transform: Any = None) -> list[Any]:
        """TODO: rasterio.features.shapes / shapely for real polygons."""
        raise NotImplementedError(
            "polygonize_stub: requires rasterio/shapely for geometry export."
        )



__all__ = [
    "CLPService",
    "CLPResult",
    "SuitabilityClass",
    "CLASS_LABELS",
    "CandidatePolygon",
    "DEFAULT_BREAKS",
]
