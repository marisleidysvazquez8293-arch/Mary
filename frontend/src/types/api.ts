/** Contratos PASO 4 — alineados a `internal/sade-paso4-api-contrato.md`. */

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

/** POST /api/escenarios/sensibilidad/ */
export interface SensibilidadPayload {
  version_reglas_usada?: string
  conjunto_pesos_id: number
  escenario_base_id?: number
  parametros_ejecucion?: Record<string, unknown>
  persist?: boolean
}

export interface SensibilidadReport {
  baseline_id: string
  notes: string | string[]
  experiments: Array<Record<string, unknown>>
  jaccard_vs_e0?: Array<Record<string, unknown>>
  zonas_estables_favorable_optimo?: unknown
  pairwise_jaccard: Array<{
    scenario_a: string
    scenario_b: string
    jaccard: number
    intersection_cells: number
    union_cells: number
  }>
}

/** GET|POST /api/escenarios/{id}/hash/ */
export interface HashResponse {
  hash_configuracion: string
  hash_trazabilidad: string
  hash_resultado: string
  coincide_persistido: boolean
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
  nombre?: string
  bloque?: string
  valor_factor: number
  peso: number
  contribucion?: number
  restriccion_activa?: boolean
  umbrales?: Record<string, unknown>
  detalle?: string
}

/**
 * GET /api/escenarios/{id}/consulta-celda/
 * Query: lat+lon | x+y (EPSG:32613) | row+col
 */
export interface ConsultaCeldaResponse {
  escenario_id?: number
  lat?: number
  lon?: number
  row?: number
  col?: number
  class_code: number
  class_label: string
  suitability: number
  excluido?: boolean
  factores: FactorCelda[]
  restricciones: string[] | Array<Record<string, unknown>>
  advertencias: string[] | Array<Record<string, unknown>>
  advertencia_aerodromo?: {
    aplica: boolean
    distancia_km?: number
    mensaje: string
  }
  fuente?: 'api' | 'mock'
  /** Motivo del fallback mock (si aplica). */
  mock_motivo?: string
}

export interface ConjuntoPesosOption {
  id: number
  nombre: string
  descripcion?: string
}

export type ConsultaCeldaQuery =
  | { lat: number; lon: number }
  | { row: number; col: number }
  | { x: number; y: number }
