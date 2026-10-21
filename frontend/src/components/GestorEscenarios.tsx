import { VERSIONES_REGLAS } from '../constants/criterios'
import type { Escenario, SensibilidadReport } from '../types/api'

export interface GestorEscenariosProps {
  escenarios: Escenario[]
  selectedId: number | null
  loading: boolean
  executing: boolean
  error: string | null
  info: string | null
  apiStatus: 'unknown' | 'ok' | 'error'
  usingDemoLayer: boolean
  versionReglas: string
  conjuntoPesosId: number
  sensibilidad: SensibilidadReport | null
  onVersionChange: (v: string) => void
  onPesosChange: (id: number) => void
  onRefresh: () => void
  onSelect: (id: number) => void
  onEjecutar: () => void
  onReejecutar: () => void
  onSensibilidad: () => void
  onDescargarPdf: () => void
  onDescargarZip: () => void
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

export function GestorEscenarios({
  escenarios,
  selectedId,
  loading,
  executing,
  error,
  info,
  apiStatus,
  usingDemoLayer,
  versionReglas,
  conjuntoPesosId,
  sensibilidad,
  onVersionChange,
  onPesosChange,
  onRefresh,
  onSelect,
  onEjecutar,
  onReejecutar,
  onSensibilidad,
  onDescargarPdf,
  onDescargarZip,
}: GestorEscenariosProps) {
  const selected = escenarios.find((e) => e.id === selectedId) ?? null

  return (
    <aside className="panel">
      <header className="panel__brand">
        <p className="panel__eyebrow">SADE · PASO 4</p>
        <h1 className="panel__title">Gestor de escenarios</h1>
        <p className="panel__subtitle">
          Rellenos sanitarios — Valles de Jalisco
        </p>
      </header>

      <section className="panel__section">
        <div className="panel__row">
          <h2 className="panel__heading">Configuración</h2>
          <span className={`status-pill status-pill--${apiStatus}`}>
            {apiStatus === 'ok' ? 'API ok' : apiStatus === 'error' ? 'API offline' : 'API…'}
          </span>
        </div>

        <label className="field">
          <span className="field__label">Versión de reglas</span>
          <select
            className="field__input"
            value={versionReglas}
            onChange={(e) => onVersionChange(e.target.value)}
          >
            {VERSIONES_REGLAS.map((v) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span className="field__label">Conjunto pesos AHP (ID)</span>
          <input
            className="field__input"
            type="number"
            min={1}
            value={conjuntoPesosId}
            onChange={(e) => onPesosChange(Number(e.target.value) || 1)}
          />
        </label>

        <div className="panel__actions">
          <button type="button" className="btn btn--ghost" onClick={onRefresh} disabled={loading}>
            {loading ? 'Cargando…' : 'Actualizar'}
          </button>
          <button
            type="button"
            className="btn btn--primary"
            onClick={onEjecutar}
            disabled={executing}
            title="POST /api/escenarios/ejecutar/"
          >
            {executing ? 'Ejecutando…' : 'Ejecutar'}
          </button>
        </div>
        <div className="panel__actions panel__actions--compact">
          <button
            type="button"
            className="btn btn--ghost"
            onClick={onSensibilidad}
            disabled={executing}
            title="POST /api/escenarios/sensibilidad/"
          >
            Sensibilidad E0–E8
          </button>
        </div>

        {error && (
          <p className="panel__error" role="alert">
            {error}
          </p>
        )}
        {info && (
          <p className="panel__hint" role="status">
            {info}
          </p>
        )}
        {usingDemoLayer && (
          <p className="panel__hint">
            Capa demo local. Con backend + escenario seleccionado se carga{' '}
            <code>/mapa/</code> o <code>/geojson/</code>.
          </p>
        )}
      </section>

      <section className="panel__section">
        <h2 className="panel__heading">Escenarios</h2>
        <ul className="scenario-list" aria-label="Lista de escenarios">
          {escenarios.length === 0 && !loading && (
            <li className="scenario-list__empty">
              Sin escenarios. Pulse «Ejecutar» o use la capa demo.
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
                  #{esc.id} · v{esc.version_reglas_usada} · pesos{' '}
                  {esc.conjunto_pesos_nombre || esc.conjunto_pesos}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel__section">
        <h2 className="panel__heading">Trazabilidad y descargas</h2>
        {selected ? (
          <>
            <dl className="trace">
              <div className="trace__row">
                <dt>Nombre</dt>
                <dd>{selected.nombre}</dd>
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
            </dl>
            <div className="panel__actions">
              <button
                type="button"
                className="btn btn--ghost"
                onClick={onReejecutar}
                disabled={executing}
              >
                Reejecutar
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={onDescargarPdf}
                title="GET /api/escenarios/{id}/expediente.pdf"
              >
                PDF expediente
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={onDescargarZip}
                title="GET /api/escenarios/{id}/reproducibilidad.zip"
              >
                ZIP reproducib.
              </button>
            </div>
            <p className="panel__footer-note">
              TODO: PDF/ZIP usan mock si el backend aún no publica esos paths.
            </p>
          </>
        ) : (
          <p className="panel__hint">Seleccione un escenario.</p>
        )}
      </section>

      {sensibilidad && (
        <section className="panel__section">
          <h2 className="panel__heading">Última sensibilidad</h2>
          <p className="panel__hint">
            Baseline {sensibilidad.baseline_id} · {sensibilidad.experiments?.length ?? 0}{' '}
            experimentos · {sensibilidad.pairwise_jaccard?.length ?? 0} pares Jaccard
          </p>
        </section>
      )}

      <footer className="panel__footer">
        Capas: OSM · exclusión · aptitud reclasificada · CRS análisis EPSG:32613
      </footer>
    </aside>
  )
}
