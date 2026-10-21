"""
AHPService — Proceso Analítico Jerárquico (tesis SADE / Apéndice B).

Capacidades:
- Reconstrucción recíproca: a_ij = v_ij / v_ji (diagonal 1; a_ji = 1/a_ij)
- AIJ: media geométrica por celda de matrices de varios expertos
- Autovector principal → pesos locales; globales = local × peso de bloque
- IC = (λmáx − n)/(n − 1); CR = IC/IA (índice aleatorio Saaty)
- Diagnóstico de panel: CR individual, mediana, % con CR ≥ 0.10
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

# Índice aleatorio Saaty (IA / RI) para n = 1..15
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
# Umbral de % de expertos inconsistentes para advertir falta de consenso
DEFAULT_PANEL_INCONSISTENT_PCT = 0.50


@dataclass(frozen=True)
class AHPResult:
    """Resultado de prioridades y consistencia de una matriz."""

    weights: np.ndarray
    lambda_max: float
    consistency_index: float  # IC
    random_index: float  # IA
    consistency_ratio: float  # CR = IC/IA
    is_consistent: bool
    n: int
    advertencia_cr: str = ""  # mensaje si CR ≥ umbral


@dataclass
class PanelConsistencyReport:
    """Diagnóstico de consistencia del panel (Apéndice B / RF-032)."""

    cr_por_experto: list[float]
    mediana_cr: float
    n_expertos: int
    n_inconsistentes: int
    pct_inconsistentes: float
    cr_agregada: float
    pesos_agregados: np.ndarray
    advertencia_consenso: bool
    mensaje: str
    threshold: float = DEFAULT_CR_THRESHOLD
    labels: list[str] = field(default_factory=list)


class AHPService:
    """
    Servicio AHP alineado a la tesis (reconstrucción direccional + AIJ).
    """

    def __init__(
        self,
        cr_threshold: float = DEFAULT_CR_THRESHOLD,
        panel_inconsistent_pct: float = DEFAULT_PANEL_INCONSISTENT_PCT,
    ):
        self.cr_threshold = cr_threshold
        self.panel_inconsistent_pct = panel_inconsistent_pct

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @staticmethod
    def random_index(n: int) -> float:
        if n < 1:
            raise ValueError("n debe ser >= 1")
        return SAATY_RI.get(n, SAATY_RI[15])

    @staticmethod
    def validate_reciprocal(matrix: np.ndarray, tol: float = 1e-6) -> None:
        a = np.asarray(matrix, dtype=float)
        if a.ndim != 2 or a.shape[0] != a.shape[1]:
            raise ValueError("La matriz de pares debe ser cuadrada")
        n = a.shape[0]
        if np.any(a <= 0):
            raise ValueError("Las entradas deben ser positivas")
        for i in range(n):
            if abs(a[i, i] - 1.0) > tol:
                raise ValueError("La diagonal debe ser 1")
            for j in range(i + 1, n):
                if abs(a[i, j] * a[j, i] - 1.0) > tol * max(1.0, abs(a[i, j])):
                    raise ValueError(
                        f"Matriz no recíproca en ({i},{j}): "
                        f"{a[i, j]} * {a[j, i]} != 1"
                    )

    @staticmethod
    def reconstruct_reciprocal(
        directional: np.ndarray,
        *,
        tol: float = 1e-12,
    ) -> np.ndarray:
        """
        Reconstruye matriz recíproca desde juicios direccionales (tesis §4.5 / Ap. B):

            a_ij = v(i sobre j) / v(j sobre i)
            a_ji = 1 / a_ij
            a_ii = 1

        ``directional[i, j]`` = v(i sobre j). La diagonal de entrada se ignora.
        """
        v = np.asarray(directional, dtype=float)
        if v.ndim != 2 or v.shape[0] != v.shape[1]:
            raise ValueError("directional debe ser cuadrada")
        n = v.shape[0]
        if np.any(v <= 0):
            raise ValueError("Los juicios direccionales deben ser positivos")
        out = np.ones((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                ratio = v[i, j] / v[j, i]
                if ratio <= tol:
                    raise ValueError(f"Cociente inválido en ({i},{j})")
                out[i, j] = ratio
                out[j, i] = 1.0 / ratio
        return out

    @staticmethod
    def matrix_from_weights(weights: Sequence[float]) -> np.ndarray:
        """
        Matriz perfectamente consistente a_ij = w_i / w_j.

        Útil como fixture cuando el extracto no incluye matrices crudas del
        Apéndice B: recupera exactamente los pesos publicados (CR ≈ 0).
        """
        w = np.asarray(weights, dtype=float)
        if np.any(w <= 0):
            raise ValueError("weights deben ser positivos")
        w = w / w.sum()
        return np.outer(w, 1.0 / w)

    # ------------------------------------------------------------------
    # Autovector / CR
    # ------------------------------------------------------------------

    @staticmethod
    def _row_geometric_mean_weights(matrix: np.ndarray) -> np.ndarray:
        gm = np.prod(matrix, axis=1) ** (1.0 / matrix.shape[0])
        return gm / gm.sum()

    def principal_eigenvector(self, matrix: np.ndarray) -> tuple[np.ndarray, float]:
        a = np.asarray(matrix, dtype=float)
        self.validate_reciprocal(a)
        eigenvalues, eigenvectors = np.linalg.eig(a)
        idx = int(np.argmax(np.real(eigenvalues)))
        lambda_max = float(np.real(eigenvalues[idx]))
        vec = np.real(eigenvectors[:, idx])
        if np.all(vec <= 0):
            vec = -vec
        if np.any(vec < 0):
            vec = self._row_geometric_mean_weights(a)
            aw = a @ vec
            lambda_max = float(np.mean(aw / vec))
        weights = vec / vec.sum()
        return weights.astype(float), lambda_max

    def consistency_index(self, lambda_max: float, n: int) -> float:
        if n <= 1:
            return 0.0
        return (lambda_max - n) / (n - 1)

    def consistency_ratio(self, matrix: np.ndarray) -> AHPResult:
        weights, lambda_max = self.principal_eigenvector(matrix)
        n = int(matrix.shape[0])
        ic = self.consistency_index(lambda_max, n)
        ia = self.random_index(n)
        cr = 0.0 if ia == 0.0 else ic / ia
        ok = cr < self.cr_threshold
        advertencia = ""
        if not ok:
            advertencia = (
                f"ADVERTENCIA: CR={cr:.4f} ≥ {self.cr_threshold} "
                f"(IC={ic:.4f}, IA={ia}). Revisar juicios (Saaty, 1980)."
            )
        return AHPResult(
            weights=weights,
            lambda_max=lambda_max,
            consistency_index=ic,
            random_index=ia,
            consistency_ratio=cr,
            is_consistent=ok,
            n=n,
            advertencia_cr=advertencia,
        )

    def validate_cr(
        self,
        matrix: np.ndarray,
        threshold: float | None = None,
        *,
        raise_on_fail: bool = True,
    ) -> AHPResult:
        """Evalúa CR; por defecto lanza ValueError si CR ≥ umbral."""
        thr = self.cr_threshold if threshold is None else threshold
        result = self.consistency_ratio(matrix)
        ok = result.consistency_ratio < thr
        result = AHPResult(
            weights=result.weights,
            lambda_max=result.lambda_max,
            consistency_index=result.consistency_index,
            random_index=result.random_index,
            consistency_ratio=result.consistency_ratio,
            is_consistent=ok,
            n=result.n,
            advertencia_cr=(
                ""
                if ok
                else (
                    f"ADVERTENCIA: CR={result.consistency_ratio:.4f} ≥ {thr} "
                    f"(IC={result.consistency_index:.4f}, IA={result.random_index})."
                )
            ),
        )
        if raise_on_fail and not ok:
            raise ValueError(result.advertencia_cr)
        return result

    def weights_from_pairwise(self, matrix: np.ndarray) -> AHPResult:
        return self.consistency_ratio(matrix)

    def global_weights(
        self,
        local_weights: Sequence[float],
        block_weight: float,
    ) -> np.ndarray:
        """peso_global = peso_local × peso_bloque."""
        local = np.asarray(local_weights, dtype=float)
        return local * float(block_weight)

    # ------------------------------------------------------------------
    # AIJ y diagnóstico de panel
    # ------------------------------------------------------------------

    def aggregate_aij(self, matrices: Sequence[np.ndarray]) -> np.ndarray:
        """Media geométrica por celda (AIJ); garantiza reciprocidad."""
        if not matrices:
            raise ValueError("matrices no puede estar vacío")
        stack = [np.asarray(m, dtype=float) for m in matrices]
        n = stack[0].shape[0]
        for m in stack:
            if m.shape != (n, n):
                raise ValueError("Todas las matrices deben compartir forma")
            self.validate_reciprocal(m)
        geo = np.prod(np.array(stack), axis=0) ** (1.0 / len(stack))
        out = np.ones((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                out[i, j] = geo[i, j]
                out[j, i] = 1.0 / geo[i, j]
        self.validate_reciprocal(out)
        return out

    def diagnose_panel(
        self,
        expert_matrices: Sequence[np.ndarray],
        *,
        labels: Sequence[str] | None = None,
        inconsistent_pct_threshold: float | None = None,
    ) -> PanelConsistencyReport:
        """
        CR por experto, mediana, % con CR ≥ umbral, CR de matriz AIJ agregada.

        Si el % inconsistente supera el umbral configurable, marca
        ``advertencia_consenso`` (la CR agregada no implica consenso).
        """
        if not expert_matrices:
            raise ValueError("expert_matrices no puede estar vacío")
        thr_pct = (
            self.panel_inconsistent_pct
            if inconsistent_pct_threshold is None
            else inconsistent_pct_threshold
        )
        crs: list[float] = []
        for m in expert_matrices:
            r = self.consistency_ratio(m)
            crs.append(float(r.consistency_ratio))
        n_exp = len(crs)
        n_bad = sum(1 for c in crs if c >= self.cr_threshold)
        pct = n_bad / n_exp
        mediana = float(np.median(crs))
        agg = self.aggregate_aij(expert_matrices)
        agg_result = self.consistency_ratio(agg)
        adv = pct > thr_pct
        if adv:
            mensaje = (
                f"Advertencia de consenso: {pct:.0%} de expertos con "
                f"CR ≥ {self.cr_threshold} (mediana individual={mediana:.4f}). "
                f"CR agregada={agg_result.consistency_ratio:.4f} no implica acuerdo "
                f"(tesis Apéndice B)."
            )
        else:
            mensaje = (
                f"Panel: {pct:.0%} inconsistentes; mediana CR={mediana:.4f}; "
                f"CR agregada={agg_result.consistency_ratio:.4f}."
            )
        return PanelConsistencyReport(
            cr_por_experto=crs,
            mediana_cr=mediana,
            n_expertos=n_exp,
            n_inconsistentes=n_bad,
            pct_inconsistentes=pct,
            cr_agregada=float(agg_result.consistency_ratio),
            pesos_agregados=agg_result.weights,
            advertencia_consenso=adv,
            mensaje=mensaje,
            threshold=self.cr_threshold,
            labels=list(labels or []),
        )
