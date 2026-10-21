"""
Placeholder seed for Tabla 4.1 (21 criterios) + Apéndice B (pesos AHP).

IMPORTANT — placeholder pending thesis PDF:
  The repository does not contain Tabla 4.1 or Apéndice B text. This module
  defines a well-documented set of 21 ids (GEO_*, ECO_*, SOC_*) aligned with
  typical NOM-083-SEMARNAT-2003 landfill siting criteria for Valles de Jalisco.
  Replace nombres / parametros / pesos locales with thesis values when the PDF
  is available; keep id_criterio stable where possible.

Block weights (Apéndice B, provided in PASO 2 brief):
  Geohidrológico 36.54%, Ecológico 31.01%, Socioeconómico 32.45%.

Per-criterion peso_local: uniform 1/7 within each block (placeholder).
peso_global = peso_local * bloque_weight.

CR (consistency ratio): left at 0.0 — real CR is produced by AHPService (PASO 3+).
"""

from __future__ import annotations

from typing import Any, TypedDict

DEFAULT_REGLA_VERSION = "1.0.0"
DEFAULT_AHP_NOMBRE = "AHP Apéndice B — default Valles de Jalisco"

# Apéndice B block weights (fractions)
BLOQUE_WEIGHTS: dict[str, float] = {
    "geohidrologico": 0.3654,
    "ecologico": 0.3101,
    "socioeconomico": 0.3245,
}


class CriterioSeed(TypedDict):
    id_criterio: str
    nombre: str
    bloque: str
    fuente: str
    tipo_restriccion: str
    activo: bool
    regla: dict[str, Any]


# 21 criteria — 7 GEO + 7 ECO + 7 SOC
CRITERIOS_SEED: list[CriterioSeed] = [
    # --- Geohidrológico ---
    {
        "id_criterio": "GEO_01",
        "nombre": "Distancia a cuerpos de agua superficiales",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.6",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": "Buffer mínimo 500 m a lagos, lagunas y cauces de caudal continuo.",
            "parametros_json": {
                "buffer_m": 500,
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.6",
            },
        },
    },
    {
        "id_criterio": "GEO_02",
        "nombre": "Distancia a pozos de extracción de agua",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.7",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": (
                "500 m mínimo cuando no se determina el cono de abatimiento "
                "(100 m + proyección del cono si se conoce)."
            ),
            "parametros_json": {
                "buffer_m": 500,
                "buffer_cono_abatimiento_extra_m": 100,
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.7",
            },
        },
    },
    {
        "id_criterio": "GEO_03",
        "nombre": "Zonas de inundación (Tr 100 años)",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.5",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": "Exclusión de zonas inundables con periodo de retorno de 100 años.",
            "parametros_json": {
                "periodo_retorno_anios": 100,
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.5",
            },
        },
    },
    {
        "id_criterio": "GEO_04",
        "nombre": "Zonas de recarga de acuíferos",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": "Exclusión de zonas de recarga de acuíferos.",
            "parametros_json": {
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.4",
            },
        },
    },
    {
        "id_criterio": "GEO_05",
        "nombre": "Profundidad del nivel freático",
        "bloque": "geohidrologico",
        "fuente": "NOM-083 / estudio hidrogeológico",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": (
                "Mayor profundidad del NF favorece idoneidad. Umbral placeholder "
                "pending thesis PDF."
            ),
            "parametros_json": {
                "profundidad_minima_m": 10,
                "suitability": "linear_increasing",
                "notes": "placeholder threshold",
            },
        },
    },
    {
        "id_criterio": "GEO_06",
        "nombre": "Permeabilidad / litología del suelo",
        "bloque": "geohidrologico",
        "fuente": "Estudio geológico / hidrogeológico",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": "Baja permeabilidad favorece contención de lixiviados.",
            "parametros_json": {
                "prefer_low_permeability": True,
                "suitability": "ordered_classes",
                "notes": "placeholder class ranking",
            },
        },
    },
    {
        "id_criterio": "GEO_07",
        "nombre": "Fallas, fracturas y cavernas",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": "Exclusión sobre cavernas, fracturas o fallas geológicas.",
            "parametros_json": {
                "buffer_m": 0,
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.4",
            },
        },
    },
    # --- Ecológico ---
    {
        "id_criterio": "ECO_01",
        "nombre": "Áreas Naturales Protegidas (ANP)",
        "bloque": "ecologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.2",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": "Exclusión dentro de ANP (salvo plan de manejo que lo contemple).",
            "parametros_json": {
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.2",
            },
        },
    },
    {
        "id_criterio": "ECO_02",
        "nombre": "Humedales, marismas, manglares y pantanos",
        "bloque": "ecologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": "Exclusión de humedales y ecosistemas acuáticos asociados.",
            "parametros_json": {
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.4",
            },
        },
    },
    {
        "id_criterio": "ECO_03",
        "nombre": "Cobertura vegetal / uso de suelo forestal",
        "bloque": "ecologico",
        "fuente": "INEGI / ERS",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": "Preferir usos de menor valor ecológico; bosques con baja idoneidad.",
            "parametros_json": {
                "suitability": "ordered_classes",
                "notes": "placeholder land-cover ranking",
            },
        },
    },
    {
        "id_criterio": "ECO_04",
        "nombre": "Hábitat y corredores de biodiversidad",
        "bloque": "ecologico",
        "fuente": "CONABIO / ERS",
        "tipo_restriccion": "advertencia",
        "activo": True,
        "regla": {
            "descripcion": "Advertencia sobre hábitats prioritarios; no exclusión dura por defecto.",
            "parametros_json": {
                "suitability": "linear_decreasing",
                "notes": "placeholder pending thesis PDF",
            },
        },
    },
    {
        "id_criterio": "ECO_05",
        "nombre": "Pendiente del terreno",
        "bloque": "ecologico",
        "fuente": "SEDESOL / buenas prácticas siting",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": "Pendientes moderadas preferidas; muy altas reducen idoneidad.",
            "parametros_json": {
                "slope_max_pct": 30,
                "suitability": "piecewise_linear",
                "notes": "placeholder threshold",
            },
        },
    },
    {
        "id_criterio": "ECO_06",
        "nombre": "Erosión e inestabilidad de laderas",
        "bloque": "ecologico",
        "fuente": "Estudio geotécnico / ERS",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": "Zonas de alta erosión o inestabilidad con baja idoneidad.",
            "parametros_json": {
                "suitability": "ordered_classes",
                "notes": "placeholder",
            },
        },
    },
    {
        "id_criterio": "ECO_07",
        "nombre": "Zonas arqueológicas",
        "bloque": "ecologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4 / INAH",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": "Exclusión de zonas arqueológicas.",
            "parametros_json": {
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.4",
            },
        },
    },
    # --- Socioeconómico ---
    {
        "id_criterio": "SOC_01",
        "nombre": "Distancia a traza urbana (≥2 500 hab.)",
        "bloque": "socioeconomico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.3",
        "tipo_restriccion": "normativa",
        "activo": True,
        "regla": {
            "descripcion": "Buffer mínimo 500 m desde traza urbana existente o planificada.",
            "parametros_json": {
                "buffer_m": 500,
                "poblacion_umbral": 2500,
                "suitability": "binary_exclusion",
                "notes": "NOM-083 §6.1.3",
            },
        },
    },
    {
        "id_criterio": "SOC_02",
        "nombre": "Proximidad a aeródromos / aeropuertos",
        "bloque": "socioeconomico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.1",
        "tipo_restriccion": "advertencia",
        "activo": True,
        "regla": {
            "descripcion": (
                "Si distancia < 13 km al centro de pista, requiere estudio de riesgo aviario."
            ),
            "parametros_json": {
                "warning_radius_m": 13000,
                "suitability": "warning_within_radius",
                "notes": "NOM-083 §6.1.1 — aerodrome warning <13 km",
            },
        },
    },
    {
        "id_criterio": "SOC_03",
        "nombre": "Accesibilidad vial / distancia a carreteras",
        "bloque": "socioeconomico",
        "fuente": "SEDESOL / ERS",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": "Acceso razonable favorece operación; demasiado cercano puede ser conflicto.",
            "parametros_json": {
                "preferred_distance_m": [200, 2000],
                "suitability": "piecewise_linear",
                "notes": "placeholder pending thesis PDF",
            },
        },
    },
    {
        "id_criterio": "SOC_04",
        "nombre": "Densidad de población en área de influencia",
        "bloque": "socioeconomico",
        "fuente": "INEGI / SEDESOL",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": "Menor densidad poblacional aumenta idoneidad relativa.",
            "parametros_json": {
                "suitability": "linear_decreasing",
                "notes": "placeholder",
            },
        },
    },
    {
        "id_criterio": "SOC_05",
        "nombre": "Uso de suelo y tenencia",
        "bloque": "socioeconomico",
        "fuente": "Catastro / plan municipal",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": "Preferir suelos compatibles con disposición final.",
            "parametros_json": {
                "suitability": "ordered_classes",
                "notes": "placeholder land-use ranking",
            },
        },
    },
    {
        "id_criterio": "SOC_06",
        "nombre": "Distancia a infraestructura crítica",
        "bloque": "socioeconomico",
        "fuente": "ERS / buenas prácticas",
        "tipo_restriccion": "modelo",
        "activo": True,
        "regla": {
            "descripcion": (
                "Buffer/preferencia respecto a líneas eléctricas, ductos e industria sensible."
            ),
            "parametros_json": {
                "buffer_m": 100,
                "suitability": "binary_exclusion",
                "notes": "placeholder buffer",
            },
        },
    },
    {
        "id_criterio": "SOC_07",
        "nombre": "Conflicto social / aceptación comunitaria",
        "bloque": "socioeconomico",
        "fuente": "ERS / consulta pública",
        "tipo_restriccion": "advertencia",
        "activo": True,
        "regla": {
            "descripcion": "Capa de advertencia socioeconómica; no exclusión normativa dura.",
            "parametros_json": {
                "suitability": "warning_overlay",
                "notes": "placeholder pending thesis PDF",
            },
        },
    },
]

# Uniform local weights within each 7-criterion block (placeholder).
_LOCAL = 1.0 / 7.0
PESOS_LOCALES: dict[str, float] = {
    cid: _LOCAL
    for cid in (
        "GEO_01",
        "GEO_02",
        "GEO_03",
        "GEO_04",
        "GEO_05",
        "GEO_06",
        "GEO_07",
        "ECO_01",
        "ECO_02",
        "ECO_03",
        "ECO_04",
        "ECO_05",
        "ECO_06",
        "ECO_07",
        "SOC_01",
        "SOC_02",
        "SOC_03",
        "SOC_04",
        "SOC_05",
        "SOC_06",
        "SOC_07",
    )
}

assert len(CRITERIOS_SEED) == 21
assert len(PESOS_LOCALES) == 21
assert abs(sum(BLOQUE_WEIGHTS.values()) - 1.0) < 1e-9
