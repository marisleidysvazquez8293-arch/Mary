# SADE — Visor cartográfico (frontend)

Interfaz web del **Sistema de Apoyo a Decisiones Espaciales** para localización de rellenos sanitarios en **Valles de Jalisco**.

Consume la API Django+DRF (`/api/`) del backend en `backend/` (rama/PR de PASO 1–4).

## Stack y elección de mapa

| Pieza | Elección |
|-------|----------|
| Build | Vite + React 19 + TypeScript |
| Mapa | **Leaflet** (+ `react-leaflet`) |
| Base | OpenStreetMap |
| Capas de aptitud | GeoJSON del escenario (`GET /api/escenarios/{id}/geojson/`) |
| Reproyección | `proj4` (EPSG:32613 → WGS84 para OSM) |

**¿Por qué Leaflet y no OpenLayers?** Para el alcance v1 (OSM + una capa GeoJSON + leyenda + zoom a región) Leaflet es más ligero, con curva de adopción menor y suficiente. OpenLayers sería preferible si más adelante se necesitan proyecciones nativas complejas, WMS/WMTS multi-fuente o edición vectorial avanzada; el contrato TileJSON del backend ya anticipa esa evolución.

## Requisitos

- Node.js 20+ (probado con 22)
- Backend SADE corriendo en `http://127.0.0.1:8000` (opcional: el visor muestra una capa demo local si la API no responde)

## Instalación

```bash
cd frontend
npm install
cp .env.example .env   # editar credenciales si aplica
```

Variables relevantes (`.env`):

| Variable | Descripción |
|----------|-------------|
| `VITE_API_URL` | Base absoluta de la API. **Vacío** = rutas `/api/…` vía proxy de Vite |
| `VITE_PROXY_TARGET` | Destino del proxy en desarrollo (default `http://127.0.0.1:8000`) |
| `VITE_API_USER` / `VITE_API_PASSWORD` | Basic Auth (DRF exige usuario + rol SADE) |
| `VITE_DEMO_CONJUNTO_PESOS_ID` | ID de `ConjuntoPesosAHP` para «Ejecutar (demo)» (default `1`) |

## Levantar en desarrollo

Terminal 1 — backend:

```bash
cd backend
source .venv/bin/activate   # o el venv que use
python manage.py runserver
```

Terminal 2 — frontend:

```bash
cd frontend
npm run dev
```

Abrir **http://127.0.0.1:5173/**

El proxy de Vite reenvía `/api/*` → `VITE_PROXY_TARGET`.

## Uso de la UI

1. El mapa inicia centrado en **Valles de Jalisco** con leyenda de 6 clases.
2. **Actualizar** lista escenarios (`GET /api/escenarios/`).
3. Seleccionar un escenario → carga GeoJSON y hace zoom a la capa.
4. **Ejecutar (demo)** → `POST /api/escenarios/ejecutar/` con parámetros demo.
5. Panel **Trazabilidad**: `hash_configuracion`, `hash_resultado`, pesos y fecha; **Reejecutar** compara hashes.

Roles backend: ejecución requiere *Analista Territorial* o *Administrador Técnico*; lectura GeoJSON también *Auditor*.

## Build de producción

```bash
cd frontend
npm run build
npm run preview
```

En producción configure `VITE_API_URL` hacia el origen del API (y CORS/sesión en Django si no usa el mismo host).

## Estructura

```
frontend/
  src/
    api/client.ts          # Cliente HTTP
    components/            # Panel, mapa, leyenda
    constants/             # Clases de aptitud + región
    data/demoGeoJson.ts    # Capa demo offline
    utils/reproject.ts     # EPSG:32613 → 4326
    App.tsx
```


## PASO 4 — componentes del visor

| Componente | Rol |
|------------|-----|
| `MapViewer` | OSM + capa exclusión + aptitud reclasificada (Leaflet); clic → consulta |
| `ConsultaCelda` | Desglose de 21 factores, restricciones y advertencia aeródromo |
| `GestorEscenarios` | Versión de reglas, pesos AHP, ejecutar, sensibilidad, PDF/ZIP |

### Endpoints consumidos / previstos

| Método | Path | Estado en UI |
|--------|------|--------------|
| POST | `/api/escenarios/ejecutar/` | Activo |
| POST | `/api/escenarios/sensibilidad/` | Activo |
| GET | `/api/escenarios/{id}/mapa/` | Activo (fallback `/geojson/`) |
| GET | `/api/escenarios/{id}/celda/?lat=&lon=` | **TODO** backend → mock demo |
| GET | `/api/escenarios/{id}/expediente.pdf` | **TODO** → descarga marcador |
| GET | `/api/escenarios/{id}/reproducibilidad.zip` | **TODO** → descarga marcador |

Cuando exista `/cursor/stores/self/internal/sade-paso4-api-contrato.md`, alinear paths/params.

## Docker

```bash
cd frontend
docker build -t sade-frontend .
docker run --rm -p 8080:80 sade-frontend
```
