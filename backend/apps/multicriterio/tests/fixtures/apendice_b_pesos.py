"""
Fixtures derivadas de pesos publicados del Apéndice B (tesis SADE).

Las matrices AHP crudas de los 15 expertos NO están en el extracto DOCX.
Aquí se documentan los pesos locales/globales oficiales y se construyen
matrices perfectamente consistentes a_ij = w_i/w_j para pruebas de
autovector / CR≈0. Los CR agregados reportados en la tesis se citan como
referencia (no se reproducen sin juicios crudos).

Fuente: tesis-sade-extracto.txt — Tablas B.3–B.6 / B.8.
"""
from __future__ import annotations

# Pesos de bloque (Tabla B.3)
BLOQUE_WEIGHTS = {
    "geohidrologico": 0.3654,
    "ecologico": 0.3101,
    "socioeconomico": 0.3245,
}

# CR de matrices agregadas AIJ (Tabla B.1 / narrativa)
CR_AGREGADA = {
    "criterios": 0.002,
    "geohidrologico": 0.0035,
    "ecologico": 0.0020,
    "socioeconomico": 0.0047,
}

# Diagnóstico individual Tabla B.2 (referencia documental)
PANEL_B2 = {
    "criterios": {"pct_inconsistentes": 0.87, "mediana_cr": 2.39},
    "geohidrologico": {"pct_inconsistentes": 0.93, "mediana_cr": 1.20},
    "ecologico": {"pct_inconsistentes": 0.67, "mediana_cr": 1.57},
    "socioeconomico": {"pct_inconsistentes": 0.80, "mediana_cr": 1.24},
}

# Pesos locales por bloque (suman ~1 dentro del bloque)
PESOS_LOCALES_GEO = [
    0.1412,  # GEO_01 recarga
    0.1495,  # GEO_02 inundación
    0.1444,  # GEO_03 fallas
    0.1533,  # GEO_04 deslizamiento
    0.1280,  # GEO_05 cavernas
    0.1374,  # GEO_06 aluviales
    0.1462,  # GEO_07 tipo de suelo
]

PESOS_LOCALES_ECO = [
    0.2824,  # ECO_01 agua superficial
    0.2407,  # ECO_02 pozos
    0.2473,  # ECO_03 ecosistemas
    0.2296,  # ECO_04 ANP
]

PESOS_LOCALES_SOC = [
    0.1049,  # SOC_01 aeródromo
    0.1002,  # SOC_02 localidades
    0.1037,  # SOC_03 vías
    0.0989,  # SOC_04 uso de suelo
    0.1048,  # SOC_05 facilidad compra
    0.1052,  # SOC_06 arqueológicas
    0.1034,  # SOC_07 vida útil
    0.0996,  # SOC_08 cobertura
    0.0860,  # SOC_09 alta tensión
    0.0934,  # SOC_10 intermunicipalidad
]

PESOS_GLOBALES_21 = [
    # GEO
    0.0516,
    0.0546,
    0.0528,
    0.0560,
    0.0468,
    0.0502,
    0.0534,
    # ECO
    0.0876,
    0.0747,
    0.0767,
    0.0712,
    # SOC
    0.0340,
    0.0325,
    0.0336,
    0.0321,
    0.0340,
    0.0342,
    0.0335,
    0.0323,
    0.0279,
    0.0303,
]

IDS_21 = [
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
    "SOC_01",
    "SOC_02",
    "SOC_03",
    "SOC_04",
    "SOC_05",
    "SOC_06",
    "SOC_07",
    "SOC_08",
    "SOC_09",
    "SOC_10",
]

assert len(PESOS_GLOBALES_21) == 21
assert abs(sum(PESOS_GLOBALES_21) - 1.0) < 1e-3
