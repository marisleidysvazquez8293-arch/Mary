/** Contratos PASO 4 — alineados al backend actual + TODOs de endpoints previstos. */

export interface Escenario {
  id: number
  nombre: string
  version_reglas_usada: string
  conjunto_pesos: number
  conjunto_pesos_nombre: string
  hash_configuracion: string
  hash_resultado: string
  fecha_ejecucion: string | null
  parametros_ejecucion: Record<string, unknown>
  resultados_json: Record<string, unknown>
  created?: boolean
  resumen_superficies?: Record<string, number>
}

export interface EjecutarPayload {
  nombre: string
  version_reglas_usada?: string
  conjunto_pesos_id: number
  parametros_ejecucion?: Record<string, unknown>
  weights_from_db?: boolean
}

export interface ReejecutarResponse {
  escenario: Escenario
  hash_configuracion: string
  hash_resultado_anterior: string
  hash_resultado_nuevo: string
  config_unchanged: boolean
  resultado_reproducido: boolean
}

export interface SensibilidadPayload {
  version_reglas_usada?: string
  conjunto_pesos_id: number
  parametros_ejecucion?: Record<string, unknown>
  persist?: boolean
}

export interface SensibilidadReport {
  baseline_id: string
  notes: string | string[]
  experiments: Array<Record<string, unknown>>
  pairwise_jaccard: Array<{
    scenario_a: string
    scenario_b: string
    jaccard: number
    intersection_cells: number
    union_cells: number
  }>
}

export interface SadeGeoJsonProperties {
  class_code: number
  class_label: string
  suitability: number
  row?: number
  col?: number
  excluded?: boolean
}

export interface SadeFeatureCollection {
  type: 'FeatureCollection'
  features: GeoJSON.Feature<GeoJSON.Polygon | GeoJSON.MultiPolygon, SadeGeoJsonProperties>[]
  sade_audit?: {
    escenario_id: number
    hash_configuracion: string
    hash_resultado: string
    crs: string
  }
}

export interface TileJsonStub {
  tilejson: string
  name?: string
  description?: string
  sade?: {
    status: string
    geojson?: string
  }
}

/** GET /api/escenarios/{id}/mapa/ */
export interface MapaResponse {
  formato: string
  crs: string
  geojson: SadeFeatureCollection
  tilejson?: TileJsonStub
  endpoints?: Record<string, string>
}

export interface FactorCelda {
  id_criterio: string
  nombre: string
  bloque: string
  /** Factor xᵢ en escala 0–5 (o 0–1 según motor). */
  valor_factor: number
  peso: number
  contribucion: number
  restriccion_activa: boolean
  /** Mensaje de regla aplicada. */
  detalle?: string
}

/**
 * GET /api/escenarios/{id}/celda/?lat=&lon=
 * TODO: confirmar query params exactos cuando exista
 * `/cursor/stores/self/internal/sade-paso4-api-contrato.md`
 */
export interface ConsultaCeldaResponse {
  escenario_id: number
  lat: number
  lon: number
  class_code: number
  class_label: string
  suitability: number
  excluido: boolean
  factores: FactorCelda[]
  restricciones: string[]
  advertencias: string[]
  /** NOM-083 6.1.1 — no excluye, solo advierte. */
  advertencia_aerodromo?: {
    aplica: boolean
    distancia_km?: number
    mensaje: string
  }
  fuente?: 'api' | 'mock'
}

export interface ConjuntoPesosOption {
  id: number
  nombre: string
  descripcion?: string
}
