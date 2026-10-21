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

## Out of scope (PASO 1)

- `load_initial_rules`, domain services, DRF views/serializers
- GeometryField footprints (metadata SRID is ready; GIS fields later)
- Full VIS / RBAC models
