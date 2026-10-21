"""
AHPService and CLPService — multicriteria engine (PASO 3).

Pure numpy core (no PostGIS required for unit tests).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Mapping, Sequence

import numpy as np

# Saaty Random Index (IA) for n = 1..15
SAATY_RI: dict[int, float] = {
    1: 0.0,
    2: 0.0,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
    11: 1.51,
    12: 1.48,
    13: 1.56,
    14: 1.57,
    15: 1.59,
}

DEFAULT_CR_THRESHOLD = 0.10


# =====================================================================
# AHP
# =====================================================================


@dataclass(frozen=True)
class AHPResult:
    weights: np.ndarray  # principal eigenvector, normalized ∑=1
    lambda_max: float
    consistency_index: float  # IC = (λmax - n) / (n - 1)
    random_index: float  # IA
    consistency_ratio: float  # CR = IC / IA
    is_consistent: bool
    n: int


class AHPService:
    """
    Analytic Hierarchy Process helpers.

    - Principal eigenvector (power iteration / numpy eig)
    - Consistency Ratio CR = IC / IA
    - AIJ group aggregation via geometric mean of reciprocal matrices
    """

    def __init__(self, cr_threshold: float = DEFAULT_CR_THRESHOLD):
        self.cr_threshold = cr_threshold

    @staticmethod
    def random_index(n: int) -> float:
        if n < 1:
            raise ValueError("n must be >= 1")
        if n in SAATY_RI:
            return SAATY_RI[n]
        # Extrapolate mildly beyond table
        return SAATY_RI[15]

    @staticmethod
    def validate_reciprocal(matrix: np.ndarray, tol: float = 1e-6) -> None:
        a = np.asarray(matrix, dtype=float)
        if a.ndim != 2 or a.shape[0] != a.shape[1]:
            raise ValueError("Pairwise matrix must be square")
        n = a.shape[0]
        if np.any(a <= 0):
            raise ValueError("Pairwise entries must be positive")
        for i in range(n):
            if abs(a[i, i] - 1.0) > tol:
                raise ValueError("Diagonal must be 1")
            for j in range(i + 1, n):
                if abs(a[i, j] * a[j, i] - 1.0) > tol * max(1.0, abs(a[i, j])):
                    raise ValueError(
                        f"Matrix not reciprocal at ({i},{j}): "
                        f"{a[i, j]} * {a[j, i]} != 1"
                    )

    def principal_eigenvector(self, matrix: np.ndarray) -> tuple[np.ndarray, float]:
        """
        Return (normalized principal eigenvector, λ_max).

        Uses numpy.linalg.eig and selects the eigenvalue with largest real part.
        """
        a = np.asarray(matrix, dtype=float)
        self.validate_reciprocal(a)
        eigenvalues, eigenvectors = np.linalg.eig(a)
        idx = int(np.argmax(np.real(eigenvalues)))
        lambda_max = float(np.real(eigenvalues[idx]))
        vec = np.real(eigenvectors[:, idx])
        if np.all(vec <= 0):
            vec = -vec
        if np.any(vec < 0):
            # Rare numerical artefact; fall back to row geometric-mean approx
            vec = self._row_geometric_mean_weights(a)
            lambda_max = float(np.dot(a @ vec, 1.0 / vec) / len(vec)) if np.all(vec > 0) else lambda_max
        weights = vec / vec.sum()
        return weights.astype(float), lambda_max

    @staticmethod
    def _row_geometric_mean_weights(matrix: np.ndarray) -> np.ndarray:
        gm = np.prod(matrix, axis=1) ** (1.0 / matrix.shape[0])
        return gm / gm.sum()

    def consistency_index(self, lambda_max: float, n: int) -> float:
        if n <= 1:
            return 0.0
        return (lambda_max - n) / (n - 1)

    def consistency_ratio(self, matrix: np.ndarray) -> AHPResult:
        weights, lambda_max = self.principal_eigenvector(matrix)
        n = matrix.shape[0]
        ic = self.consistency_index(lambda_max, n)
        ia = self.random_index(n)
        if ia == 0.0:
            cr = 0.0
        else:
            cr = ic / ia
        return AHPResult(
            weights=weights,
            lambda_max=lambda_max,
            consistency_index=ic,
            random_index=ia,
            consistency_ratio=cr,
            is_consistent=cr < self.cr_threshold,
            n=n,
        )

    def validate_cr(self, matrix: np.ndarray, threshold: float | None = None) -> AHPResult:
        """Compute AHP result and raise if CR >= threshold."""
        thr = self.cr_threshold if threshold is None else threshold
        result = self.consistency_ratio(matrix)
        # Re-evaluate with override threshold
        ok = result.consistency_ratio < thr
        result = AHPResult(
            weights=result.weights,
            lambda_max=result.lambda_max,
            consistency_index=result.consistency_index,
            random_index=result.random_index,
            consistency_ratio=result.consistency_ratio,
            is_consistent=ok,
            n=result.n,
        )
        if not ok:
            raise ValueError(
                f"CR={result.consistency_ratio:.4f} >= threshold {thr} "
                f"(IC={result.consistency_index:.4f}, IA={result.random_index})"
            )
        return result

    def aggregate_aij(
        self,
        matrices: Sequence[np.ndarray],
    ) -> np.ndarray:
        """
        AIJ aggregation: element-wise geometric mean of reciprocal pairwise
        matrices from multiple experts, then re-normalize reciprocity.
        """
        if not matrices:
            raise ValueError("matrices must be non-empty")
        stack = np.array([np.asarray(m, dtype=float) for m in matrices])
        n = stack.shape[1]
        for m in stack:
            if m.shape != (n, n):
                raise ValueError("All matrices must share the same shape")
            self.validate_reciprocal(m)

        # Geometric mean of upper triangle; mirror reciprocal
        geo = np.prod(stack, axis=0) ** (1.0 / stack.shape[0])
        out = np.ones((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                out[i, j] = geo[i, j]
                out[j, i] = 1.0 / geo[i, j]
        self.validate_reciprocal(out)
        return out

    def weights_from_pairwise(self, matrix: np.ndarray) -> AHPResult:
        """Alias: eigenvector + CR in one call (no raise)."""
        return self.consistency_ratio(matrix)


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

# Default breakpoints on S ∈ (0, 1] after applying ∏ c_j.
# Excluido is forced when S ≈ 0 (exclusion product). Four cuts → five bands
# plus Excluido = 6 classes.
DEFAULT_BREAKS: tuple[float, float, float, float] = (
    0.20,  # (0, b0] → No apto
    0.40,  # (b0, b1] → No recomendable
    0.60,  # (b1, b2] → Apto con restricciones
    0.80,  # (b2, b3] → Favorable; (b3, 1] → Óptimo
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

    def polygonize_stub(self, class_map: np.ndarray, transform: Any = None) -> list[Any]:
        """TODO: rasterio.features.shapes / shapely for real polygons."""
        raise NotImplementedError(
            "polygonize_stub: requires rasterio/shapely for geometry export."
        )


# Re-export convenience
__all__ = [
    "AHPService",
    "AHPResult",
    "CLPService",
    "CLPResult",
    "SuitabilityClass",
    "CLASS_LABELS",
    "CandidatePolygon",
    "DEFAULT_CR_THRESHOLD",
    "DEFAULT_BREAKS",
    "SAATY_RI",
]
