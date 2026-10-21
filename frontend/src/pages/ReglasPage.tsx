import { useMemo, useState } from 'react'

import {
  BLOQUE_LABEL,
  CRITERIOS_CATALOGO,
  VERSIONES_REGLAS,
  type CriterioCatalogo,
} from '../data/criteriosCatalog'

/**
 * RI-003 — Motor de reglas: 21 criterios, umbrales editables,
 * buffers NOM-083 bloqueados para usuarios normales.
 */
export function ReglasPage() {
  const role = (import.meta.env.VITE_SADE_ROLE as string | undefined) ?? 'analista'
  const esAdmin = role === 'admin' || role === 'administrador_tecnico'

  const [version, setVersion] = useState<string>(VERSIONES_REGLAS[0])
  const [rows, setRows] = useState<CriterioCatalogo[]>(() =>
    CRITERIOS_CATALOGO.map((c) => ({ ...c })),
  )
  const [msg, setMsg] = useState<string | null>(null)
  const [historial, setHistorial] = useState<string[]>(['1.0.0'])
  const [loading] = useState(false)

  const porBloque = useMemo(() => {
    const map = new Map<string, CriterioCatalogo[]>()
    for (const r of rows) {
      const list = map.get(r.bloque) ?? []
      list.push(r)
      map.set(r.bloque, list)
    }
    return map
  }, [rows])

  const updateBuffer = (id: string, value: string) => {
    const row = rows.find((r) => r.id === id)
    if (!row) return
    if (row.buffer_bloqueado && !esAdmin) {
      setMsg(
        `Buffer de ${id} bloqueado (NOM-083). Solo Administrador Técnico puede editarlo.`,
      )
      return
    }
    const n = value === '' ? null : Number(value)
    setRows((prev) =>
      prev.map((r) => (r.id === id ? { ...r, buffer_m: Number.isFinite(n as number) ? n : null } : r)),
    )
    setMsg(`Umbral ${id} actualizado en versión ${version} (local; persistencia API pendiente).`)
  }

  return (
    <div className="mx-auto h-full max-w-6xl overflow-auto p-4 sm:p-6">
      <header className="mb-4">
        <h2 className="text-lg font-semibold">Motor de reglas · RI-003</h2>
        <p className="mt-1 text-sm text-sade-muted">
          21 criterios GEO/ECO/SOC. Los buffers normativos NOM-083 están bloqueados para
          usuarios normales (rol actual: <code>{role}</code>).
        </p>
      </header>

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <label className="text-xs font-semibold text-sade-muted">
          Versión de reglas
          <select
            className="mt-1 block rounded border border-sade-border bg-white px-2 py-1.5 text-sm"
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
        <button
          type="button"
          className="rounded bg-sade-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-sade-accent-hover"
          onClick={() => {
            if (!historial.includes(version)) {
              setHistorial((h) => [version, ...h])
            }
            setMsg(
              `Versión ${version} registrada en el historial local. Persistencia remota cuando la API de reglas esté disponible.`,
            )
          }}
        >
          Guardar versión
        </button>
        <div className="text-xs text-sade-muted">
          Historial:{' '}
          {historial.map((v) => (
            <button
              key={v}
              type="button"
              className="mr-1 rounded bg-white px-1.5 py-0.5 font-mono ring-1 ring-sade-border hover:bg-slate-50"
              onClick={() => setVersion(v)}
            >
              {v}
            </button>
          ))}
        </div>
      </div>
      {loading && (
        <p className="mb-3 text-xs text-sade-muted">Cargando criterios…</p>
      )}

      {msg && (
        <p className="mb-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-sade-warn">
          {msg}
        </p>
      )}

      {[...porBloque.entries()].map(([bloque, criterios]) => (
        <section key={bloque} className="mb-6">
          <h3 className="mb-2 text-xs font-bold tracking-wide text-sade-muted uppercase">
            {BLOQUE_LABEL[bloque as keyof typeof BLOQUE_LABEL]} ({criterios.length})
          </h3>
          <div className="overflow-auto rounded border border-sade-border bg-white">
            <table className="w-full min-w-[40rem] border-collapse text-sm">
              <thead>
                <tr className="bg-slate-100 text-left text-xs text-sade-muted">
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">Criterio</th>
                  <th className="px-3 py-2">Tipo</th>
                  <th className="px-3 py-2">Norma</th>
                  <th className="px-3 py-2">Buffer (m)</th>
                  <th className="px-3 py-2">Peso %</th>
                </tr>
              </thead>
              <tbody>
                {criterios.map((c) => {
                  const locked = c.buffer_bloqueado && !esAdmin
                  return (
                    <tr key={c.id} className="border-t border-slate-100">
                      <td className="px-3 py-2 font-mono text-xs">{c.id}</td>
                      <td className="px-3 py-2">{c.nombre}</td>
                      <td className="px-3 py-2 text-xs">{c.tipo_restriccion}</td>
                      <td className="px-3 py-2 text-xs text-sade-muted">
                        {c.norma ?? '—'}
                      </td>
                      <td className="px-3 py-2">
                        <input
                          type="number"
                          className={`w-24 rounded border px-2 py-1 text-xs ${
                            locked
                              ? 'cursor-not-allowed border-slate-200 bg-slate-100 text-sade-muted'
                              : 'border-sade-border bg-white'
                          }`}
                          value={c.buffer_m ?? ''}
                          disabled={locked}
                          title={
                            locked
                              ? 'Buffer NOM-083 bloqueado'
                              : 'Editable'
                          }
                          onChange={(e) => updateBuffer(c.id, e.target.value)}
                          placeholder={c.buffer_m == null ? 'n/a' : undefined}
                        />
                        {c.buffer_bloqueado && (
                          <span className="ml-1 text-[0.65rem] text-sade-muted">🔒</span>
                        )}
                      </td>
                      <td className="px-3 py-2 font-mono text-xs">
                        {(c.peso_global * 100).toFixed(2)}%
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </section>
      ))}
    </div>
  )
}
