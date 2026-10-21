"""
SensitivityService — análisis E0–E8 según Tabla 4.3 (tesis SADE).

E0  Pesos AHP Apéndice B (referencia)
E1  Pesos iguales dentro de cada bloque; pesos de bloque AHP
E2  Pesos iguales para los 21 criterios
E3–E8  Peso de cada bloque ±10 % y ±20 %, renormalizando:
       E3 GEO +10 %, E4 GEO −10 %,
       E5 ECO +20 %, E6 ECO −20 %,
       E7 SOC +10 %, E8 SOC −20 %

Índice de Jaccard sobre celdas Favorable + Óptimo (RF-040).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np
from django.db import transaction

from apps.escenarios.hashing import hash_resultado
from apps.escenarios.models import Escenario
from apps.multicriterio.models import ConjuntoPesosAHP, PesoCriterio
from apps.multicriterio.services import SuitabilityClass
from apps.multicriterio.tests.fixtures.apendice_b_pesos import (
    BLOQUE_WEIGHTS,
    IDS_21,
    PESOS_GLOBALES_21,
    PESOS_LOCALES_ECO,
    PESOS_LOCALES_GEO,
    PESOS_LOCALES_SOC,
)
from apps.reglas.data.initial_rules import BLOQUE_WEIGHTS as SEED_BLOQUE_WEIGHTS

# Tabla 4.3 — perturbaciones de bloque E3–E8
TABLA_43_BLOCK_PERTURBATIONS: tuple[tuple[str, str, float], ...] = (
    ("E3", "geohidrologico", 0.10),
    ("E4", "geohidrologico", -0.10),
    ("E5", "ecologico", 0.20),
    ("E6", "ecologico", -0.20),
    ("E7", "socioeconomico", 0.10),
    ("E8", "socioeconomico", -0.20),
)

BLOCK_IDS = {
    "geohidrologico": [f"GEO_{i:02d}" for i in range(1, 8)],
    "ecologico": [f"ECO_{i:02d}" for i in range(1, 5)],
    "socioeconomico": [f"SOC_{i:02d}" for i in range(1, 11)],
}

LOCALS_BY_BLOCK = {
    "geohidrologico": PESOS_LOCALES_GEO,
    "ecologico": PESOS_LOCALES_ECO,
    "socioeconomico": PESOS_LOCALES_SOC,
}


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
    baseline_escenario_id: int | None
    experiments: list[dict[str, Any]]
    pairwise_jaccard: list[SensitivityPair]
    jaccard_vs_e0: list[dict[str, Any]] = field(default_factory=list)
    zonas_estables_favorable_optimo: dict[str, Any] = field(default_factory=dict)
    notes: str = (
        "Tabla 4.3: E0 base AHP; E1 iguales en bloque; E2 iguales 21; "
        "E3–E8 bloque ±10%/±20% renormalizado. Jaccard = Favorable+Óptimo."
    )


class SensitivityService:
    """Genera y ejecuta E1–E8 a partir de un escenario base E0."""

    def __init__(self, execution_service=None):
        # Lazy import para evitar ciclo con execution
        if execution_service is None:
            from apps.escenarios.services.execution import EscenarioExecutionService

            execution_service = EscenarioExecutionService()
        self.execution = execution_service

    # ------------------------------------------------------------------
    # Pesos Tabla 4.3
    # ------------------------------------------------------------------

    @staticmethod
    def pesos_e0_apendice_b(
        conjunto: ConjuntoPesosAHP | None = None,
    ) -> dict[str, float]:
        """Pesos globales E0: DB del conjunto si hay 21 filas; si no, Apéndice B."""
        if conjunto is not None:
            rows = list(
                PesoCriterio.objects.filter(conjunto=conjunto)
                .select_related("criterio")
                .order_by("criterio__id_criterio")
            )
            if len(rows) >= 21:
                return {
                    r.criterio.id_criterio: float(r.peso_global) for r in rows[:21]
                }
        return {cid: float(w) for cid, w in zip(IDS_21, PESOS_GLOBALES_21)}

    @staticmethod
    def pesos_e1_iguales_en_bloque(
        block_weights: Mapping[str, float] | None = None,
    ) -> dict[str, float]:
        bw = dict(block_weights or SEED_BLOQUE_WEIGHTS or BLOQUE_WEIGHTS)
        out: dict[str, float] = {}
        for bloque, ids in BLOCK_IDS.items():
            n = len(ids)
            share = float(bw[bloque]) / n
            for cid in ids:
                out[cid] = share
        return _renorm_dict(out)

    @staticmethod
    def pesos_e2_iguales_21() -> dict[str, float]:
        w = 1.0 / 21.0
        return {cid: w for cid in IDS_21}

    @staticmethod
    def pesos_bloque_perturbado(
        *,
        bloque: str,
        delta: float,
        block_weights: Mapping[str, float] | None = None,
        locales: Mapping[str, Sequence[float]] | None = None,
    ) -> dict[str, float]:
        """
        Multiplica el peso del bloque por (1+delta) y renormaliza los tres
        bloques; redistribuye con pesos locales AHP (Apéndice B).
        """
        bw = dict(block_weights or BLOQUE_WEIGHTS)
        if bloque not in bw:
            raise ValueError(f"Bloque desconocido: {bloque}")
        bw[bloque] = bw[bloque] * (1.0 + float(delta))
        total = sum(bw.values()) or 1.0
        bw = {k: v / total for k, v in bw.items()}
        locs = locales or LOCALS_BY_BLOCK
        out: dict[str, float] = {}
        for b, ids in BLOCK_IDS.items():
            local = list(locs[b])
            if len(local) != len(ids):
                local = [1.0 / len(ids)] * len(ids)
            s_loc = sum(local) or 1.0
            local = [x / s_loc for x in local]
            for cid, lw in zip(ids, local):
                out[cid] = bw[b] * lw
        return _renorm_dict(out)

    def esquema_pesos(self, experiment_id: str, conjunto: ConjuntoPesosAHP) -> dict[str, float]:
        eid = experiment_id.upper()
        if eid == "E0":
            return self.pesos_e0_apendice_b(conjunto)
        if eid == "E1":
            return self.pesos_e1_iguales_en_bloque()
        if eid == "E2":
            return self.pesos_e2_iguales_21()
        for label, bloque, delta in TABLA_43_BLOCK_PERTURBATIONS:
            if label == eid:
                return self.pesos_bloque_perturbado(bloque=bloque, delta=delta)
        raise ValueError(f"Experimento de sensibilidad desconocido: {experiment_id}")

    # ------------------------------------------------------------------
    # Jaccard Favorable + Óptimo
    # ------------------------------------------------------------------

    @staticmethod
    def mascara_favorable_optimo(class_map: np.ndarray | list) -> np.ndarray:
        cm = np.asarray(class_map)
        return cm >= int(SuitabilityClass.FAVORABLE)

    @classmethod
    def jaccard_binary(
        cls, a: np.ndarray, b: np.ndarray
    ) -> tuple[float, int, int]:
        a_b = np.asarray(a, dtype=bool).ravel()
        b_b = np.asarray(b, dtype=bool).ravel()
        inter = int(np.logical_and(a_b, b_b).sum())
        union = int(np.logical_or(a_b, b_b).sum())
        if union == 0:
            return 1.0, 0, 0
        return inter / union, inter, union

    def calcular_indice_jaccard(
        self,
        escenario_a: Escenario,
        escenario_b: Escenario,
    ) -> dict[str, Any]:
        """Jaccard de zonas Favorable+Óptimo entre dos escenarios (RF-040)."""
        cm_a = (escenario_a.resultados_json or {}).get("class_map")
        cm_b = (escenario_b.resultados_json or {}).get("class_map")
        if cm_a is None or cm_b is None:
            raise ValueError("Ambos escenarios deben tener resultados_json.class_map")
        mask_a = self.mascara_favorable_optimo(cm_a)
        mask_b = self.mascara_favorable_optimo(cm_b)
        jac, inter, union = self.jaccard_binary(mask_a, mask_b)
        return {
            "escenario_a_id": escenario_a.pk,
            "escenario_b_id": escenario_b.pk,
            "jaccard": round(float(jac), 6),
            "intersection_cells": inter,
            "union_cells": union,
            "clases": ["Favorable", "Óptimo"],
        }

    # ------------------------------------------------------------------
    # Ejecución E0–E8
    # ------------------------------------------------------------------

    @transaction.atomic
    def ejecutar_analisis_sensibilidad(
        self,
        escenario_base_e0: Escenario,
        *,
        persist: bool = True,
    ) -> SensitivityReport:
        """
        A partir del escenario base (E0), genera y ejecuta E1–E8 (Tabla 4.3).
        """
        conjunto = escenario_base_e0.conjunto_pesos
        base_params = dict(escenario_base_e0.parametros_ejecucion or {})
        base_params.setdefault("demo_seed", 42)
        base_params.setdefault("shape", [8, 8])
        # Sensibilidad tesis: 21 criterios (descarta weights de demos cortos)
        base_params["n_criteria"] = 21
        base_params.pop("weights", None)
        version = escenario_base_e0.version_reglas_usada

        experiments: list[dict[str, Any]] = []
        masks: dict[str, np.ndarray] = {}
        escenarios_by_id: dict[str, Escenario] = {"E0": escenario_base_e0}

        # Asegurar máscara E0
        cm0 = (escenario_base_e0.resultados_json or {}).get("class_map")
        if cm0 is None:
            # Re-ejecutar E0 con 21 criterios si hace falta
            pesos0 = self.esquema_pesos("E0", conjunto)
            params0 = dict(base_params)
            params0["weights"] = [pesos0[c] for c in IDS_21]
            params0["sensitivity_id"] = "E0"
            out0 = self.execution.execute(
                nombre=escenario_base_e0.nombre or "Sensibilidad E0",
                version_reglas_usada=version,
                conjunto_pesos=conjunto,
                parametros_ejecucion=params0,
                weights_from_db=False,
            )
            escenario_base_e0 = out0.escenario
            escenarios_by_id["E0"] = escenario_base_e0
            cm0 = out0.class_map
        masks["E0"] = self.mascara_favorable_optimo(cm0)

        pesos0 = self.esquema_pesos("E0", conjunto)
        experiments.append(
            {
                "id": "E0",
                "descripcion": "Pesos AHP del Apéndice B (base)",
                "weights": [pesos0[c] for c in IDS_21],
                "weights_by_id": pesos0,
                "class_counts": (escenario_base_e0.resultados_json or {}).get(
                    "class_counts", {}
                ),
                "hash_resultado": escenario_base_e0.hash_resultado,
                "escenario_id": escenario_base_e0.pk,
                "hash_configuracion": escenario_base_e0.hash_configuracion,
            }
        )

        for eid in [f"E{i}" for i in range(1, 9)]:
            pesos = self.esquema_pesos(eid, conjunto)
            params = dict(base_params)
            params["weights"] = [pesos[c] for c in IDS_21]
            params["sensitivity_id"] = eid
            params["tabla_4_3"] = _meta_for(eid)
            resultados = self.execution.run_engine(params)
            class_map = np.asarray(resultados["class_map"])
            masks[eid] = self.mascara_favorable_optimo(class_map)
            entry: dict[str, Any] = {
                "id": eid,
                "descripcion": _meta_for(eid).get("proposito", ""),
                "weights": params["weights"],
                "weights_by_id": pesos,
                "class_counts": resultados["class_counts"],
                "hash_resultado": hash_resultado(resultados),
                "perturbacion": _meta_for(eid),
            }
            if persist:
                out = self.execution.execute(
                    nombre=f"Sensibilidad {eid}",
                    version_reglas_usada=version,
                    conjunto_pesos=conjunto,
                    parametros_ejecucion=params,
                    weights_from_db=False,
                )
                entry["escenario_id"] = out.escenario.pk
                entry["hash_configuracion"] = out.escenario.hash_configuracion
                escenarios_by_id[eid] = out.escenario
            experiments.append(entry)

        # Jaccard vs E0
        jaccard_vs_e0: list[dict[str, Any]] = []
        for eid, mask in masks.items():
            if eid == "E0":
                continue
            jac, inter, union = self.jaccard_binary(masks["E0"], mask)
            jaccard_vs_e0.append(
                {
                    "scenario_a": "E0",
                    "scenario_b": eid,
                    "jaccard": round(jac, 6),
                    "intersection_cells": inter,
                    "union_cells": union,
                }
            )

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

        # Zonas estables: Favorable+Óptimo en todos los escenarios
        stable = np.ones_like(masks["E0"], dtype=bool)
        for m in masks.values():
            stable = np.logical_and(stable, m)
        zonas_estables = {
            "celdas": int(stable.sum()),
            "total_celdas": int(stable.size),
            "fraccion": round(float(stable.sum()) / float(stable.size or 1), 6),
            "definicion": "Favorable u Óptimo en E0–E8",
        }

        return SensitivityReport(
            baseline_id="E0",
            baseline_escenario_id=escenario_base_e0.pk,
            experiments=experiments,
            pairwise_jaccard=pairs,
            jaccard_vs_e0=jaccard_vs_e0,
            zonas_estables_favorable_optimo=zonas_estables,
        )


def _renorm_dict(weights: dict[str, float]) -> dict[str, float]:
    s = sum(weights.values()) or 1.0
    return {k: float(v) / s for k, v in weights.items()}


def _meta_for(eid: str) -> dict[str, Any]:
    if eid == "E1":
        return {
            "proposito": "Pesos iguales dentro de cada bloque; pesos de bloque AHP",
        }
    if eid == "E2":
        return {"proposito": "Pesos iguales para los 21 criterios"}
    for label, bloque, delta in TABLA_43_BLOCK_PERTURBATIONS:
        if label == eid:
            pct = int(abs(delta) * 100)
            signo = "+" if delta > 0 else "−"
            return {
                "proposito": f"Peso bloque {bloque} {signo}{pct} %, renormalizando",
                "bloque": bloque,
                "delta": delta,
            }
    return {"proposito": "Base AHP"}
