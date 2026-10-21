import { buildMockCelda } from '../data/mockCelda'
import type {
  ConsultaCeldaResponse,
  Escenario,
  EjecutarPayload,
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

export async function sensibilidadEscenario(
  payload: SensibilidadPayload,
): Promise<SensibilidadReport> {
  return request('/api/escenarios/sensibilidad/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function fetchGeoJson(id: number): Promise<SadeFeatureCollection> {
  return request(`/api/escenarios/${id}/geojson/`)
}

export async function fetchTileJson(id: number): Promise<TileJsonStub> {
  return request(`/api/escenarios/${id}/tilejson/`)
}

/**
 * GET /api/escenarios/{id}/mapa/
 * Preferido frente a geojson suelto; hace fallback a /geojson/.
 */
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

/**
 * GET /api/escenarios/{id}/celda/?lat=&lon=
 * TODO: confirmar path/params en sade-paso4-api-contrato.md cuando el backend lo publique.
 * Si 404/501/offline → mock demo.
 */
export async function fetchConsultaCelda(
  escenarioId: number,
  lat: number,
  lon: number,
): Promise<ConsultaCeldaResponse> {
  const q = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
  })
  try {
    const data = await request<ConsultaCeldaResponse>(
      `/api/escenarios/${escenarioId}/celda/?${q.toString()}`,
    )
    return { ...data, fuente: data.fuente ?? 'api' }
  } catch {
    return buildMockCelda(escenarioId, lat, lon)
  }
}

/**
 * GET /api/escenarios/{id}/expediente.pdf
 * TODO: endpoint previsto; descarga mock (texto) si no existe.
 */
export async function downloadExpedientePdf(id: number): Promise<{ blob: Blob; mock: boolean }> {
  const url = `${apiBase()}/api/escenarios/${id}/expediente.pdf`
  try {
    const res = await fetch(url, { headers: { ...authHeaders(), Accept: 'application/pdf' } })
    if (!res.ok) throw new Error(String(res.status))
    return { blob: await res.blob(), mock: false }
  } catch {
    const text = [
      'SADE — Expediente de escenario (DEMO)',
      `Escenario ID: ${id}`,
      '',
      'TODO: conectar a GET /api/escenarios/{id}/expediente.pdf',
      'cuando el backend lo publique (ver sade-paso4-api-contrato.md).',
      '',
      'Este archivo es un marcador generado por el frontend.',
    ].join('\n')
    return {
      blob: new Blob([text], { type: 'text/plain;charset=utf-8' }),
      mock: true,
    }
  }
}

/**
 * GET /api/escenarios/{id}/reproducibilidad.zip
 * TODO: endpoint previsto; descarga mock si no existe.
 */
export async function downloadReproducibilidadZip(
  id: number,
): Promise<{ blob: Blob; mock: boolean }> {
  const url = `${apiBase()}/api/escenarios/${id}/reproducibilidad.zip`
  try {
    const res = await fetch(url, {
      headers: { ...authHeaders(), Accept: 'application/zip' },
    })
    if (!res.ok) throw new Error(String(res.status))
    return { blob: await res.blob(), mock: false }
  } catch {
    const text = [
      'SADE — Paquete de reproducibilidad (DEMO)',
      `Escenario ID: ${id}`,
      '',
      'TODO: conectar a GET /api/escenarios/{id}/reproducibilidad.zip',
    ].join('\n')
    return {
      blob: new Blob([text], { type: 'text/plain;charset=utf-8' }),
      mock: true,
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
