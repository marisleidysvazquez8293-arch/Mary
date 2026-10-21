import type { Escenario } from '../types/api'

interface ScenarioPanelProps {
  escenarios: Escenario[]
  selectedId: number | null
  loading: boolean
  executing: boolean
  error: string | null
  apiStatus: 'unknown' | 'ok' | 'error'
  usingDemoLayer: boolean
  onRefresh: () => void
  onSelect: (id: number) => void
  onEjecutar: () => void
  onReejecutar: () => void
}

function shortHash(h: string | undefined | null): string {
  if (!h) return '—'
  return h.length > 16 ? `${h.slice(0, 12)}…` : h
}

function formatFecha(iso: string | null): string {
  if (!iso) return 'Sin ejecución'
  try {
    return new Intl.DateTimeFormat('es-MX', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

export function ScenarioPanel({
  escenarios,
  selectedId,
  loading,
  executing,
  error,
  apiStatus,
  usingDemoLayer,
  onRefresh,
  onSelect,
  onEjecutar,
  onReejecutar,
}: ScenarioPanelProps) {
  const selected = escenarios.find((e) => e.id === selectedId) ?? null

  return (
    <aside className="panel">
      <header className="panel__brand">
        <p className="panel__eyebrow">SADE</p>
        <h1 className="panel__title">Visor de aptitud</h1>
        <p className="panel__subtitle">
          Localización de rellenos sanitarios — Valles de Jalisco
        </p>
      </header>

      <section className="panel__section">
        <div className="panel__row">
          <h2 className="panel__heading">Escenarios</h2>
          <span
            className={`status-pill status-pill--${apiStatus}`}
            title="Estado de /api/health/"
          >
            {apiStatus === 'ok'
              ? 'API ok'
              : apiStatus === 'error'
                ? 'API offline'
                : 'API…'}
          </span>
        </div>

        <div className="panel__actions">
          <button type="button" className="btn btn--ghost" onClick={onRefresh} disabled={loading}>
            {loading ? 'Cargando…' : 'Actualizar'}
          </button>
          <button
            type="button"
            className="btn btn--primary"
            onClick={onEjecutar}
            disabled={executing}
            title="POST /api/escenarios/ejecutar/ (demo)"
          >
            {executing ? 'Ejecutando…' : 'Ejecutar (demo)'}
          </button>
        </div>

        {error && (
          <p className="panel__error" role="alert">
            {error}
          </p>
        )}

        {usingDemoLayer && (
          <p className="panel__hint">
            Mostrando capa demo local. Conecte el backend y seleccione un escenario
            para ver GeoJSON real.
          </p>
        )}

        <ul className="scenario-list" aria-label="Lista de escenarios">
          {escenarios.length === 0 && !loading && (
            <li className="scenario-list__empty">
              No hay escenarios. Use «Ejecutar (demo)» o cree uno vía API.
            </li>
          )}
          {escenarios.map((esc) => (
            <li key={esc.id}>
              <button
                type="button"
                className={`scenario-item${selectedId === esc.id ? ' scenario-item--active' : ''}`}
                onClick={() => onSelect(esc.id)}
              >
                <span className="scenario-item__name">{esc.nombre}</span>
                <span className="scenario-item__meta">
                  #{esc.id} · v{esc.version_reglas_usada}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel__section">
        <h2 className="panel__heading">Trazabilidad</h2>
        {selected ? (
          <dl className="trace">
            <div className="trace__row">
              <dt>Nombre</dt>
              <dd>{selected.nombre}</dd>
            </div>
            <div className="trace__row">
              <dt>Pesos AHP</dt>
              <dd>{selected.conjunto_pesos_nombre || `ID ${selected.conjunto_pesos}`}</dd>
            </div>
            <div className="trace__row">
              <dt>Ejecutado</dt>
              <dd>{formatFecha(selected.fecha_ejecucion)}</dd>
            </div>
            <div className="trace__row">
              <dt>Hash config.</dt>
              <dd>
                <code title={selected.hash_configuracion}>
                  {shortHash(selected.hash_configuracion)}
                </code>
              </dd>
            </div>
            <div className="trace__row">
              <dt>Hash resultado</dt>
              <dd>
                <code title={selected.hash_resultado}>
                  {shortHash(selected.hash_resultado)}
                </code>
              </dd>
            </div>
            <div className="panel__actions panel__actions--compact">
              <button
                type="button"
                className="btn btn--ghost"
                onClick={onReejecutar}
                disabled={executing}
              >
                Reejecutar
              </button>
            </div>
          </dl>
        ) : (
          <p className="panel__hint">Seleccione un escenario para ver hashes.</p>
        )}
      </section>

      <footer className="panel__footer">
        Capas: OSM + GeoJSON de aptitud · CRS análisis EPSG:32613
      </footer>
    </aside>
  )
}
