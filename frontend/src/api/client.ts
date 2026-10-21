import { buildMockCelda } from '../data/mockCelda'
import type {
  ConsultaCeldaQuery,
  ConsultaCeldaResponse,
  Escenario,
  EjecutarPayload,
  HashResponse,
  MapaResponse,
  ReejecutarResponse,
  SadeFeatureCollection,
  SensibilidadPayload,
  SensibilidadReport,
  TileJsonStub,
} from '../types/api'

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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${apiBase()}${path}`
  const res = await fetch(url, {
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
    throw new Error(`API ${res.status}: ${detail}`)
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

async function requestBlob(
  path: string,
  accept: string,
): Promise<Blob> {
  const url = `${apiBase()}${path}`
  const res = await fetch(url, {
    headers: { ...authHeaders(), Accept: accept },
  })
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`)
  }
  return res.blob()
}

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  return request('/api/health/')
}

export async function listEscenarios(): Promise<Escenario[]> {
  const data = await request<Escenario[] | { results: Escenario[] }>('/api/escenarios/')
  if (Array.isArray(data)) return data
  return data.results ?? []
}

export async function getEscenario(id: number): Promise<Escenario> {
  return request(`/api/escenarios/${id}/`)
}

export async function ejecutarEscenario(payload: EjecutarPayload): Promise<Escenario> {
  return request('/api/escenarios/ejecutar/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function reejecutarEscenario(id: number): Promise<ReejecutarResponse> {
  return request(`/api/escenarios/${id}/reejecutar/`, {
    method: 'POST',
    body: JSON.stringify({}),
  })
}

/** POST /api/escenarios/sensibilidad/ */
export async function sensibilidadEscenario(
  payload: SensibilidadPayload,
): Promise<SensibilidadReport> {
  return request('/api/escenarios/sensibilidad/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/** GET /api/escenarios/{id}/hash/ */
export async function fetchHash(id: number): Promise<HashResponse> {
  return request(`/api/escenarios/${id}/hash/`)
}

/** POST /api/escenarios/{id}/hash/?actualizar=1 */
export async function actualizarHash(id: number): Promise<HashResponse> {
  return request(`/api/escenarios/${id}/hash/?actualizar=1`, {
    method: 'POST',
    body: JSON.stringify({}),
  })
}

export async function fetchGeoJson(id: number): Promise<SadeFeatureCollection> {
  return request(`/api/escenarios/${id}/geojson/`)
}

export async function fetchTileJson(id: number): Promise<TileJsonStub> {
  return request(`/api/escenarios/${id}/tilejson/`)
}

/** GET /api/escenarios/{id}/mapa/ — fallback a /geojson/. */
export async function fetchMapa(id: number): Promise<SadeFeatureCollection> {
  try {
    const data = await request<MapaResponse | SadeFeatureCollection>(
      `/api/escenarios/${id}/mapa/?formato=geojson`,
    )
    if ('type' in data && data.type === 'FeatureCollection') {
      return data as SadeFeatureCollection
    }
    const mapa = data as MapaResponse
    if (mapa.geojson?.type === 'FeatureCollection') return mapa.geojson
  } catch {
    /* fallback */
  }
  return fetchGeoJson(id)
}

function queryToParams(q: ConsultaCeldaQuery): URLSearchParams {
  if ('lat' in q) {
    return new URLSearchParams({ lat: String(q.lat), lon: String(q.lon) })
  }
  if ('row' in q) {
    return new URLSearchParams({ row: String(q.row), col: String(q.col) })
  }
  return new URLSearchParams({ x: String(q.x), y: String(q.y) })
}

/**
 * GET /api/escenarios/{id}/consulta-celda/?lat=&lon= | row=&col= | x=&y=
 * Si la API falla → mock con mensaje claro.
 */
export async function fetchConsultaCelda(
  escenarioId: number,
  query: ConsultaCeldaQuery,
): Promise<ConsultaCeldaResponse> {
  const params = queryToParams(query)
  try {
    const data = await request<ConsultaCeldaResponse>(
      `/api/escenarios/${escenarioId}/consulta-celda/?${params.toString()}`,
    )
    return { ...data, fuente: data.fuente ?? 'api' }
  } catch (err) {
    const motivo =
      err instanceof Error
        ? err.message
        : 'API de consulta-celda no disponible'
    if ('lat' in query) {
      const mock = buildMockCelda(escenarioId, query.lat, query.lon)
      return { ...mock, mock_motivo: motivo }
    }
    // row/col o x/y sin lat/lon: mock sintético con coords derivadas
    const lat = 'row' in query ? 20.5 + query.row * 0.01 : 20.6
    const lon = 'col' in query ? -104.0 + query.col * 0.01 : -103.9
    const mock = buildMockCelda(escenarioId, lat, lon)
    return {
      ...mock,
      row: 'row' in query ? query.row : mock.row,
      col: 'col' in query ? query.col : mock.col,
      mock_motivo: motivo,
    }
  }
}

/** GET /api/escenarios/{id}/pdf/ — expediente. Mock solo si falla. */
export async function downloadExpedientePdf(id: number): Promise<{ blob: Blob; mock: boolean; motivo?: string }> {
  try {
    const blob = await requestBlob(`/api/escenarios/${id}/pdf/`, 'application/pdf')
    return { blob, mock: false }
  } catch (err) {
    const motivo = err instanceof Error ? err.message : 'API /pdf/ no disponible'
    const text = [
      'SADE — Expediente de escenario (FALLBACK DEMO)',
      `Escenario ID: ${id}`,
      `Motivo: ${motivo}`,
      '',
      'Path real: GET /api/escenarios/{id}/pdf/',
      'Reintente con backend + autenticación SADE.',
    ].join('\n')
    return {
      blob: new Blob([text], { type: 'text/plain;charset=utf-8' }),
      mock: true,
      motivo,
    }
  }
}

/** GET /api/escenarios/{id}/reproducibilidad/ — ZIP RNF-002. Mock solo si falla. */
export async function downloadReproducibilidadZip(
  id: number,
): Promise<{ blob: Blob; mock: boolean; motivo?: string }> {
  try {
    const blob = await requestBlob(
      `/api/escenarios/${id}/reproducibilidad/`,
      'application/zip',
    )
    return { blob, mock: false }
  } catch (err) {
    const motivo = err instanceof Error ? err.message : 'API /reproducibilidad/ no disponible'
    const text = [
      'SADE — Paquete de reproducibilidad (FALLBACK DEMO)',
      `Escenario ID: ${id}`,
      `Motivo: ${motivo}`,
      '',
      'Path real: GET /api/escenarios/{id}/reproducibilidad/',
    ].join('\n')
    return {
      blob: new Blob([text], { type: 'text/plain;charset=utf-8' }),
      mock: true,
      motivo,
    }
  }
}

export function triggerDownload(blob: Blob, filename: string): void {
  const href = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = href
  a.download = filename
  a.click()
  URL.revokeObjectURL(href)
}

export function demoConjuntoPesosId(): number {
  const raw = import.meta.env.VITE_DEMO_CONJUNTO_PESOS_ID as string | undefined
  const n = Number(raw ?? '1')
  return Number.isFinite(n) && n > 0 ? n : 1
}
