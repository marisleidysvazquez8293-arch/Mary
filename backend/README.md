# SADE v1.0 — Backend (Django GIS)

Sistema Inteligente de Apoyo a la Toma de Decisiones Espacial — localización de rellenos sanitarios en **Valles de Jalisco**.

Proyecto Django bajo `backend/` junto a la app CodeIgniter PHP (sin modificar).

## Stack

| Componente | Nota |
|------------|------|
| Django | 4.2+ (probado con 5.0.x) |
| Django REST Framework | `/api/` (PASO 3–4 + GEE) |
| PostgreSQL / PostGIS | 15 — GIS de producción |
| CRS análisis | **EPSG:32613** (UTM 13N) |
| CRS GEE / visor | **EPSG:4326** |
| numpy / ReportLab | motores + PDF |
| earthengine-api | Google Earth Engine (modo degradado sin credenciales) |

## Apps (`backend/apps/`)

| App | Rol |
|-----|------|
| `adquisicion` | `CapaGeoespacial` + **GeeService** |
| `reglas` | `Criterio`, `Regla`, `RulesEngineService` |
| `multicriterio` | AHP / CLP + pesos |
| `escenarios` | ejecución, sensibilidad, ZIP |
| `visualizacion` | PDF expediente |
| `usuarios` | RBAC (Groups) |

## Google Earth Engine

Sin credenciales el backend **arranca igual** (`GET /api/gee/status/` → `mode: "degraded"`).

```bash
# 1) Crear cuenta de servicio en GCP y registrar en Earth Engine
# 2) Copiar backend/.env.example → backend/.env y configurar UNA opción:

# Opción A
export GOOGLE_APPLICATION_CREDENTIALS=/ruta/sade-gee-sa.json

# Opción B
export GEE_SERVICE_ACCOUNT=sade-gee@PROYECTO.iam.gserviceaccount.com
export GEE_PRIVATE_KEY_PATH=/ruta/sade-gee-sa.json

# Opcional
export GEE_PROJECT=tu-proyecto-gcp

pip install -r requirements.txt   # incluye earthengine-api
```

API GEE:

| Método | Path |
|--------|------|
| GET | `/api/gee/status/` |
| GET | `/api/gee/capas/` |
| GET | `/api/gee/capas/{id}/tiles/` |
| GET/POST | `/api/gee/consulta-celda/` |

Capas: `dem_srtm`, `pendiente_srtm`, `sentinel2_ndvi`, `landsat8_rgb`, `gsw_occurrence`.

Contrato: store `internal/sade-gee-api-contrato.md`.

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Production DB: PostgreSQL 15 + PostGIS, GDAL, GEOS
export POSTGRES_DB=sade POSTGRES_USER=sade POSTGRES_PASSWORD=sade
export POSTGRES_HOST=localhost POSTGRES_PORT=5432

python manage.py migrate
python manage.py load_initial_rules
python manage.py createsuperuser
python manage.py runserver
```

Admin: http://127.0.0.1:8000/admin/

## PASO 2 — semilla Tabla 4.1 / Apéndice B (tesis)

```bash
python manage.py load_initial_rules          # idempotente
python manage.py load_initial_rules --dry-run
```

**21 criterios reales de la tesis** (corregido: **GEO×7, ECO×4, SOC×10**, no 7/7/7):

- Pesos de bloque: GEO **36.54%**, ECO **31.01%**, SOC **32.45%**
- CR AIJ: geo **0.0035**, eco **0.0020**, socio **0.0047**
- Catálogo y fuentes: [`docs/criterios-fuente.md`](docs/criterios-fuente.md)

## PASO 3 — engine services

| Service | Module |
|---------|--------|
| `RulesEngineService` (alias `ReglasEngineService`) | `apps/reglas/services/rules_engine.py` |
| `AHPService` | `apps/multicriterio/services/ahp_service.py` |
| `CLPService` | `apps/multicriterio/services/clp_service.py` |

Import estable:

```python
from apps.reglas.services import RulesEngineService
from apps.multicriterio.services import AHPService, CLPService
```

API mapa: `GET /api/escenarios/{id}/mapa/` (GeoJSON + TileJSON).

`AHPService` implementa reconstrucción `a_ij = v_ij/v_ji`, AIJ, autovector,
IC/CR y diagnóstico de panel (CR individual, mediana, % ≥ 0.10).

## Docker (raíz del repo)

```bash
docker compose up --build
# backend http://localhost:8000  ·  frontend http://localhost:3000  ·  PostGIS :5432
```

El servicio `frontend` apunta a `./frontend` (placeholder hasta merge de la UI).

## PASO 4 — REST API, sensibilidad Tabla 4.3, PDF, ZIP

Servicios: `apps/escenarios/services/` (`ScenarioTraceabilityService`,
`SensitivityService`, `EscenarioExecutionService`) y
`apps/visualizacion/services/pdf_service.py`.

Base path: **`/api/`**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health/` | Smoke check (no auth) |
| GET | `/api/escenarios/` | List escenarios |
| GET | `/api/escenarios/{id}/` | Detail |
| POST | `/api/escenarios/ejecutar/` | Run Reglas+CLP; persist hashes |
| POST | `/api/escenarios/{id}/reejecutar/` | Re-run; compare `hash_resultado` |
| POST | `/api/escenarios/sensibilidad/` | Tabla 4.3 E0–E8 + Jaccard Favorable+Óptimo |
| GET/POST | `/api/escenarios/{id}/hash/` | Hash config + trazabilidad SHA-256 |
| GET | `/api/escenarios/{id}/reproducibilidad/` | ZIP RNF-002 / RF-039 |
| GET | `/api/escenarios/{id}/pdf/` | Expediente PDF (leyenda legal) |
| GET | `/api/escenarios/{id}/consulta-celda/` | 21 factores / restricciones / advertencias |
| GET | `/api/escenarios/{id}/geojson/` | Class cell polygons (EPSG:32613 grid) |
| GET | `/api/escenarios/{id}/tilejson/` | TileJSON stub → points at GeoJSON |
| GET | `/api/escenarios/{id}/mapa/` | GeoJSON + TileJSON unificados |
| GET | `/api/escenarios/{id}/tiles/{z}/{x}/{y}.png` | Tile stub (**501**) |

### Try it (session auth / browsable API)

```bash
# 1) migrate + seed + superuser, then runserver
python manage.py runserver

# 2) In another shell (Basic auth example):
curl -u admin:PASSWORD http://127.0.0.1:8000/api/health/

# Assign Django Groups named exactly:
#   "Administrador Técnico" | "Analista Territorial" | "Auditor"

# Execute (Analista / Admin Técnico):
curl -u analista:PASSWORD -H 'Content-Type: application/json' \
  -d '{
    "nombre": "Demo E0",
    "version_reglas_usada": "1.0.0",
    "conjunto_pesos_id": 1,
    "parametros_ejecucion": {
      "demo_seed": 42,
      "shape": [8, 8],
      "weights": [0.4, 0.3, 0.3]
    },
    "weights_from_db": false
  }' \
  http://127.0.0.1:8000/api/escenarios/ejecutar/

# Re-execute:
curl -u analista:PASSWORD -X POST \
  http://127.0.0.1:8000/api/escenarios/1/reejecutar/

# Sensitivity E0–E8:
curl -u analista:PASSWORD -H 'Content-Type: application/json' \
  -d '{"conjunto_pesos_id": 1, "parametros_ejecucion": {"demo_seed": 42, "weights": [0.4, 0.3, 0.3]}}' \
  http://127.0.0.1:8000/api/escenarios/sensibilidad/

# Maps:
curl -u auditor:PASSWORD http://127.0.0.1:8000/api/escenarios/1/geojson/
curl -u auditor:PASSWORD http://127.0.0.1:8000/api/escenarios/1/tilejson/
```

Without live GIS layers, `parametros_ejecucion` uses **deterministic demo rasters**
(`demo_seed` / `shape` / `weights`) so executions are repeatable in CI.

### Hash scheme (audit)

Implemented in `apps/escenarios/hashing.py`:

- **`hash_configuracion`** — SHA-256 of canonical JSON  
  `{version_reglas_usada, conjunto_pesos_id, parametros_ejecucion}`  
  (keys sorted, compact separators). Same config → same hash; execute is
  idempotent on this key.

- **`hash_resultado`** — SHA-256 of canonical JSON of persisted
  `resultados_json` (class maps, counts, geojson, candidates, …).

Re-execute reports `resultado_reproducido` when the new result hash matches
the previous one (bit-stable pipeline for the same config).

### RBAC (thin)

Django `Group.name` values (`apps/usuarios/roles.py`):

| Role | execute / reejecutar | sensibilidad / map / audit |
|------|----------------------|----------------------------|
| Administrador Técnico | ✓ | ✓ |
| Analista Territorial | ✓ | ✓ |
| Auditor | ✗ | ✓ |

Permissions: `apps/usuarios/permissions.py`.

## Tests (no PostGIS required)

```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings_test python manage.py test \
  apps.escenarios.tests apps.multicriterio.tests apps.reglas.tests -v2
```

## Remaining / deferred

- Real XYZ/COG tiling (TileJSON currently stubs with HTTP 501 on tile URLs)
- shapely dissolve of class polygons; GEE live hooks
- Full custom Usuario model (Groups are enough for v1)
