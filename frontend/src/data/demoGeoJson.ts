import type { SadeFeatureCollection } from '../types/api'

/**
 * Malla demo en WGS84 sobre Valles de Jalisco (solo si no hay escenario/API).
 * 4×4 celdas ~Ameca–Tala con las 6 clases de aptitud.
 */
export const DEMO_GEOJSON: SadeFeatureCollection = {
  type: 'FeatureCollection',
  sade_audit: {
    escenario_id: 0,
    hash_configuracion: 'demo-local-sin-backend',
    hash_resultado: 'demo-local-sin-backend',
    crs: 'EPSG:4326',
  },
  features: (() => {
    const codes = [
      [0, 1, 1, 2],
      [1, 2, 3, 3],
      [2, 3, 4, 4],
      [3, 4, 5, 5],
    ]
    const west = -104.15
    const south = 20.45
    const cellW = 0.12
    const cellH = 0.1
    const features: SadeFeatureCollection['features'] = []
    const labels = [
      'Excluido',
      'No apto',
      'No recomendable',
      'Apto con restricciones',
      'Favorable',
      'Óptimo',
    ]
    for (let row = 0; row < 4; row++) {
      for (let col = 0; col < 4; col++) {
        const code = codes[row][col]
        const x0 = west + col * cellW
        const y0 = south + (3 - row) * cellH
        features.push({
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [
              [
                [x0, y0],
                [x0 + cellW, y0],
                [x0 + cellW, y0 + cellH],
                [x0, y0 + cellH],
                [x0, y0],
              ],
            ],
          },
          properties: {
            class_code: code,
            class_label: labels[code],
            suitability: code / 5,
            row,
            col,
          },
        })
      }
    }
    return features
  })(),
}
