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
    <aside className="celda-panel" aria-label="Consulta de celda">
      <header className="celda-panel__head">
        <div>
          <h2 className="celda-panel__title">Consulta de celda</h2>
          {data && (
            <p className="celda-panel__coords">
              {coords ?? '—'}
              {data.fuente === 'mock' && (
                <span className="celda-panel__badge"> fallback mock</span>
              )}
            </p>
          )}
        </div>
        <button type="button" className="btn btn--ghost" onClick={onClose} aria-label="Cerrar">
          Cerrar
        </button>
      </header>

      {loading && <p className="panel__hint">Consultando factores…</p>}

      {data && !loading && (
        <>
          <div className="celda-summary">
            <div>
              <span className="celda-summary__label">Clase</span>
              <strong>
                {data.class_code} · {data.class_label}
              </strong>
            </div>
            <div>
              <span className="celda-summary__label">Aptitud S</span>
              <strong>{data.suitability}</strong>
            </div>
            <div>
              <span className="celda-summary__label">Excluido</span>
              <strong>{data.excluido ? 'Sí' : 'No'}</strong>
            </div>
          </div>

          {data.advertencia_aerodromo?.aplica && (
            <div className="celda-alert celda-alert--warn" role="status">
              <strong>Aeródromo (NOM-083 6.1.1)</strong>
              <p>{data.advertencia_aerodromo.mensaje}</p>
              {data.advertencia_aerodromo.distancia_km != null && (
                <p>Distancia estimada: {data.advertencia_aerodromo.distancia_km} km</p>
              )}
            </div>
          )}

          {restricciones.length > 0 && (
            <div className="celda-alert celda-alert--danger">
              <strong>Restricciones activas</strong>
              <ul>
                {restricciones.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            </div>
          )}

          {advertencias.length > 0 && (
            <ul className="celda-warn-list">
              {advertencias.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
          )}

          <h3 className="celda-panel__subtitle">
            Desglose de factores ({data.factores.length})
          </h3>
          <div className="celda-table-wrap">
            <table className="celda-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Criterio</th>
                  <th>xᵢ</th>
                  <th>wᵢ</th>
                  <th>w·x</th>
                  <th>Rest.</th>
                </tr>
              </thead>
              <tbody>
                {data.factores.map((f) => {
                  const contrib =
                    f.contribucion ??
                    Number((f.valor_factor * f.peso).toFixed(4))
                  return (
                    <tr
                      key={f.id_criterio}
                      className={f.restriccion_activa ? 'celda-table__row--rest' : undefined}
                    >
                      <td>
                        <code>{f.id_criterio}</code>
                      </td>
                      <td title={f.detalle ?? f.nombre}>
                        <span className="celda-table__nombre">{f.nombre ?? f.id_criterio}</span>
                        {f.bloque && (
                          <span className="celda-table__bloque">{f.bloque}</span>
                        )}
                      </td>
                      <td>{f.valor_factor}</td>
                      <td>{(f.peso * 100).toFixed(1)}%</td>
                      <td>{contrib}</td>
                      <td>{f.restriccion_activa ? 'Sí' : '—'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {data.fuente === 'mock' && (
            <p className="panel__hint">
              Fallback mock: {data.mock_motivo ?? 'API no respondió'}. Path contrato:{' '}
              <code>GET /api/escenarios/{'{id}'}/consulta-celda/?lat=&amp;lon=</code> (también{' '}
              <code>row</code>/<code>col</code>).
            </p>
          )}
        </>
      )}
    </aside>
  )
}
