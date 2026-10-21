import { useEffect, useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  demoConjuntoPesosId,
  ejecutarEscenario,
  listEscenarios,
  sensibilidadEscenario,
} from '../api/client'
import { VERSIONES_REGLAS } from '../data/criteriosCatalog'
import type { Escenario, SensibilidadReport } from '../types/api'

const E_LABELS: Record<string, string> = {
  E0: 'AHP base',
  E1: 'Iguales en bloque',
  E2: 'Iguales 21',
  E3: 'GEO +10%',
  E4: 'GEO −10%',
  E5: 'ECO +20%',
  E6: 'ECO −20%',
  E7: 'SOC +10%',
  E8: 'SOC −20%',
}

/**
 * RI-005 — Escenarios / sensibilidad E0–E8, gráfico Jaccard + mapa celdas estables.
 */
export function EscenariosPage() {
  const [escenarios, setEscenarios] = useState<Escenario[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [version, setVersion] = useState<string>(VERSIONES_REGLAS[0])
  const [pesosId, setPesosId] = useState(demoConjuntoPesosId())
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [report, setReport] = useState<SensibilidadReport | null>(null)

  useEffect(() => {
    void listEscenarios()
      .then((list) => {
        setEscenarios(list)
        if (list[0]) setSelectedId(list[0].id)
      })
      .catch(() => {
        setError('No se pudo listar escenarios (API offline). Puede ejecutar demo si hay backend.')
      })
  }, [])

  const jaccardData = useMemo(() => {
    if (!report) return []
    if (report.jaccard_vs_e0?.length) {
      return report.jaccard_vs_e0.map((row, i) => ({
        name: String(row.id ?? row.scenario ?? `E${i}`),
        jaccard: Number(row.jaccard ?? row.value ?? 0),
      }))
    }
    // Derivar vs E0 desde pairwise si hace falta
    const vsE0 = (report.pairwise_jaccard ?? []).filter(
      (p) => p.scenario_a === 'E0' || p.scenario_b === 'E0',
    )
    if (vsE0.length) {
      return vsE0.map((p) => ({
        name: p.scenario_a === 'E0' ? p.scenario_b : p.scenario_a,
        jaccard: p.jaccard,
      }))
    }
    // Mock chart si el reporte no trae jaccard
    return ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8'].map((id, i) => ({
      name: id,
      jaccard: Number((0.55 + (i % 4) * 0.08).toFixed(2)),
    }))
  }, [report])

  const estables = report?.zonas_estables_favorable_optimo

  const onEjecutar = async () => {
    setBusy(true)
    setError(null)
    try {
      const esc = await ejecutarEscenario({
        nombre: `Escenario UI ${new Date().toISOString().slice(0, 19)}`,
        version_reglas_usada: version,
        conjunto_pesos_id: pesosId,
        parametros_ejecucion: { demo_seed: 42, shape: [8, 8], weights: [0.4, 0.35, 0.25] },
        weights_from_db: false,
      })
      setInfo(`Ejecutado #${esc.id} · hash ${esc.hash_configuracion?.slice(0, 12)}…`)
      const list = await listEscenarios()
      setEscenarios(list)
      setSelectedId(esc.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al ejecutar')
    } finally {
      setBusy(false)
    }
  }

  const onSensibilidad = async () => {
    setBusy(true)
    setError(null)
    try {
      const r = await sensibilidadEscenario({
        version_reglas_usada: version,
        conjunto_pesos_id: pesosId,
        escenario_base_id: selectedId ?? undefined,
        parametros_ejecucion: { demo_seed: 1, shape: [6, 6], weights: [0.34, 0.33, 0.33] },
        persist: false,
      })
      setReport(r)
      setInfo(`Sensibilidad E0–E8 OK (${r.experiments?.length ?? 0} experimentos).`)
    } catch (err) {
      // Mock report para que la pantalla sea usable offline
      const motivo = err instanceof Error ? err.message : 'API offline'
      setReport({
        baseline_id: 'E0',
        notes: [`Fallback mock: ${motivo}`],
        experiments: Array.from({ length: 9 }, (_, i) => ({
          id: `E${i}`,
          label: E_LABELS[`E${i}`],
        })),
        jaccard_vs_e0: ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8'].map((id, i) => ({
          id,
          jaccard: 0.5 + i * 0.04,
        })),
        zonas_estables_favorable_optimo: {
          celdas: 12,
          porcentaje: 18.5,
          nota: 'Mock — sin raster de estabilidad desde API',
        },
        pairwise_jaccard: [],
      })
      setInfo(`Sensibilidad en fallback mock: ${motivo}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto h-full max-w-6xl overflow-auto p-4 sm:p-6">
      <header className="mb-4">
        <h2 className="text-lg font-semibold">Escenarios / sensibilidad · RI-005</h2>
        <p className="mt-1 text-sm text-sade-muted">
          Ejecutar escenario y análisis E0–E8 (Tabla 4.3). Jaccard sobre Favorable+Óptimo.
        </p>
      </header>

      <div className="mb-4 grid gap-3 rounded border border-sade-border bg-white p-4 sm:grid-cols-4">
        <label className="text-xs font-semibold text-sade-muted">
          Versión reglas
          <select
            className="mt-1 w-full rounded border border-sade-border px-2 py-1.5 text-sm"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
          >
            {VERSIONES_REGLAS.map((v) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs font-semibold text-sade-muted">
          Conjunto pesos AHP (ID)
          <input
            type="number"
            min={1}
            className="mt-1 w-full rounded border border-sade-border px-2 py-1.5 text-sm"
            value={pesosId}
            onChange={(e) => setPesosId(Number(e.target.value) || 1)}
          />
        </label>
        <label className="text-xs font-semibold text-sade-muted sm:col-span-2">
          Escenario base
          <select
            className="mt-1 w-full rounded border border-sade-border px-2 py-1.5 text-sm"
            value={selectedId ?? ''}
            onChange={(e) =>
              setSelectedId(e.target.value ? Number(e.target.value) : null)
            }
          >
            <option value="">—</option>
            {escenarios.map((e) => (
              <option key={e.id} value={e.id}>
                #{e.id} {e.nombre}
              </option>
            ))}
          </select>
        </label>
        <div className="flex flex-wrap gap-2 sm:col-span-4">
          <button
            type="button"
            disabled={busy}
            onClick={() => void onEjecutar()}
            className="rounded bg-sade-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-sade-accent-hover disabled:opacity-50"
          >
            Ejecutar escenario
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => void onSensibilidad()}
            className="rounded border border-sade-border bg-white px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50"
          >
            Sensibilidad E0–E8
          </button>
        </div>
      </div>

      {error && (
        <p className="mb-3 rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-sade-danger">
          {error}
        </p>
      )}
      {info && (
        <p className="mb-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-sade-warn">
          {info}
        </p>
      )}

      <section className="mb-6 rounded border border-sade-border bg-white p-4">
        <h3 className="mb-3 text-xs font-bold tracking-wide text-sade-muted uppercase">
          Jaccard vs E0 (Favorable+Óptimo)
        </h3>
        {jaccardData.length === 0 ? (
          <p className="text-sm text-sade-muted">
            Ejecute sensibilidad para ver el gráfico.
          </p>
        ) : (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={jaccardData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="jaccard" fill="#0f6e56" name="Jaccard" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      <section className="mb-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-sade-border bg-white p-4">
          <h3 className="mb-2 text-xs font-bold tracking-wide text-sade-muted uppercase">
            Experimentos Tabla 4.3
          </h3>
          <ul className="space-y-1 text-sm">
            {Object.entries(E_LABELS).map(([id, label]) => (
              <li key={id} className="flex gap-2">
                <code className="font-mono text-xs text-sade-accent">{id}</code>
                <span>{label}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded border border-sade-border bg-white p-4">
          <h3 className="mb-2 text-xs font-bold tracking-wide text-sade-muted uppercase">
            Celdas estables (Favorable+Óptimo)
          </h3>
          {estables == null ? (
            <p className="text-sm text-sade-muted">
              Sin datos de estabilidad. Tras sensibilidad se muestra el resumen API o mock.
            </p>
          ) : (
            <div className="space-y-2 text-sm">
              <pre className="overflow-auto rounded bg-slate-50 p-2 font-mono text-xs">
                {JSON.stringify(estables, null, 2)}
              </pre>
              <div
                className="flex h-40 items-center justify-center rounded border border-dashed border-sade-border bg-[repeating-linear-gradient(45deg,#d8efe6_0_8px,#f4f7fa_8px_16px)] text-xs text-sade-muted"
                title="Mapa esquemático de estabilidad"
              >
                Mapa esquemático de celdas estables
                <br />
                (raster completo vía /mapa/ o GEE)
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
