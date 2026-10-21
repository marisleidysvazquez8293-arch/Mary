import { useCallback, useEffect, useState } from 'react'

import {
  demoConjuntoPesosId,
  downloadExpedientePdf,
  downloadReproducibilidadZip,
  ejecutarEscenario,
  fetchConsultaCelda,
  fetchHealth,
  fetchMapa,
  listEscenarios,
  reejecutarEscenario,
  sensibilidadEscenario,
  triggerDownload,
} from './api/client'
import { ConsultaCelda } from './components/ConsultaCelda'
import { GestorEscenarios } from './components/GestorEscenarios'
import { MapViewer, type MapClickPayload } from './components/MapViewer'
import { DEMO_GEOJSON } from './data/demoGeoJson'
import type {
  ConsultaCeldaResponse,
  Escenario,
  SadeFeatureCollection,
  SensibilidadReport,
} from './types/api'

export default function App() {
  const [escenarios, setEscenarios] = useState<Escenario[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [geojson, setGeojson] = useState<SadeFeatureCollection | null>(DEMO_GEOJSON)
  const [usingDemoLayer, setUsingDemoLayer] = useState(true)
  const [loading, setLoading] = useState(false)
  const [executing, setExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<'unknown' | 'ok' | 'error'>('unknown')
  const [versionReglas, setVersionReglas] = useState('1.0.0')
  const [conjuntoPesosId, setConjuntoPesosId] = useState(demoConjuntoPesosId())
  const [sensibilidad, setSensibilidad] = useState<SensibilidadReport | null>(null)
  const [celda, setCelda] = useState<ConsultaCeldaResponse | null>(null)
  const [celdaLoading, setCeldaLoading] = useState(false)
  const [clickPoint, setClickPoint] = useState<MapClickPayload | null>(null)

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
        const gj = await fetchMapa(selectedId)
        if (!cancelled) {
          setGeojson(gj)
          setUsingDemoLayer(false)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'No se pudo cargar mapa del escenario.',
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
    setInfo(null)
    try {
      const esc = await ejecutarEscenario({
        nombre: `Demo UI ${new Date().toISOString().slice(0, 19)}`,
        version_reglas_usada: versionReglas,
        conjunto_pesos_id: conjuntoPesosId,
        parametros_ejecucion: {
          demo_seed: 42,
          shape: [8, 8],
          n_criteria: 3,
          weights: [0.4, 0.35, 0.25],
        },
        weights_from_db: false,
      })
      setInfo(
        `Ejecutado #${esc.id}. Hash config: ${esc.hash_configuracion?.slice(0, 12) ?? '—'}…`,
      )
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
    setInfo(null)
    try {
      const out = await reejecutarEscenario(selectedId)
      setEscenarios((prev) =>
        prev.map((e) => (e.id === out.escenario.id ? out.escenario : e)),
      )
      const gj = await fetchMapa(selectedId)
      setGeojson(gj)
      setUsingDemoLayer(false)
      setInfo(
        out.resultado_reproducido
          ? 'Reejecución: hash de resultado reproducido.'
          : `Hash cambió (${out.hash_resultado_anterior.slice(0, 8)}… → ${out.hash_resultado_nuevo.slice(0, 8)}…)`,
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al reejecutar.')
    } finally {
      setExecuting(false)
    }
  }

  const onSensibilidad = async () => {
    setExecuting(true)
    setError(null)
    setInfo(null)
    try {
      const report = await sensibilidadEscenario({
        version_reglas_usada: versionReglas,
        conjunto_pesos_id: conjuntoPesosId,
        parametros_ejecucion: {
          demo_seed: 1,
          shape: [6, 6],
          weights: [0.34, 0.33, 0.33],
        },
        persist: false,
      })
      setSensibilidad(report)
      setInfo(
        `Sensibilidad OK: ${report.experiments?.length ?? 0} experimentos (E0–E8).`,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No se pudo ejecutar sensibilidad (API offline o sin permisos).',
      )
    } finally {
      setExecuting(false)
    }
  }

  const onMapClick = async (p: MapClickPayload) => {
    setClickPoint(p)
    setCeldaLoading(true)
    const id = selectedId ?? 0
    try {
      const data = await fetchConsultaCelda(id, p.lat, p.lon)
      setCelda(data)
      if (data.fuente === 'mock') {
        setInfo(
          'Desglose de celda en modo demo (endpoint /celda/ no disponible o sin auth).',
        )
      }
    } finally {
      setCeldaLoading(false)
    }
  }

  const onDescargarPdf = async () => {
    if (selectedId == null) return
    const { blob, mock } = await downloadExpedientePdf(selectedId)
    triggerDownload(
      blob,
      mock ? `expediente-escenario-${selectedId}-DEMO.txt` : `expediente-escenario-${selectedId}.pdf`,
    )
    setInfo(
      mock
        ? 'PDF no disponible en API: se descargó marcador DEMO. TODO: /expediente.pdf'
        : 'Expediente PDF descargado.',
    )
  }

  const onDescargarZip = async () => {
    if (selectedId == null) return
    const { blob, mock } = await downloadReproducibilidadZip(selectedId)
    triggerDownload(
      blob,
      mock
        ? `reproducibilidad-escenario-${selectedId}-DEMO.txt`
        : `reproducibilidad-escenario-${selectedId}.zip`,
    )
    setInfo(
      mock
        ? 'ZIP no disponible en API: se descargó marcador DEMO. TODO: /reproducibilidad.zip'
        : 'Paquete de reproducibilidad descargado.',
    )
  }

  return (
    <div className="app">
      <GestorEscenarios
        escenarios={escenarios}
        selectedId={selectedId}
        loading={loading}
        executing={executing}
        error={error}
        info={info}
        apiStatus={apiStatus}
        usingDemoLayer={usingDemoLayer}
        versionReglas={versionReglas}
        conjuntoPesosId={conjuntoPesosId}
        sensibilidad={sensibilidad}
        onVersionChange={setVersionReglas}
        onPesosChange={setConjuntoPesosId}
        onRefresh={() => void refreshList()}
        onSelect={setSelectedId}
        onEjecutar={() => void onEjecutar()}
        onReejecutar={() => void onReejecutar()}
        onSensibilidad={() => void onSensibilidad()}
        onDescargarPdf={() => void onDescargarPdf()}
        onDescargarZip={() => void onDescargarZip()}
      />
      <main className="app__map">
        <MapViewer
          geojson={geojson}
          fitKey={selectedId ?? 'demo'}
          onMapClick={(p) => void onMapClick(p)}
          clickMarker={clickPoint}
        />
        <ConsultaCelda
          data={celda}
          loading={celdaLoading}
          onClose={() => {
            setCelda(null)
            setClickPoint(null)
          }}
        />
      </main>
    </div>
  )
}
