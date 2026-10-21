# SADE v1.0 — Backend (Django GIS)

Sistema Inteligente de Apoyo a la Toma de Decisiones Espacial — siting de rellenos sanitarios en **Valles de Jalisco**.

This Django project lives under `backend/` alongside the existing CodeIgniter PHP app at the repository root. The PHP app is left untouched; SADE v1.0 starts here.

## Stack

| Component | Version / note |
|-----------|----------------|
| Django | 4.2+ (tested with 5.0.x) |
| Django REST Framework | for future API (PASO 2+) |
| PostgreSQL | 15 |
| PostGIS | required (`django.contrib.gis`) |
| CRS | **EPSG:32613** (UTM Zone 13N) for spatial analysis |

## Apps (`backend/apps/`)

| App | PASO 1 |
|-----|--------|
| `adquisicion` | `CapaGeoespacial` |
| `reglas` | `Criterio`, `Regla` |
| `multicriterio` | `ConjuntoPesosAHP`, `PesoCriterio` |
| `escenarios` | `Escenario` |
| `visualizacion` | stub only |
| `usuarios` | stub only |

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# System packages: PostgreSQL 15 + PostGIS, GDAL, GEOS
export POSTGRES_DB=sade POSTGRES_USER=sade POSTGRES_PASSWORD=sade
export POSTGRES_HOST=localhost POSTGRES_PORT=5432

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Admin: http://127.0.0.1:8000/admin/

## PASO 2 — seed data

```bash
python manage.py migrate
python manage.py load_initial_rules          # idempotent
python manage.py load_initial_rules --dry-run
```

Loads **21 criterios** + default `Regla` v1.0.0 and one `ConjuntoPesosAHP`
(Apéndice B block weights: GEO 36.54%, ECO 31.01%, SOC 32.45%).

**Placeholder pending thesis PDF:** Tabla 4.1 / Apéndice B text is not in the
repo. Seed ids are NOM-083-aligned placeholders:

`GEO_01`–`GEO_07`, `ECO_01`–`ECO_07`, `SOC_01`–`SOC_07`

Notable NOM-083 parameters in `parametros_json`: 500 m water/wells/urban,
aerodrome warning &lt;13 km (`SOC_02`). CR fields are `0.0` until AHPService.

Data module: `apps/reglas/data/initial_rules.py`

## PASO 3 — engine services

| Service | Module | Role |
|---------|--------|------|
| `ReglasEngineService` | `apps/reglas/services.py` | Exclusion mask ∏ c_j, 500 m buffers, aerodrome warnings |
| `AHPService` | `apps/multicriterio/services.py` | Eigenvector, CR=IC/IA, AIJ geometric mean |
| `CLPService` | `apps/multicriterio/services.py` | S=(∑ w·x)·∏c, 6-class reclass, candidate stubs |

### Tests (no PostGIS required)

```bash
cd backend
pip install -r requirements.txt

# Recommended (sqlite test settings):
DJANGO_SETTINGS_MODULE=config.settings_test python manage.py test \
  apps.multicriterio.tests apps.reglas.tests -v2

# Or pure unittest discovery:
PYTHONPATH=. python -m unittest discover -s apps -p 'test_*.py' -v
```

## Out of scope (through PASO 3)

- PASO 4: DRF endpoints / serializers
- GeometryField footprints; full shapely/rasterio/GEE backends (stubs only)
- Full VIS / RBAC models
