import type {
  Escenario,
  EjecutarPayload,
  ReejecutarResponse,
  SadeFeatureCollection,
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
  const token = btoa(`${user}:${pass}`)
  return { Authorization: `Basic ${token}` }
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

export async function fetchGeoJson(id: number): Promise<SadeFeatureCollection> {
  return request(`/api/escenarios/${id}/geojson/`)
}

export async function fetchTileJson(id: number): Promise<TileJsonStub> {
  return request(`/api/escenarios/${id}/tilejson/`)
}

export function demoConjuntoPesosId(): number {
  const raw = import.meta.env.VITE_DEMO_CONJUNTO_PESOS_ID as string | undefined
  const n = Number(raw ?? '1')
  return Number.isFinite(n) && n > 0 ? n : 1
}
