import type { FeatureCollection, Polygon } from 'geojson'

/** Polígonos candidatos demo (Favorable/Óptimo) — Valles de Jalisco. */
export const DEMO_CANDIDATOS: FeatureCollection<Polygon> = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: {
        candidate_id: 'C-01',
        class_label: 'Óptimo',
        area_ha: 42.5,
        suitability: 4.7,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-103.95, 20.72],
            [-103.88, 20.72],
            [-103.88, 20.78],
            [-103.95, 20.78],
            [-103.95, 20.72],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        candidate_id: 'C-02',
        class_label: 'Favorable',
        area_ha: 28.1,
        suitability: 4.1,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-104.05, 20.58],
            [-103.98, 20.58],
            [-103.98, 20.64],
            [-104.05, 20.64],
            [-104.05, 20.58],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        candidate_id: 'C-03',
        class_label: 'Favorable',
        area_ha: 35.0,
        suitability: 3.9,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-103.82, 20.55],
            [-103.76, 20.55],
            [-103.76, 20.6],
            [-103.82, 20.6],
            [-103.82, 20.55],
          ],
        ],
      },
    },
  ],
}
