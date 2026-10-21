import { useMemo, useState } from 'react'

import {
  AHP_PROCEDENCIA,
  BLOQUE_LABEL,
  BLOQUE_WEIGHTS,
  CR_BLOQUES,
  CRITERIOS_CATALOGO,
} from '../data/criteriosCatalog'

const SCALE = [1 / 9, 1 / 7, 1 / 5, 1 / 3, 1, 3, 5, 7, 9] as const

function formatScale(v: number): string {
  if (v >= 1) return String(v)
  const inv = Math.round(1 / v)
  return `1/${inv}`
}

/** Estimación simple de CR a partir de una matriz 3×3 de bloques (demo). */
function estimateCr3(matrix: number[][]): number {
  const n = 3
  const rowSums = matrix.map((row) => row.reduce((a, b) => a + b, 0))
  const total = rowSums.reduce((a, b) => a + b, 0) || 1
  const weights = rowSums.map((s) => s / total)
  const aw = matrix.map((row) =>
    row.reduce((acc, v, j) => acc + v * weights[j], 0),
  )
  const lambda =
    aw.reduce((acc, v, i) => acc + v / weights[i], 0) / n
  const ci = (lambda - n) / (n - 1)
  const ri = 0.58
  return ci / ri
}

/**
 * RI-004 — AHP: pesos Apéndice B + formulario matrices 1/9–9 + alerta CR≥0.10.
 */
export function AhpPage() {
  // Matriz de comparación de bloques GEO / ECO / SOC (valores iniciales ≈ pesos publicados)
  const [m01, setM01] = useState(1.18) // GEO vs ECO
  const [m02, setM02] = useState(1.13) // GEO vs SOC
  const [m12, setM12] = useState(0.96) // ECO vs SOC

  const matrix = useMemo(
    () => [
      [1, m01, m02],
      [1 / m01, 1, m12],
      [1 / m02, 1 / m12, 1],
    ],
    [m01, m02, m12],
  )

  const cr = estimateCr3(matrix)
  const crAlert = cr >= 0.1

  const bloques = [
    { key: 'geohidrologico', label: 'GEO' },
    { key: 'ecologico', label: 'ECO' },
    { key: 'socioeconomico', label: 'SOC' },
  ] as const

  return (
    <div className="mx-auto h-full max-w-6xl overflow-auto p-4 sm:p-6">
      <header className="mb-4">
        <h2 className="text-lg font-semibold">AHP · RI-004</h2>
        <p className="mt-1 text-sm text-sade-muted">
          Pesos publicados del Apéndice B (panel de 15 expertos, agregación AIJ).
          Puede explorar juicios 1/9–9; si CR ≥ 0.10 se muestra alerta. No se
          requieren matrices crudas del panel histórico.
        </p>
      </header>

      <section className="mb-6 rounded border border-sade-border bg-white p-4">
        <h3 className="text-xs font-bold tracking-wide text-sade-muted uppercase">
          Procedencia
        </h3>
        <dl className="mt-2 grid gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-xs text-sade-muted">Conjunto</dt>
            <dd>{AHP_PROCEDENCIA.nombre}</dd>
          </div>
          <div>
            <dt className="text-xs text-sade-muted">Panel / fechas</dt>
            <dd>
              {AHP_PROCEDENCIA.panel} expertos · {AHP_PROCEDENCIA.fechas}
            </dd>
          </div>
          <div>
            <dt className="text-xs text-sade-muted">Método</dt>
            <dd>{AHP_PROCEDENCIA.metodo}</dd>
          </div>
          <div>
            <dt className="text-xs text-sade-muted">CR publicados (bloques)</dt>
            <dd className="font-mono text-xs">
              GEO {CR_BLOQUES.cr_geohidro} · ECO {CR_BLOQUES.cr_ecol} · SOC{' '}
              {CR_BLOQUES.cr_socio} · criterios {CR_BLOQUES.cr_criterios}
            </dd>
          </div>
        </dl>
      </section>

      <section className="mb-6 rounded border border-sade-border bg-white p-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-xs font-bold tracking-wide text-sade-muted uppercase">
            Matriz de juicios (bloques)
          </h3>
          <div
            className={`rounded px-2 py-1 text-xs font-semibold ${
              crAlert
                ? 'bg-red-50 text-sade-danger'
                : 'bg-sade-soft text-sade-accent'
            }`}
          >
            CR estimado = {cr.toFixed(4)}
            {crAlert ? ' · ⚠ CR ≥ 0.10 — revise juicios' : ' · consistente'}
          </div>
        </div>

        {crAlert && (
          <p className="mb-3 rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-sade-danger">
            La razón de consistencia es ≥ 0.10. Saaty recomienda revisar los juicios
            antes de publicar pesos.
          </p>
        )}

        <div className="overflow-auto">
          <table className="w-full min-w-[20rem] border-collapse text-sm">
            <thead>
              <tr className="bg-slate-100 text-xs text-sade-muted">
                <th className="px-2 py-2" />
                {bloques.map((b) => (
                  <th key={b.key} className="px-2 py-2">
                    {b.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bloques.map((row, i) => (
                <tr key={row.key} className="border-t border-slate-100">
                  <th className="px-2 py-2 text-left text-xs">{row.label}</th>
                  {bloques.map((col, j) => {
                    if (i === j) {
                      return (
                        <td key={col.key} className="px-2 py-2 text-center text-sade-muted">
                          1
                        </td>
                      )
                    }
                    if (i > j) {
                      return (
                        <td key={col.key} className="px-2 py-2 text-center font-mono text-xs text-sade-muted">
                          {formatScale(1 / matrix[j][i])}
                        </td>
                      )
                    }
                    const value = matrix[i][j]
                    const setter =
                      i === 0 && j === 1
                        ? setM01
                        : i === 0 && j === 2
                          ? setM02
                          : setM12
                    return (
                      <td key={col.key} className="px-2 py-2 text-center">
                        <select
                          className="rounded border border-sade-border px-1 py-1 text-xs"
                          value={String(value)}
                          onChange={(e) => setter(Number(e.target.value))}
                        >
                          {SCALE.map((s) => (
                            <option key={s} value={String(s)}>
                              {formatScale(s)}
                            </option>
                          ))}
                        </select>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-[0.7rem] text-sade-muted">
          Escala Saaty 1/9–9. Los pesos globales de la tabla inferior siguen siendo los
          del Apéndice B publicados (referencia fija).
        </p>
      </section>

      <section className="mb-6">
        <h3 className="mb-2 text-xs font-bold tracking-wide text-sade-muted uppercase">
          Pesos de bloque (Apéndice B)
        </h3>
        <div className="grid gap-2 sm:grid-cols-3">
          {(Object.keys(BLOQUE_WEIGHTS) as Array<keyof typeof BLOQUE_WEIGHTS>).map(
            (k) => (
              <div
                key={k}
                className="rounded border border-sade-border bg-white px-3 py-2 text-sm"
              >
                <div className="text-xs text-sade-muted">{BLOQUE_LABEL[k]}</div>
                <div className="font-mono font-semibold">
                  {(BLOQUE_WEIGHTS[k] * 100).toFixed(2)}%
                </div>
              </div>
            ),
          )}
        </div>
      </section>

      <section>
        <h3 className="mb-2 text-xs font-bold tracking-wide text-sade-muted uppercase">
          Pesos globales · 21 criterios
        </h3>
        <div className="overflow-auto rounded border border-sade-border bg-white">
          <table className="w-full min-w-[28rem] border-collapse text-sm">
            <thead>
              <tr className="bg-slate-100 text-left text-xs text-sade-muted">
                <th className="px-3 py-2">ID</th>
                <th className="px-3 py-2">Criterio</th>
                <th className="px-3 py-2">Bloque</th>
                <th className="px-3 py-2">Peso global</th>
              </tr>
            </thead>
            <tbody>
              {CRITERIOS_CATALOGO.map((c) => (
                <tr key={c.id} className="border-t border-slate-100">
                  <td className="px-3 py-1.5 font-mono text-xs">{c.id}</td>
                  <td className="px-3 py-1.5">{c.nombre}</td>
                  <td className="px-3 py-1.5 text-xs">{BLOQUE_LABEL[c.bloque]}</td>
                  <td className="px-3 py-1.5 font-mono text-xs">
                    {(c.peso_global * 100).toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
