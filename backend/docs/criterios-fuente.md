# Criterios SADE — Tabla 4.1 y Apéndice B

Documento de trazabilidad de la semilla `load_initial_rules` respecto a la
**tesis SADE Valles de Jalisco** (`docs/tesis-sade-valles-jalisco.docx` en el
Project store; extractos en `internal/tesis-sade-extracto.txt`).

## Distribución (corregida: no es 7/7/7)

| Bloque | Cantidad | Peso de bloque (Apéndice B) | CR agregado (AIJ) |
|--------|----------|-----------------------------|-------------------|
| Geohidrológico | **7** | 36.54 % | 0.0035 |
| Ecológico | **4** | 31.01 % | 0.0020 |
| Socioeconómico | **10** | 32.45 % | 0.0047 |
| **Total** | **21** | 100 % | CR criterios principales = 0.002 |

Procedencia AHP: panel de **15 expertos**, encuesta 17-abr a 7-may-2026,
agregación **AIJ** (media geométrica con reconstrucción direccional).

## Catálogo de IDs

### Geohidrológicos (`GEO_01`–`GEO_07`)

| ID | Nombre | Fuente | Tipo | Peso local | Peso global | ¿Placeholder? |
|----|--------|--------|------|------------|-------------|---------------|
| GEO_01 | Zonas de recarga de acuíferos | NOM-083 §6.1.4 / SEDESOL | normativa | 14.12 % | 5.16 % | No (tesis) |
| GEO_02 | Zona de inundación | NOM-083 §6.1.5 | normativa | 14.95 % | 5.46 % | No |
| GEO_03 | Fracturas o fallas geológicas | NOM-083 §6.1.4 / SEDESOL | normativa | 14.44 % | 5.28 % | No |
| GEO_04 | Zonas de riesgo de deslizamiento | Antecedente / panel | modelo | 15.33 % | 5.60 % | No |
| GEO_05 | Cavernas | NOM-083 §6.1.4 | normativa | 12.80 % | 4.68 % | No |
| GEO_06 | Planicies aluviales | NOM-083 §6.1.4 | normativa | 13.74 % | 5.02 % | No |
| GEO_07 | Tipo de suelo | SEDESOL / geotécnico | modelo | 14.62 % | 5.34 % | No |

### Ecológicos (`ECO_01`–`ECO_04`)

| ID | Nombre | Fuente | Tipo | Peso local | Peso global | ¿Placeholder? |
|----|--------|--------|------|------------|-------------|---------------|
| ECO_01 | Cuerpos de agua superficial (500 m) | NOM-083 §6.1.6 | normativa | 28.24 % | 8.76 % | No |
| ECO_02 | Pozos de extracción (500 m) | NOM-083 §6.1.7 | normativa | 24.07 % | 7.47 % | No |
| ECO_03 | Ecosistemas acuáticos | NOM-083 §6.1.4 | normativa | 24.73 % | 7.67 % | No |
| ECO_04 | Áreas Naturales Protegidas | NOM-083 §6.1.2 | normativa | 22.96 % | 7.12 % | No |

### Socioeconómicos (`SOC_01`–`SOC_10`)

| ID | Nombre | Fuente | Tipo | Peso local | Peso global | ¿Placeholder? |
|----|--------|--------|------|------------|-------------|---------------|
| SOC_01 | Distancia a aeródromo (13 km) | NOM-083 §6.1.1 | **advertencia** | 10.49 % | 3.40 % | No |
| SOC_02 | Proximidad a localidades >2 500 hab. (500 m) | NOM-083 §6.1.3 | normativa | 10.02 % | 3.25 % | No |
| SOC_03 | Vías de acceso | SEDESOL / panel | modelo | 10.37 % | 3.36 % | No |
| SOC_04 | Uso de suelo (agavero, cañero, otro) | Panel / plan municipal | modelo | 9.89 % | 3.21 % | No |
| SOC_05 | Facilidad de compra del terreno | Panel (captura usuario) | modelo | 10.48 % | 3.40 % | Parámetro de usuario |
| SOC_06 | Zonas arqueológicas | NOM-083 §6.1.4 / INAH | normativa | 10.52 % | 3.42 % | No |
| SOC_07 | Vida útil del sitio | SEDESOL (≥7 años) / panel | modelo | 10.34 % | 3.35 % | Métrica por polígono |
| SOC_08 | Disponibilidad de material de cobertura | Panel / OPS-EPA | modelo | 9.96 % | 3.23 % | No |
| SOC_09 | Cables de alta tensión | SEDESOL / panel | modelo | 8.60 % | 2.79 % | Buffer operativo tipificado |
| SOC_10 | Intermunicipalidad | Panel | modelo | 9.34 % | 3.03 % | Métrica por polígono |

## Parámetros NOM-083 destacados en `parametros_json`

- **500 m**: cuerpos de agua (`ECO_01`), pozos respaldo (`ECO_02`), localidades (`SOC_02`)
- **13 km**: advertencia aeródromo (`SOC_01`)
- **SEDESOL**: recarga >1 km (`GEO_01`), fallas >500 m (`GEO_03`), vías >200 m (`SOC_03`), freático >10 m (`GEO_07`), vida útil ≥7 años (`SOC_07`)

## Pendiente respecto a la tesis

- Graduaciones finas 0–5 por criterio (algunas reglas de puntuación de la Tabla 4.1 no vienen numéricas en el extracto DOCX).
- Umbral exacto de buffer a líneas de alta tensión (tipificado 50 m).
- Escenarios de sensibilidad E0–E8 según Tabla 4.3 (detalle de cada perturbación).
- Matrices AHP crudas del Apéndice B (solo pesos/CR finales cargados).

## Carga

```bash
python manage.py load_initial_rules
```
