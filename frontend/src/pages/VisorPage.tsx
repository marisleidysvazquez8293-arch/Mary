import { useCallback, useEffect, useState } from 'react'

import { fetchConsultaCelda, fetchHealth, fetchMapa, listEscenarios } from '../api/client'
import { fetchGeeLayers, type GeeMapContract } from '../api/gee'
import { ConsultaCelda } from '../components/ConsultaCelda'
import { MapViewer, type MapClickPayload } from '../components/MapViewer'
import { DEMO_GEOJSON } from '../data/demoGeoJson'
import type { ConsultaCeldaResponse, Escenario, SadeFeatureCollection } from '../types/api'

/**
 * RF-044 — Visor fullscreen: OSM + GeoJSON (exclusión/aptitud) + capas GEE (mock si falta contrato).
 */
export function VisorPage() {
  const [escenarios, setEscenarios] = useState<Escenario[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [geojson, setGeojson] = useState<SadeFeatureCollection | null>(DEMO_GEOJSON)
  const [gee, setGee] = useState<GeeMapContract | null>(null)
  const [apiOk, setApiOk] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [celda, setCelda] = useState<ConsultaCeldaResponse | null>(null)
  const [celdaLoading, setCeldaLoading] = useState(false)
  const [clickPoint, setClickPoint] = useState<MapClickPayload | null>(null)
  const [showExclusion, setShowExclusion] = useState(true)
  const [showAptitud, setShowAptitud] = useState(true)

  useEffect(() => {
    void (async () => {
      try {
        await fetchHealth()
        setApiOk(true)
        const list = await listEscenarios()
        setEscenarios(list)
        if (list[0]) setSelectedId(list[0].id)
      } catch {
        setApiOk(false)
        setMsg('API offline — mostrando capa demo local y mocks GEE.')
      }
    })()
  }, [])

  useEffect(() => {
    if (selectedId == null) {
      setGeojson(DEMO_GEOJSON)
      void fetchGeeLayers(0).then(setGee)
      return
    }
    let cancelled = false
    void (async () => {
      try {
        const gj = await fetchMapa(selectedId)
        if (!cancelled) {
          setGeojson(gj)
          setMsg(null)
        }
      } catch (err) {
        if (!cancelled) {
          setGeojson(DEMO_GEOJSON)
          setMsg(
            err instanceof Error
              ? `Mapa API falló (${err.message}) — capa demo.`
              : 'Mapa API falló — capa demo.',
          )
        }
      }
      const g = await fetchGeeLayers(selectedId)
      if (!cancelled) setGee(g)
    })()
    return () => {
      cancelled = true
    }
  }, [selectedId])

  const onMapClick = useCallback(
    async (p: MapClickPayload) => {
      setClickPoint(p)
      setCeldaLoading(true)
      const id = selectedId ?? 0
      const data = await fetchConsultaCelda(id, { lat: p.lat, lon: p.lon })
      setCelda(data)
      if (data.fuente === 'mock') {
        setMsg(
          `Inspector en fallback mock: ${data.mock_motivo ?? 'API no disponible'}`,
        )
      }
      setCeldaLoading(false)
    },
    [selectedId],
  )

  return (
    <div className="relative flex h-full min-h-0 flex-col">
      <div className="absolute top-3 left-3 z-[1000] flex max-w-md flex-col gap-2">
        <div className="rounded border border-sade-border bg-white/95 p-3 shadow-sm">
          <div className="mb-2 flex items-center justify-between gap-2">
            <h2 className="text-sm font-semibold">Visor · Valles de Jalisco</h2>
            <span
              className={`rounded px-1.5 py-0.5 text-[0.65rem] font-semibold ${
                apiOk
                  ? 'bg-sade-soft text-sade-accent'
                  : 'bg-red-50 text-sade-danger'
              }`}
            >
              {apiOk ? 'API ok' : 'API offline'}
            </span>
          </div>
          <label className="mb-2 block text-xs text-sade-muted">
            Escenario
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
          <div className="flex flex-wrap gap-3 text-xs">
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
          </div>
          {gee?.fuente === 'mock' && (
            <p className="mt-2 text-[0.7rem] leading-snug text-sade-warn">
              GEE TileURL no disponible ({gee.mock_motivo}). Capas GEE: exclusión /
              aptitud / candidatos en modo mock.
            </p>
          )}
          {msg && (
            <p className="mt-2 text-[0.7rem] leading-snug text-amber-800">{msg}</p>
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
