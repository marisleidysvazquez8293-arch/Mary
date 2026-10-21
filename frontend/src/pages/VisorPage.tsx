import { useCallback, useEffect, useMemo, useState } from 'react'

import { fetchConsultaCelda, fetchHealth, fetchMapa, listEscenarios } from '../api/client'
import {
  fetchGeeCapas,
  fetchGeeConsultaCelda,
  fetchGeeLayerTiles,
  fetchGeeStatus,
  type GeeCapa,
} from '../api/gee'
import { ConsultaCelda } from '../components/ConsultaCelda'
import {
  MapViewer,
  type GeeXyzLayer,
  type MapClickPayload,
} from '../components/MapViewer'
import { StatusLine } from '../components/StatusLine'
import { DEMO_CANDIDATOS } from '../data/demoCandidatos'
import { DEMO_GEOJSON } from '../data/demoGeoJson'
import type { ConsultaCeldaResponse, Escenario, SadeFeatureCollection } from '../types/api'

/**
 * RF-044 — Visor: OSM + GeoJSON aptitud/exclusión + capas GEE XYZ dinámicas.
 * Contrato: /api/gee/status|capas|capas/{id}/tiles|consulta-celda
 */
export function VisorPage() {
  const [escenarios, setEscenarios] = useState<Escenario[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [geojson, setGeojson] = useState<SadeFeatureCollection | null>(DEMO_GEOJSON)
  const [apiOk, setApiOk] = useState(false)
  const [geeMode, setGeeMode] = useState<'ready' | 'degraded' | 'unknown'>('unknown')
  const [geeMsg, setGeeMsg] = useState<string | null>(null)
  const [capas, setCapas] = useState<GeeCapa[]>([])
  const [enabledLayers, setEnabledLayers] = useState<Record<string, boolean>>({})
  const [tileUrls, setTileUrls] = useState<Record<string, string | null>>({})
  const [msg, setMsg] = useState<string | null>(null)
  const [celda, setCelda] = useState<ConsultaCeldaResponse | null>(null)
  const [celdaLoading, setCeldaLoading] = useState(false)
  const [clickPoint, setClickPoint] = useState<MapClickPayload | null>(null)
  const [showExclusion, setShowExclusion] = useState(true)
  const [showAptitud, setShowAptitud] = useState(true)
  const [showCandidatos, setShowCandidatos] = useState(true)
  const [inspectorFuente, setInspectorFuente] = useState<'gee' | 'escenario'>('gee')
  const [booting, setBooting] = useState(true)
  const [mapLoading, setMapLoading] = useState(false)

  useEffect(() => {
    void (async () => {
      setBooting(true)
      try {
        await fetchHealth()
        setApiOk(true)
        const list = await listEscenarios()
        setEscenarios(list)
        if (list[0]) setSelectedId(list[0].id)
      } catch {
        setApiOk(false)
        setMsg('API escenarios no conectada — se muestran datos demo coherentes del territorio.')
      }

      const status = await fetchGeeStatus()
      const mode = (status.gee?.mode ?? status.mode ?? 'degraded') as string
      setGeeMode(mode === 'ready' ? 'ready' : 'degraded')
      if (status.fuente === 'mock' || mode !== 'ready') {
        setGeeMsg(
          status.mock_motivo ??
            status.message ??
            status.gee?.message ??
            'GEE degradado',
        )
      }

      const catalog = await fetchGeeCapas({
        forceMock: mode !== 'ready' && status.fuente === 'mock',
      })
      setCapas(catalog.capas)
      if (catalog.fuente === 'mock') {
        setGeeMsg(catalog.mock_motivo ?? catalog.gee.message ?? 'Capas GEE en mock')
        setGeeMode('degraded')
      }

      const initialEnabled: Record<string, boolean> = {}
      const urls: Record<string, string | null> = {}
      for (const c of catalog.capas) {
        // Activa por defecto NDVI / GSW si hay tile; resto apagado
        const prefer =
          c.id === 'sentinel2_ndvi' || c.id === 'gsw_occurrence' || c.id === 'landsat8_rgb'
        initialEnabled[c.id] = Boolean(prefer && c.tile_url_template)
        urls[c.id] = c.tile_url_template
      }
      setEnabledLayers(initialEnabled)
      setTileUrls(urls)

      // Si falta plantilla pero GEE ready, pedir /tiles/ por capa preferida
      if (catalog.fuente === 'api' && mode === 'ready') {
        for (const c of catalog.capas) {
          if (!c.tile_url_template) {
            const tiles = await fetchGeeLayerTiles(c.id)
            if (tiles.tile_url_template) {
              urls[c.id] = tiles.tile_url_template
            }
          }
        }
        setTileUrls({ ...urls })
      }
      setBooting(false)
    })()
  }, [])

  useEffect(() => {
    if (selectedId == null) {
      setGeojson(DEMO_GEOJSON)
      return
    }
    let cancelled = false
    void (async () => {
      setMapLoading(true)
      try {
        const gj = await fetchMapa(selectedId)
        if (!cancelled) {
          setGeojson(gj)
        }
      } catch (err) {
        if (!cancelled) {
          setGeojson(DEMO_GEOJSON)
          setMsg(
            err instanceof Error
              ? `Mapa del escenario no disponible (${err.message}). Capa demo de Valles activa.`
              : 'Mapa del escenario no disponible. Capa demo de Valles activa.',
          )
        }
      } finally {
        if (!cancelled) setMapLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [selectedId])

  const toggleLayer = async (id: string) => {
    const next = !enabledLayers[id]
    setEnabledLayers((prev) => ({ ...prev, [id]: next }))
    if (next && !tileUrls[id] && geeMode === 'ready') {
      const tiles = await fetchGeeLayerTiles(id)
      setTileUrls((prev) => ({
        ...prev,
        [id]: tiles.tile_url_template,
      }))
      if (!tiles.tile_url_template) {
        setGeeMsg(tiles.message ?? `Sin TileURL para ${id}`)
      }
    }
  }

  const geeXyzLayers: GeeXyzLayer[] = useMemo(
    () =>
      capas
        .filter((c) => enabledLayers[c.id] && tileUrls[c.id])
        .map((c) => ({
          id: c.id,
          nombre: c.nombre,
          url: tileUrls[c.id] as string,
          opacity: c.id === 'landsat8_rgb' ? 0.85 : 0.6,
          visible: true,
        })),
    [capas, enabledLayers, tileUrls],
  )

  const onMapClick = useCallback(
    async (p: MapClickPayload) => {
      setClickPoint(p)
      setCeldaLoading(true)
      try {
        if (inspectorFuente === 'gee') {
          const data = await fetchGeeConsultaCelda({
            lat: p.lat,
            lon: p.lon,
            escenario_id: selectedId ?? undefined,
          })
          setCelda(data)
          if (data.fuente === 'mock') {
            setMsg(
              `GEE consulta-celda fallback: ${data.mock_motivo ?? 'error'}. Path: /api/gee/consulta-celda/`,
            )
          }
        } else {
          const id = selectedId ?? 0
          const data = await fetchConsultaCelda(id, { lat: p.lat, lon: p.lon })
          setCelda(data)
          if (data.fuente === 'mock') {
            setMsg(
              `Escenario consulta-celda fallback: ${data.mock_motivo ?? 'error'}`,
            )
          }
        }
      } finally {
        setCeldaLoading(false)
      }
    },
    [inspectorFuente, selectedId],
  )

  return (
    <div className="relative flex h-full min-h-0 flex-col">
      <div className="absolute top-3 left-3 z-[1000] flex max-w-md flex-col gap-2">
        <div className="rounded border border-sade-border bg-white/95 p-3 shadow-sm">
          <div className="mb-2 flex items-center justify-between gap-2">
            <h2 className="text-sm font-semibold">Visor · Valles de Jalisco</h2>
            <div className="flex gap-1">
              <span
                className={`rounded px-1.5 py-0.5 text-[0.65rem] font-semibold ${
                  apiOk ? 'bg-sade-soft text-sade-accent' : 'bg-red-50 text-sade-danger'
                }`}
              >
                {apiOk ? 'API ok' : 'API offline'}
              </span>
              <span
                className={`rounded px-1.5 py-0.5 text-[0.65rem] font-semibold ${
                  geeMode === 'ready'
                    ? 'bg-sade-soft text-sade-accent'
                    : 'bg-amber-50 text-sade-warn'
                }`}
              >
                GEE {geeMode}
              </span>
            </div>
          </div>

          <label className="mb-2 block text-xs text-sade-muted">
            Escenario (CLP / GeoJSON)
            <select
              className="mt-1 w-full rounded border border-sade-border px-2 py-1.5 text-sm"
              value={selectedId ?? ''}
              onChange={(e) =>
                setSelectedId(e.target.value ? Number(e.target.value) : null)
              }
            >
              <option value="">Demo local</option>
              {escenarios.map((esc) => (
                <option key={esc.id} value={esc.id}>
                  #{esc.id} {esc.nombre}
                </option>
              ))}
            </select>
          </label>

          {(booting || mapLoading) && (
            <div className="mb-2">
              <StatusLine loading tone="info">
                {booting ? 'Cargando catálogo GEE y escenarios…' : 'Actualizando mapa del escenario…'}
              </StatusLine>
            </div>
          )}

          <div className="mb-2 flex flex-wrap gap-3 text-xs">
            <label className="inline-flex items-center gap-1.5">
              <input
                type="checkbox"
                checked={showExclusion}
                onChange={(e) => setShowExclusion(e.target.checked)}
              />
              Exclusión
            </label>
            <label className="inline-flex items-center gap-1.5">
              <input
                type="checkbox"
                checked={showAptitud}
                onChange={(e) => setShowAptitud(e.target.checked)}
              />
              Aptitud (6 clases)
            </label>
            <label className="inline-flex items-center gap-1.5">
              <input
                type="checkbox"
                checked={showCandidatos}
                onChange={(e) => setShowCandidatos(e.target.checked)}
              />
              Candidatos
            </label>
          </div>

          <fieldset className="mb-2">
            <legend className="mb-1 text-[0.65rem] font-bold tracking-wide text-sade-muted uppercase">
              Capas GEE (XYZ)
            </legend>
            <div className="flex max-h-28 flex-col gap-1 overflow-auto text-xs">
              {capas.length === 0 && (
                <span className="text-sade-muted">Sin catálogo aún…</span>
              )}
              {capas.map((c) => {
                const hasTile = Boolean(tileUrls[c.id])
                return (
                  <label key={c.id} className="inline-flex items-start gap-1.5">
                    <input
                      type="checkbox"
                      className="mt-0.5"
                      checked={Boolean(enabledLayers[c.id])}
                      disabled={!hasTile && geeMode !== 'ready'}
                      onChange={() => void toggleLayer(c.id)}
                    />
                    <span>
                      <span className="font-medium">{c.nombre}</span>
                      <span className="ml-1 font-mono text-[0.65rem] text-sade-muted">
                        {c.id}
                        {!hasTile ? ' · sin tile' : ''}
                      </span>
                    </span>
                  </label>
                )
              })}
            </div>
          </fieldset>

          <label className="mb-1 block text-xs text-sade-muted">
            Inspector al clic
            <select
              className="mt-1 w-full rounded border border-sade-border px-2 py-1.5 text-sm"
              value={inspectorFuente}
              onChange={(e) =>
                setInspectorFuente(e.target.value as 'gee' | 'escenario')
              }
            >
              <option value="gee">GEE · /api/gee/consulta-celda/</option>
              <option value="escenario">Escenario · /api/escenarios/…/consulta-celda/</option>
            </select>
          </label>

          {(geeMsg || msg) && (
            <div className="mt-2">
              <StatusLine tone={geeMode === 'ready' ? 'ok' : 'warn'}>
                {geeMsg ?? msg}
              </StatusLine>
            </div>
          )}
        </div>
      </div>

      <div className="min-h-0 flex-1">
        <MapViewer
          geojson={geojson}
          fitKey={selectedId ?? 'demo'}
          onMapClick={(p) => void onMapClick(p)}
          clickMarker={clickPoint}
          showExclusion={showExclusion}
          showAptitud={showAptitud}
          showCandidatos={showCandidatos}
          candidatos={DEMO_CANDIDATOS}
          geeLayers={geeXyzLayers}
          fullscreen
        />
      </div>

      <ConsultaCelda
        data={celda}
        loading={celdaLoading}
        onClose={() => {
          setCelda(null)
          setClickPoint(null)
        }}
      />
    </div>
  )
}
