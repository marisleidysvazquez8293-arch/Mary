import { useEffect, useState } from 'react'

import {
  downloadExpedientePdf,
  downloadReproducibilidadZip,
  fetchHash,
  listEscenarios,
  triggerDownload,
} from '../api/client'
import { LEYENDA_LEGAL } from '../data/criteriosCatalog'
import type { Escenario, HashResponse } from '../types/api'

/**
 * RF-039 / RF-046 — Expediente: PDF + ZIP reproducibilidad + leyenda legal.
 */
export function ExpedientePage() {
  const [escenarios, setEscenarios] = useState<Escenario[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [hash, setHash] = useState<HashResponse | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    void listEscenarios()
      .then((list) => {
        setEscenarios(list)
        if (list[0]) setSelectedId(list[0].id)
      })
      .catch(() => setMsg('API offline: seleccione un ID manual o use descargas en fallback mock.'))
  }, [])

  useEffect(() => {
    if (selectedId == null) {
      setHash(null)
      return
    }
    void fetchHash(selectedId)
      .then(setHash)
      .catch(() => setHash(null))
  }, [selectedId])

  const selected = escenarios.find((e) => e.id === selectedId) ?? null

  const onPdf = async () => {
    if (selectedId == null) {
      setMsg('Seleccione un escenario.')
      return
    }
    setBusy(true)
    const { blob, mock, motivo } = await downloadExpedientePdf(selectedId)
    triggerDownload(
      blob,
      mock ? `expediente-${selectedId}-DEMO.txt` : `expediente-${selectedId}.pdf`,
    )
    setMsg(
      mock
        ? `PDF fallback mock (GET …/pdf/ falló: ${motivo}).`
        : 'PDF de expediente descargado.',
    )
    setBusy(false)
  }

  const onZip = async () => {
    if (selectedId == null) {
      setMsg('Seleccione un escenario.')
      return
    }
    setBusy(true)
    const { blob, mock, motivo } = await downloadReproducibilidadZip(selectedId)
    triggerDownload(
      blob,
      mock
        ? `reproducibilidad-${selectedId}-DEMO.txt`
        : `reproducibilidad-${selectedId}.zip`,
    )
    setMsg(
      mock
        ? `ZIP fallback mock (GET …/reproducibilidad/ falló: ${motivo}).`
        : 'ZIP de reproducibilidad descargado (RNF-002).',
    )
    setBusy(false)
  }

  return (
    <div className="mx-auto h-full max-w-3xl overflow-auto p-4 sm:p-6">
      <header className="mb-4">
        <h2 className="text-lg font-semibold">Expediente · RF-039 / RF-046</h2>
        <p className="mt-1 text-sm text-sade-muted">
          Genere el expediente PDF del escenario y el paquete ZIP de
          reproducibilidad (config, pesos AHP, hashes de capas, software,
          resultados). Incluye la leyenda legal obligatoria.
        </p>
      </header>

      <section className="mb-4 rounded border border-sade-border bg-white p-4">
        <label className="text-xs font-semibold text-sade-muted">
          Escenario
          <select
            className="mt-1 block w-full rounded border border-sade-border px-2 py-1.5 text-sm"
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

        {selected && (
          <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-xs text-sade-muted">Versión reglas</dt>
              <dd>{selected.version_reglas_usada}</dd>
            </div>
            <div>
              <dt className="text-xs text-sade-muted">Pesos AHP</dt>
              <dd>{selected.conjunto_pesos_nombre || selected.conjunto_pesos}</dd>
            </div>
            <div>
              <dt className="text-xs text-sade-muted">Hash configuración</dt>
              <dd className="font-mono text-xs">
                {hash?.hash_configuracion ?? selected.hash_configuracion}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-sade-muted">Hash trazabilidad</dt>
              <dd className="font-mono text-xs">
                {hash?.hash_trazabilidad ?? '—'}
              </dd>
            </div>
          </dl>
        )}

        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy || selectedId == null}
            onClick={() => void onPdf()}
            className="rounded bg-sade-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-sade-accent-hover disabled:opacity-50"
          >
            Descargar PDF
          </button>
          <button
            type="button"
            disabled={busy || selectedId == null}
            onClick={() => void onZip()}
            className="rounded border border-sade-border bg-white px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50"
          >
            Descargar ZIP
          </button>
        </div>
        {msg && (
          <p className="mt-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-sade-warn">
            {msg}
          </p>
        )}
      </section>

      <section className="rounded border border-sade-border bg-white p-4">
        <h3 className="text-xs font-bold tracking-wide text-sade-muted uppercase">
          Leyenda legal
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-sade-ink">{LEYENDA_LEGAL}</p>
        <p className="mt-3 text-[0.7rem] text-sade-muted">
          Paths: <code>GET /api/escenarios/{'{id}'}/pdf/</code> ·{' '}
          <code>GET /api/escenarios/{'{id}'}/reproducibilidad/</code>
        </p>
      </section>
    </div>
  )
}
