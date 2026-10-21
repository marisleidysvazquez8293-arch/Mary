/**
 * Contrato GEE previsto: `/cursor/stores/self/internal/sade-gee-api-contrato.md`
 * (aún no publicado). Paths tentativos + mock TileURL.
 */

export interface GeeLayerSpec {
  id: 'exclusion' | 'aptitud' | 'candidatos'
  nombre: string
  /** Plantilla XYZ o URL de tiles GEE. */
  tileUrl: string | null
  opacity: number
  disponible: boolean
  mensaje?: string
}

export interface GeeMapContract {
  escenario_id: number
  crs: string
  layers: GeeLayerSpec[]
  fuente: 'api' | 'mock'
  mock_motivo?: string
}

/** GET tentativo /api/escenarios/{id}/gee-tiles/ — mock si falla. */
export async function fetchGeeLayers(escenarioId: number): Promise<GeeMapContract> {
  const base = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ?? ''
  try {
    const user = import.meta.env.VITE_API_USER as string | undefined
    const pass = import.meta.env.VITE_API_PASSWORD as string | undefined
    const headers: HeadersInit = { Accept: 'application/json' }
    if (user && pass) headers.Authorization = `Basic ${btoa(`${user}:${pass}`)}`
    const res = await fetch(`${base}/api/escenarios/${escenarioId}/gee-tiles/`, { headers })
    if (!res.ok) throw new Error(`API ${res.status}`)
    const data = (await res.json()) as GeeMapContract
    return { ...data, fuente: data.fuente ?? 'api' }
  } catch (err) {
    const motivo = err instanceof Error ? err.message : 'GEE no disponible'
    return {
      escenario_id: escenarioId,
      crs: 'EPSG:3857',
      fuente: 'mock',
      mock_motivo: `${motivo}. TODO: alinear a sade-gee-api-contrato.md`,
      layers: [
        {
          id: 'exclusion',
          nombre: 'Exclusión (GEE)',
          tileUrl: null,
          opacity: 0.55,
          disponible: false,
          mensaje: 'Sin TileURL GEE — use capa GeoJSON local',
        },
        {
          id: 'aptitud',
          nombre: 'Aptitud 6 clases (GEE)',
          tileUrl: null,
          opacity: 0.7,
          disponible: false,
          mensaje: 'Sin TileURL GEE — use capa GeoJSON local',
        },
        {
          id: 'candidatos',
          nombre: 'Polígonos candidatos',
          tileUrl: null,
          opacity: 0.8,
          disponible: false,
          mensaje: 'Capa candidata pendiente de contrato GEE',
        },
      ],
    }
  }
}
