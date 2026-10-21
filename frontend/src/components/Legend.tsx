import { SUITABILITY_CLASSES } from '../constants/suitability'

export function Legend() {
  return (
    <aside className="legend" aria-label="Leyenda de clases de aptitud">
      <h2 className="legend__title">Clases de aptitud</h2>
      <ul className="legend__list">
        {SUITABILITY_CLASSES.map((c) => (
          <li key={c.code} className="legend__item">
            <span
              className="legend__swatch"
              style={{ backgroundColor: c.color, borderColor: c.stroke }}
              aria-hidden
            />
            <span className="legend__label">
              <span className="legend__code">{c.code}</span>
              {c.label}
            </span>
          </li>
        ))}
      </ul>
    </aside>
  )
}
