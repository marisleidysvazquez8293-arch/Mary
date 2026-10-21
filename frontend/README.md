# SADE — SPA frontend

Interfaz React + Tailwind + Leaflet del **Sistema de Apoyo a Decisiones Espaciales** (rellenos sanitarios, Valles de Jalisco).

## Pantallas (React Router)

| Ruta | RF/RI | Contenido |
|------|-------|-----------|
| `/` | RF-044 | Visor fullscreen OSM + exclusión/aptitud + inspector de celda; capas GEE (mock si no hay contrato) |
| `/reglas` | RI-003 | Motor de reglas — 21 criterios, umbrales, buffers NOM-083 bloqueados |
| `/ahp` | RI-004 | Pesos Apéndice B, matrices 1/9–9, alerta CR ≥ 0.10 |
| `/escenarios` | RI-005 | Ejecutar, sensibilidad E0–E8, gráfico Jaccard, celdas estables |
| `/expediente` | RF-039/046 | PDF + ZIP + leyenda legal |

## Stack

Vite · React 19 · TypeScript · Tailwind CSS v4 · React Router · Leaflet · Recharts

**Leaflet** (no OpenLayers): suficiente para OSM + GeoJSON + clics; GEE entra como TileURL cuando exista `sade-gee-api-contrato.md`.

## Instalación

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

http://127.0.0.1:5173/

## API (PASO 4)

Contrato: `internal/sade-paso4-api-contrato.md`

| Path | Uso |
|------|-----|
| `POST /api/escenarios/ejecutar/` | Ejecutar |
| `POST /api/escenarios/sensibilidad/` | E0–E8 |
| `GET/POST …/hash/` | Trazabilidad |
| `GET …/mapa/` | Capas mapa |
| `GET …/consulta-celda/` | Inspector |
| `GET …/pdf/` | Expediente |
| `GET …/reproducibilidad/` | ZIP |

Si la API/GEE falla: **mocks con mensaje claro**.

## Docker

```bash
cd frontend
docker build -t sade-frontend .
docker run --rm -p 8080:80 sade-frontend
```
