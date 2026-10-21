"""
Deterministic hashing for Escenario auditability (PASO 4).

hash_configuracion
  SHA-256 hex of canonical JSON:
  {
    "version_reglas_usada": str,
    "conjunto_pesos_id": int,
    "parametros_ejecucion": <canonical dict>
  }

hash_resultado
  SHA-256 hex of canonical JSON of resultados_json (class_counts, class_map
  digest, candidates summary — whatever was persisted).

Canonical JSON: UTF-8, sort_keys=True, separators=(",", ":"),
numpy-friendly via _json_default.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

import numpy as np


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def canonical_json(payload: Mapping[str, Any] | list | dict) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    )


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_configuracion(
    *,
    version_reglas_usada: str,
    conjunto_pesos_id: int,
    parametros_ejecucion: Mapping[str, Any],
) -> str:
    payload = {
        "conjunto_pesos_id": int(conjunto_pesos_id),
        "parametros_ejecucion": dict(parametros_ejecucion or {}),
        "version_reglas_usada": str(version_reglas_usada),
    }
    return sha256_hex(canonical_json(payload))


def hash_resultado(resultados_json: Mapping[str, Any]) -> str:
    return sha256_hex(canonical_json(dict(resultados_json or {})))
