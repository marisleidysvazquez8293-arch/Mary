import type { ConsultaCeldaResponse } from '../types/api'

interface ConsultaCeldaProps {
  data: ConsultaCeldaResponse | null
  loading: boolean
  onClose: () => void
}

function asLines(items: ConsultaCeldaResponse['restricciones']): string[] {
  return (items ?? []).map((item) =>
    typeof item === 'string' ? item : JSON.stringify(item),
  )
}

export function ConsultaCelda({ data, loading, onClose }: ConsultaCeldaProps) {
  if (!loading && !data) return null

  const restricciones = data ? asLines(data.restricciones) : []
  const advertencias = data ? asLines(data.advertencias) : []
  const coords =
    data?.lat != null && data?.lon != null
      ? `${data.lat.toFixed(5)}°, ${data.lon.toFixed(5)}°`
      : data?.row != null && data?.col != null
        ? `fila ${data.row}, col ${data.col}`
        : null

  return (
    <aside
      className="absolute top-3 right-3 z-[1100] max-h-[calc(100%-1.5rem)] w-[min(28rem,calc(100%-1.5rem))] overflow-auto rounded border border-sade-border bg-white/97 p-3 shadow-lg"
      aria-label="Inspector espacial"
    >
      <header className="mb-3 flex items-start justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold">Inspector espacial</h2>
          {data && (
            <p className="mt-0.5 font-mono text-[0.7rem] text-sade-muted">
              {coords ?? '—'}
              {data.fuente === 'mock' && (
                <span className="ml-1 font-sans font-semibold text-sade-warn">
                  fallback mock
                </span>
              )}
            </p>
          )}
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded border border-sade-border px-2 py-1 text-xs hover:bg-slate-50"
        >
          Cerrar
        </button>
      </header>

      {loading && (
        <p className="rounded bg-amber-50 px-2 py-1.5 text-xs text-sade-warn">
          Consultando factores…
        </p>
      )}

      {data && !loading && (
        <>
          <div className="mb-3 grid grid-cols-3 gap-2 text-xs">
            <div>
              <span className="block text-[0.65rem] tracking-wide text-sade-muted uppercase">
                Clase
              </span>
              <strong>
                {data.class_code} · {data.class_label}
              </strong>
            </div>
            <div>
              <span className="block text-[0.65rem] tracking-wide text-sade-muted uppercase">
                Aptitud S
              </span>
              <strong>{data.suitability}</strong>
            </div>
            <div>
              <span className="block text-[0.65rem] tracking-wide text-sade-muted uppercase">
                Excluido
              </span>
              <strong>{data.excluido ? 'Sí' : 'No'}</strong>
            </div>
          </div>

          {data.advertencia_aerodromo?.aplica && (
            <div className="mb-2 rounded border border-yellow-300 bg-amber-50 p-2 text-xs text-sade-warn">
              <strong>Aeródromo (NOM-083 6.1.1)</strong>
              <p className="mt-1">{data.advertencia_aerodromo.mensaje}</p>
            </div>
          )}

          {restricciones.length > 0 && (
            <div className="mb-2 rounded border border-red-200 bg-red-50 p-2 text-xs text-sade-danger">
              <strong>Restricciones activas</strong>
              <ul className="mt-1 list-disc pl-4">
                {restricciones.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            </div>
          )}

          {advertencias.length > 0 && (
            <ul className="mb-2 list-disc pl-4 text-xs text-sade-warn">
              {advertencias.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
          )}

          <h3 className="mb-1 text-[0.7rem] font-bold tracking-wide text-sade-muted uppercase">
            Desglose ({data.factores.length} factores)
          </h3>
          <div className="max-h-56 overflow-auto rounded border border-sade-border">
            <table className="w-full border-collapse text-[0.7rem]">
              <thead>
                <tr className="sticky top-0 bg-slate-100 text-left text-sade-muted">
                  <th className="px-1.5 py-1">ID</th>
                  <th className="px-1.5 py-1">Criterio</th>
                  <th className="px-1.5 py-1">xᵢ</th>
                  <th className="px-1.5 py-1">wᵢ</th>
                </tr>
              </thead>
              <tbody>
                {data.factores.map((f) => (
                  <tr
                    key={f.id_criterio}
                    className={`border-t border-slate-100 ${
                      f.restriccion_activa ? 'bg-red-50' : ''
                    }`}
                  >
                    <td className="px-1.5 py-1 font-mono">{f.id_criterio}</td>
                    <td className="px-1.5 py-1">{f.nombre ?? f.id_criterio}</td>
                    <td className="px-1.5 py-1">{f.valor_factor}</td>
                    <td className="px-1.5 py-1">{(f.peso * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.fuente === 'mock' && (
            <p className="mt-2 rounded bg-amber-50 px-2 py-1.5 text-[0.7rem] text-sade-warn">
              Fallback mock: {data.mock_motivo ?? 'API no respondió'}. Path:{' '}
              <code>GET …/consulta-celda/</code>
            </p>
          )}
        </>
      )}
    </aside>
  )
}
