/** Contratos alineados con backend PASO 4 (`/api/escenarios/`). */

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

export interface SadeGeoJsonProperties {
  class_code: number
  class_label: string
  suitability: number
  row?: number
  col?: number
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
