/**
 * Cliente GEE — contrato `internal/sade-gee-api-contrato.md`
 * Paths: /api/gee/status|capas|capas/{id}/tiles|consulta-celda
 */

import { buildMockCelda } from '../data/mockCelda'
import type { ConsultaCeldaResponse, FactorCelda } from '../types/api'

function apiBase(): string {
  const raw = import.meta.env.VITE_API_URL as string | undefined
  if (!raw || raw.trim() === '') return ''
  return raw.replace(/\/$/, '')
}

function authHeaders(): HeadersInit {
  const user = import.meta.env.VITE_API_USER as string | undefined
  const pass = import.meta.env.VITE_API_PASSWORD as string | undefined
  if (!user || !pass) return {}
  return { Authorization: `Basic ${btoa(`${user}:${pass}`)}` }
}

async function geeRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(init?.headers ?? {}),
    },
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = (await res.json()) as { detail?: unknown }
      if (body.detail != null) {
        detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
      }
    } catch {
      /* ignore */
    }
    throw new Error(`GEE API ${res.status}: ${detail}`)
  }
  return (await res.json()) as T
}

export interface GeeStatus {
  mode: 'ready' | 'degraded' | string
  available?: boolean
  message?: string
  crs_gee?: string
  crs_analisis?: string
  roi_bbox_4326?: [number, number, number, number]
  gee?: {
    mode?: string
    available?: boolean
    message?: string
  }
}

export interface GeeCapa {
  id: string
  nombre: string
  tile_url_template: string | null
  degraded?: boolean
  coleccion?: string
  descripcion?: string
}

export interface GeeCapasResponse {
  crs_gee: string
  crs_analisis: string
  roi_bbox_4326: [number, number, number, number]
  gee: { mode: string; available: boolean; message?: string }
  capas: GeeCapa[]
}

export interface GeeTilesResponse {
  layer_id: string
  mapid?: string
  token?: string
  tile_url_template: string | null
  degraded?: boolean
  message?: string
}

export interface GeeConsultaCeldaRaw {
  fuente?: string
  coordenadas?: { lon: number; lat: number }
  gee?: {
    valores?: Record<string, unknown>
    degraded?: boolean
  }
  suitability_S?: number
  clase?: { code: number; label: string }
  factores?: FactorCelda[]
  restricciones_nom083?: Array<string | Record<string, unknown>>
  advertencias?: Array<string | { id_criterio?: string; message?: string }>
  row?: number
  col?: number
}

const MOCK_CAPAS: GeeCapa[] = [
  { id: 'dem_srtm', nombre: 'DEM SRTM (mock)', tile_url_template: null, degraded: true },
  { id: 'pendiente_srtm', nombre: 'Pendiente SRTM (mock)', tile_url_template: null, degraded: true },
  { id: 'sentinel2_ndvi', nombre: 'Sentinel-2 NDVI (mock)', tile_url_template: null, degraded: true },
  { id: 'landsat8_rgb', nombre: 'Landsat 8 RGB (mock)', tile_url_template: null, degraded: true },
  { id: 'gsw_occurrence', nombre: 'GSW occurrence (mock)', tile_url_template: null, degraded: true },
]

/** GET /api/gee/status/ (sin auth). */
export async function fetchGeeStatus(): Promise<GeeStatus & { fuente: 'api' | 'mock'; mock_motivo?: string }> {
  try {
    const data = await geeRequest<GeeStatus>('/api/gee/status/')
    return { ...data, fuente: 'api' }
  } catch (err) {
    return {
      mode: 'degraded',
      available: false,
      message: err instanceof Error ? err.message : 'status falló',
      fuente: 'mock',
      mock_motivo: err instanceof Error ? err.message : 'GEE status no disponible',
      crs_gee: 'EPSG:4326',
      crs_analisis: 'EPSG:32613',
      roi_bbox_4326: [-104.55, 20.25, -103.45, 21.15],
    }
  }
}

/**
 * GET /api/gee/capas/?tiles=1
 * Si mode degraded o error → catálogo mock sin TileURL.
 */
export async function fetchGeeCapas(options?: {
  forceMock?: boolean
}): Promise<GeeCapasResponse & { fuente: 'api' | 'mock'; mock_motivo?: string }> {
  if (options?.forceMock) {
    return {
      crs_gee: 'EPSG:4326',
      crs_analisis: 'EPSG:32613',
      roi_bbox_4326: [-104.55, 20.25, -103.45, 21.15],
      gee: { mode: 'degraded', available: false, message: 'Forzado mock' },
      capas: MOCK_CAPAS,
      fuente: 'mock',
      mock_motivo: 'status degradado o forzado',
    }
  }
  try {
    const data = await geeRequest<GeeCapasResponse>('/api/gee/capas/?tiles=1')
    const mode = data.gee?.mode ?? 'degraded'
    if (mode === 'degraded' || data.gee?.available === false) {
      return {
        ...data,
        fuente: 'mock',
        mock_motivo:
          data.gee?.message ??
          'GEE en modo degraded — sin tiles reales; catálogo API conservado',
      }
    }
    return { ...data, fuente: 'api' }
  } catch (err) {
    return {
      crs_gee: 'EPSG:4326',
      crs_analisis: 'EPSG:32613',
      roi_bbox_4326: [-104.55, 20.25, -103.45, 21.15],
      gee: {
        mode: 'degraded',
        available: false,
        message: err instanceof Error ? err.message : 'capas falló',
      },
      capas: MOCK_CAPAS,
      fuente: 'mock',
      mock_motivo: err instanceof Error ? err.message : 'GEE capas no disponible',
    }
  }
}

/** GET /api/gee/capas/{layer_id}/tiles/ */
export async function fetchGeeLayerTiles(layerId: string): Promise<GeeTilesResponse> {
  try {
    return await geeRequest<GeeTilesResponse>(
      `/api/gee/capas/${encodeURIComponent(layerId)}/tiles/`,
    )
  } catch (err) {
    return {
      layer_id: layerId,
      tile_url_template: null,
      degraded: true,
      message: err instanceof Error ? err.message : 'tiles no disponible',
    }
  }
}

function mapAdvertencias(
  items: GeeConsultaCeldaRaw['advertencias'],
): string[] {
  return (items ?? []).map((a) =>
    typeof a === 'string' ? a : a.message ?? JSON.stringify(a),
  )
}

function mapRestricciones(
  items: GeeConsultaCeldaRaw['restricciones_nom083'],
): string[] {
  return (items ?? []).map((r) =>
    typeof r === 'string' ? r : JSON.stringify(r),
  )
}

/**
 * GET/POST /api/gee/consulta-celda/
 * Normaliza a ConsultaCeldaResponse para el Inspector.
 */
export async function fetchGeeConsultaCelda(params: {
  lat: number
  lon: number
  escenario_id?: number
}): Promise<ConsultaCeldaResponse> {
  const q = new URLSearchParams({
    lat: String(params.lat),
    lon: String(params.lon),
  })
  if (params.escenario_id != null && params.escenario_id > 0) {
    q.set('escenario_id', String(params.escenario_id))
  }
  try {
    const raw = await geeRequest<GeeConsultaCeldaRaw>(
      `/api/gee/consulta-celda/?${q.toString()}`,
    )
    const code = raw.clase?.code ?? 0
    const label = raw.clase?.label ?? String(code)
    const advertencias = mapAdvertencias(raw.advertencias)
    const aero = advertencias.find((a) =>
      /aeródromo|aviario|13\s*km/i.test(a),
    )
    return {
      escenario_id: params.escenario_id,
      lat: raw.coordenadas?.lat ?? params.lat,
      lon: raw.coordenadas?.lon ?? params.lon,
      row: raw.row,
      col: raw.col,
      class_code: code,
      class_label: label,
      suitability: raw.suitability_S ?? 0,
      excluido: code === 0,
      factores: raw.factores ?? [],
      restricciones: mapRestricciones(raw.restricciones_nom083),
      advertencias,
      advertencia_aerodromo: aero
        ? { aplica: true, mensaje: aero }
        : undefined,
      fuente: 'api',
    }
  } catch (err) {
    const motivo = err instanceof Error ? err.message : 'consulta-celda GEE falló'
    const mock = buildMockCelda(params.escenario_id ?? 0, params.lat, params.lon)
    return {
      ...mock,
      mock_motivo: `GET /api/gee/consulta-celda/ falló: ${motivo}`,
    }
  }
}
