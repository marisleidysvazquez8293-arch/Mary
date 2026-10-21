"""
Semilla Tabla 4.1 + Apéndice B (tesis SADE Valles de Jalisco).

Fuente: docs/tesis-sade-valles-jalisco.docx (extractos en
internal/tesis-sade-extracto.txt y tesis-criterios-y-pesos-clave.txt).

21 criterios: GEO×7, ECO×4, SOC×10 (NO 7/7/7).
Pesos de bloque: GEO 36.54%, ECO 31.01%, SOC 32.45%.
CR agregados (AIJ): criterios 0.002, GEO 0.0035, ECO 0.0020, SOC 0.0047.
"""
from __future__ import annotations

from typing import Any, TypedDict

DEFAULT_REGLA_VERSION = "1.0.0"
DEFAULT_AHP_NOMBRE = "AHP Apéndice B — panel 15 expertos (AIJ)"

# Apéndice B — Tabla B.3
BLOQUE_WEIGHTS: dict[str, float] = {
    "geohidrologico": 0.3654,
    "ecologico": 0.3101,
    "socioeconomico": 0.3245,
}

# CR de matrices agregadas (Apéndice B / Tabla 4.2 narrativa)
CR_BLOQUES: dict[str, float] = {
    "cr_geohidro": 0.0035,
    "cr_ecol": 0.0020,
    "cr_socio": 0.0047,
}
CR_CRITERIOS_PRINCIPALES = 0.002

# Procedencia AHP (RF Apéndice A)
AHP_PROCEDENCIA: dict[str, Any] = {
    "panel": 15,
    "fechas": "2026-04-17 a 2026-05-07",
    "metodo_agregacion": "AIJ media geométrica (reconstrucción direccional)",
    "cr_criterios_principales": CR_CRITERIOS_PRINCIPALES,
    **CR_BLOQUES,
}


class CriterioSeed(TypedDict):
    id_criterio: str
    nombre: str
    bloque: str
    fuente: str
    tipo_restriccion: str
    activo: bool
    peso_local: float
    peso_global: float
    regla: dict[str, Any]


CRITERIOS_SEED: list[CriterioSeed] = [
    # --- Geohidrológico (7) — Tabla 4.1 + B.4 ---
    {
        "id_criterio": "GEO_01",
        "nombre": "Zonas de recarga de acuíferos",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4 / SEDESOL NTE-CRM-001/90",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.1412,
        "peso_global": 0.0516,
        "regla": {
            "descripcion": (
                "Excluye sitios en áreas de alta vulnerabilidad a la infiltración "
                "y contaminación del acuífero. SEDESOL sugiere >1 km a zonas de recarga."
            ),
            "parametros_json": {
                "suitability": "binary_exclusion",
                "buffer_m": 1000,
                "norma": "NOM-083 §6.1.4",
                "antecedente": "SEDESOL NTE-CRM-001/90 (>1 km)",
            },
        },
    },
    {
        "id_criterio": "GEO_02",
        "nombre": "Zona de inundación",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.5",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.1495,
        "peso_global": 0.0546,
        "regla": {
            "descripcion": (
                "Excluye áreas susceptibles de anegamiento o escurrimientos "
                "extraordinarios (periodo de retorno 100 años)."
            ),
            "parametros_json": {
                "periodo_retorno_anios": 100,
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.5",
            },
        },
    },
    {
        "id_criterio": "GEO_03",
        "nombre": "Fracturas o fallas geológicas",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4 / SEDESOL NTE-CRM-001/90",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.1444,
        "peso_global": 0.0528,
        "regla": {
            "descripcion": (
                "Excluye zonas con inestabilidad estructural o rutas preferenciales "
                "de infiltración de lixiviados. SEDESOL: >500 m a fallas/fracturas."
            ),
            "parametros_json": {
                "buffer_m": 500,
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.4",
                "antecedente": "SEDESOL (>500 m)",
            },
        },
    },
    {
        "id_criterio": "GEO_04",
        "nombre": "Zonas de riesgo de deslizamiento",
        "bloque": "geohidrologico",
        "fuente": "Antecedente técnico / panel de expertos (Tabla 4.1)",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.1533,
        "peso_global": 0.0560,
        "regla": {
            "descripcion": (
                "Excluye terrenos con susceptibilidad a movimientos de ladera "
                "o pérdida de estabilidad física."
            ),
            "parametros_json": {
                "suitability": "binary_exclusion",
                "origen": "modelo_tecnico",
            },
        },
    },
    {
        "id_criterio": "GEO_05",
        "nombre": "Cavernas",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.1280,
        "peso_global": 0.0468,
        "regla": {
            "descripcion": (
                "Excluye áreas con vacíos subterráneos o alta permeabilidad "
                "que incrementan el riesgo geotécnico e hidrogeológico."
            ),
            "parametros_json": {
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.4",
            },
        },
    },
    {
        "id_criterio": "GEO_06",
        "nombre": "Planicies aluviales",
        "bloque": "geohidrologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.1374,
        "peso_global": 0.0502,
        "regla": {
            "descripcion": (
                "Descarta zonas con dinámica sedimentaria o hidrológica "
                "desfavorable para la disposición final."
            ),
            "parametros_json": {
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.4",
            },
        },
    },
    {
        "id_criterio": "GEO_07",
        "nombre": "Tipo de suelo",
        "bloque": "geohidrologico",
        "fuente": "SEDESOL NTE-CRM-001/90 / estudio geotécnico",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.1462,
        "peso_global": 0.0534,
        "regla": {
            "descripcion": (
                "Valora capacidad portante e infiltración (factor continuo 0–5). "
                "SEDESOL: profundidad del manto freático >10 m como referencia."
            ),
            "parametros_json": {
                "suitability": "ordered_classes",
                "profundidad_freatico_min_m": 10,
                "escala_factor": [0, 5],
                "antecedente": "SEDESOL NTE-CRM-001/90",
            },
        },
    },
    # --- Ecológico (4) — Tabla 4.1 + B.5 ---
    {
        "id_criterio": "ECO_01",
        "nombre": "Cuerpos de agua superficial (buffer 500 m)",
        "bloque": "ecologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.6",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.2824,
        "peso_global": 0.0876,
        "regla": {
            "descripcion": (
                "Protege cauces, ríos y cuerpos de agua superficiales de caudal "
                "continuo con buffer mínimo de 500 m."
            ),
            "parametros_json": {
                "buffer_m": 500,
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.6",
                "regla_respaldo": (
                    "Si no hay capa de cuerpos de agua, índice sustituto "
                    "(corrientes, litología, pendiente)."
                ),
            },
        },
    },
    {
        "id_criterio": "ECO_02",
        "nombre": "Pozos de extracción de agua (buffer 500 m)",
        "bloque": "ecologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.7",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.2407,
        "peso_global": 0.0747,
        "regla": {
            "descripcion": (
                "Evita afectaciones a fuentes de abastecimiento. "
                "100 m + cono de abatimiento; respaldo 500 m si no se determina."
            ),
            "parametros_json": {
                "buffer_m": 500,
                "buffer_cono_abatimiento_extra_m": 100,
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.7",
                "es_regla_respaldo_posible": True,
            },
        },
    },
    {
        "id_criterio": "ECO_03",
        "nombre": "Ecosistemas acuáticos",
        "bloque": "ecologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.2473,
        "peso_global": 0.0767,
        "regla": {
            "descripcion": (
                "Restringe localización en marismas, manglares, esteros, "
                "pantanos, humedales y entornos de alto valor ecológico."
            ),
            "parametros_json": {
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.4",
            },
        },
    },
    {
        "id_criterio": "ECO_04",
        "nombre": "Áreas Naturales Protegidas",
        "bloque": "ecologico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.2",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.2296,
        "peso_global": 0.0712,
        "regla": {
            "descripcion": (
                "Impide ubicación en ANP (salvo plan de manejo que lo contemple)."
            ),
            "parametros_json": {
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.2",
            },
        },
    },
    # --- Socioeconómico (10) — Tabla 4.1 + B.6 ---
    {
        "id_criterio": "SOC_01",
        "nombre": "Distancia a aeródromo (13 km)",
        "bloque": "socioeconomico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.1",
        "tipo_restriccion": "advertencia",
        "activo": True,
        "peso_local": 0.1049,
        "peso_global": 0.0340,
        "regla": {
            "descripcion": (
                "Celdas a menos de 13 km del centro de pista: advertencia "
                "«requiere estudio de riesgo aviario» (no exclusión dura)."
            ),
            "parametros_json": {
                "warning_radius_m": 13000,
                "suitability": "warning_within_radius",
                "norma": "NOM-083 §6.1.1",
                "hard_exclude": False,
            },
        },
    },
    {
        "id_criterio": "SOC_02",
        "nombre": "Proximidad a localidades >2 500 hab. (buffer 500 m)",
        "bloque": "socioeconomico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.3",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.1002,
        "peso_global": 0.0325,
        "regla": {
            "descripcion": (
                "Evita conflictos con asentamientos: buffer mínimo 500 m "
                "desde traza urbana de localidades >2 500 habitantes."
            ),
            "parametros_json": {
                "buffer_m": 500,
                "poblacion_umbral": 2500,
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.3",
            },
        },
    },
    {
        "id_criterio": "SOC_03",
        "nombre": "Vías de acceso",
        "bloque": "socioeconomico",
        "fuente": "SEDESOL NTE-CRM-001/90 / panel de expertos",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.1037,
        "peso_global": 0.0336,
        "regla": {
            "descripcion": (
                "Favorece sitios con conectividad suficiente. "
                "SEDESOL: distancia a vías de comunicación >200 m."
            ),
            "parametros_json": {
                "buffer_m": 200,
                "suitability": "piecewise_linear",
                "escala_factor": [0, 5],
                "antecedente": "SEDESOL (>200 m)",
            },
        },
    },
    {
        "id_criterio": "SOC_04",
        "nombre": "Uso de suelo (agavero, cañero, otro)",
        "bloque": "socioeconomico",
        "fuente": "Plan municipal / panel (Tabla 4.1)",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.0989,
        "peso_global": 0.0321,
        "regla": {
            "descripcion": (
                "Evalúa compatibilidad territorial; evita uso indebido de "
                "zonas agroproductivas estratégicas (agavero, cañero)."
            ),
            "parametros_json": {
                "suitability": "ordered_classes",
                "escala_factor": [0, 5],
                "clases_ejemplo": ["agavero", "canero", "otro"],
            },
        },
    },
    {
        "id_criterio": "SOC_05",
        "nombre": "Facilidad de compra del terreno",
        "bloque": "socioeconomico",
        "fuente": "Panel de expertos (parámetro de usuario)",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.1048,
        "peso_global": 0.0340,
        "regla": {
            "descripcion": (
                "Viabilidad de adquisición legal y costo. "
                "Sin capa pública: capturado por el usuario (tesis §1.6)."
            ),
            "parametros_json": {
                "suitability": "user_parameter",
                "escala_factor": [0, 5],
                "captura": "usuario",
            },
        },
    },
    {
        "id_criterio": "SOC_06",
        "nombre": "Zonas arqueológicas",
        "bloque": "socioeconomico",
        "fuente": "NOM-083-SEMARNAT-2003 §6.1.4 / INAH",
        "tipo_restriccion": "normativa",
        "activo": True,
        "peso_local": 0.1052,
        "peso_global": 0.0342,
        "regla": {
            "descripcion": "Excluye sitios con vestigios patrimoniales protegidos.",
            "parametros_json": {
                "suitability": "binary_exclusion",
                "norma": "NOM-083 §6.1.4",
            },
        },
    },
    {
        "id_criterio": "SOC_07",
        "nombre": "Vida útil del sitio",
        "bloque": "socioeconomico",
        "fuente": "SEDESOL NTE-CRM-001/90 / panel",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.1034,
        "peso_global": 0.0335,
        "regla": {
            "descripcion": (
                "Valora capacidad del sitio para periodo mínimo de operación. "
                "SEDESOL: vida útil mínima 7 años. Se calcula por polígono candidato."
            ),
            "parametros_json": {
                "suitability": "polygon_metric",
                "vida_util_min_anios": 7,
                "escala_factor": [0, 5],
                "fase": "poligono",
                "antecedente": "SEDESOL (mín. 7 años)",
            },
        },
    },
    {
        "id_criterio": "SOC_08",
        "nombre": "Disponibilidad de material de cobertura",
        "bloque": "socioeconomico",
        "fuente": "Panel de expertos / OPS-EPA antecedentes",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.0996,
        "peso_global": 0.0323,
        "regla": {
            "descripcion": (
                "Valora proximidad y accesibilidad de materiales para cobertura "
                "periódica de residuos."
            ),
            "parametros_json": {
                "suitability": "linear_decreasing_distance",
                "escala_factor": [0, 5],
            },
        },
    },
    {
        "id_criterio": "SOC_09",
        "nombre": "Cables de alta tensión (sistema eléctrico)",
        "bloque": "socioeconomico",
        "fuente": "SEDESOL NTE-CRM-001/90 / panel",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.0860,
        "peso_global": 0.0279,
        "regla": {
            "descripcion": (
                "Excluye zonas próximas a líneas de alta tensión por seguridad "
                "operativa (construcción y operación)."
            ),
            "parametros_json": {
                "suitability": "binary_exclusion",
                "buffer_m": 50,
                "origen_buffer": "literatura_operativa",
            },
        },
    },
    {
        "id_criterio": "SOC_10",
        "nombre": "Intermunicipalidad",
        "bloque": "socioeconomico",
        "fuente": "Panel de expertos (Tabla 4.1)",
        "tipo_restriccion": "modelo",
        "activo": True,
        "peso_local": 0.0934,
        "peso_global": 0.0303,
        "regla": {
            "descripcion": (
                "Favorece sitios que atiendan varios municipios. "
                "Se evalúa por polígono (distancia promedio ponderada)."
            ),
            "parametros_json": {
                "suitability": "polygon_metric",
                "escala_factor": [0, 5],
                "fase": "poligono",
            },
        },
    },
]

PESOS_LOCALES: dict[str, float] = {
    c["id_criterio"]: c["peso_local"] for c in CRITERIOS_SEED
}
PESOS_GLOBALES: dict[str, float] = {
    c["id_criterio"]: c["peso_global"] for c in CRITERIOS_SEED
}


def peso_global(id_criterio: str, bloque: str | None = None) -> float:
    return PESOS_GLOBALES[id_criterio]


assert len(CRITERIOS_SEED) == 21
assert sum(1 for c in CRITERIOS_SEED if c["bloque"] == "geohidrologico") == 7
assert sum(1 for c in CRITERIOS_SEED if c["bloque"] == "ecologico") == 4
assert sum(1 for c in CRITERIOS_SEED if c["bloque"] == "socioeconomico") == 10
assert abs(sum(BLOQUE_WEIGHTS.values()) - 1.0) < 1e-9
assert abs(sum(PESOS_GLOBALES.values()) - 1.0) < 1e-3  # tesis ~100%
for _b in ("geohidrologico", "ecologico", "socioeconomico"):
    assert abs(sum(c["peso_local"] for c in CRITERIOS_SEED if c["bloque"] == _b) - 1.0) < 1e-3
