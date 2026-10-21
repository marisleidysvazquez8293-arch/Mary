import { SUITABILITY_CLASSES } from '../constants/suitability'

export function Legend() {
  return (
    <aside
      className="absolute bottom-4 left-3 z-[1000] min-w-[11.5rem] rounded border border-sade-border bg-white/95 p-3 shadow-sm"
      aria-label="Leyenda de clases de aptitud"
    >
      <h2 className="mb-2 text-[0.7rem] font-bold tracking-wide text-sade-muted uppercase">
        Clases de aptitud
      </h2>
      <ul className="flex flex-col gap-1.5">
        {SUITABILITY_CLASSES.map((c) => (
          <li key={c.code} className="flex items-center gap-2 text-xs leading-tight">
            <span
              className="inline-block h-4 w-4 shrink-0 rounded-sm border"
              style={{ backgroundColor: c.color, borderColor: c.stroke }}
              aria-hidden
            />
            <span>
              <span className="mr-1 font-mono text-[0.65rem] text-sade-muted">{c.code}</span>
              {c.label}
            </span>
          </li>
        ))}
      </ul>
    </aside>
  )
}
