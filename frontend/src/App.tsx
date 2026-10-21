import { useCallback, useEffect, useState } from 'react'

import {
  demoConjuntoPesosId,
  ejecutarEscenario,
  fetchGeoJson,
  fetchHealth,
  listEscenarios,
  reejecutarEscenario,
} from './api/client'
import { MapViewer } from './components/MapViewer'
import { ScenarioPanel } from './components/ScenarioPanel'
import { DEMO_GEOJSON } from './data/demoGeoJson'
import type { Escenario, SadeFeatureCollection } from './types/api'

export default function App() {
  const [escenarios, setEscenarios] = useState<Escenario[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [geojson, setGeojson] = useState<SadeFeatureCollection | null>(DEMO_GEOJSON)
  const [usingDemoLayer, setUsingDemoLayer] = useState(true)
  const [loading, setLoading] = useState(false)
  const [executing, setExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<'unknown' | 'ok' | 'error'>('unknown')

  const refreshList = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      try {
        await fetchHealth()
        setApiStatus('ok')
      } catch {
        setApiStatus('error')
      }

      const list = await listEscenarios()
      setEscenarios(list)
      if (list.length && selectedId == null) {
        setSelectedId(list[0].id)
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No se pudo listar escenarios. ¿Backend y credenciales listos?',
      )
    } finally {
      setLoading(false)
    }
  }, [selectedId])

  useEffect(() => {
    void refreshList()
    // Solo al montar
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (selectedId == null) {
      setGeojson(DEMO_GEOJSON)
      setUsingDemoLayer(true)
      return
    }

    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const gj = await fetchGeoJson(selectedId)
        if (!cancelled) {
          setGeojson(gj)
          setUsingDemoLayer(false)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'No se pudo cargar GeoJSON del escenario.',
          )
          setGeojson(DEMO_GEOJSON)
          setUsingDemoLayer(true)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()

    return () => {
      cancelled = true
    }
  }, [selectedId])

  const onEjecutar = async () => {
    setExecuting(true)
    setError(null)
    try {
      const esc = await ejecutarEscenario({
        nombre: `Demo UI ${new Date().toISOString().slice(0, 19)}`,
        version_reglas_usada: '1.0.0',
        conjunto_pesos_id: demoConjuntoPesosId(),
        parametros_ejecucion: {
          demo_seed: 42,
          shape: [8, 8],
          n_criteria: 3,
          weights: [0.4, 0.35, 0.25],
        },
        weights_from_db: false,
      })
      await refreshList()
      setSelectedId(esc.id)
    } catch (err) {
      setError(
        err instanceof Error
          ? `${err.message} (requiere rol Analista/Admin Técnico y VITE_API_USER/PASSWORD)`
          : 'Error al ejecutar escenario.',
      )
    } finally {
      setExecuting(false)
    }
  }

  const onReejecutar = async () => {
    if (selectedId == null) return
    setExecuting(true)
    setError(null)
    try {
      const out = await reejecutarEscenario(selectedId)
      setEscenarios((prev) =>
        prev.map((e) => (e.id === out.escenario.id ? out.escenario : e)),
      )
      const gj = await fetchGeoJson(selectedId)
      setGeojson(gj)
      setUsingDemoLayer(false)
      if (!out.resultado_reproducido) {
        setError(
          `Reejecución: hash cambió (${out.hash_resultado_anterior.slice(0, 8)}… → ${out.hash_resultado_nuevo.slice(0, 8)}…)`,
        )
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al reejecutar.')
    } finally {
      setExecuting(false)
    }
  }

  return (
    <div className="app">
      <ScenarioPanel
        escenarios={escenarios}
        selectedId={selectedId}
        loading={loading}
        executing={executing}
        error={error}
        apiStatus={apiStatus}
        usingDemoLayer={usingDemoLayer}
        onRefresh={() => void refreshList()}
        onSelect={setSelectedId}
        onEjecutar={() => void onEjecutar()}
        onReejecutar={() => void onReejecutar()}
      />
      <main className="app__map">
        <MapViewer geojson={geojson} fitKey={selectedId ?? 'demo'} />
      </main>
    </div>
  )
}
