import { NavLink, Outlet } from 'react-router-dom'

const NAV: Array<{ to: string; label: string; end?: boolean }> = [
  { to: '/', label: 'Visor', end: true },
  { to: '/reglas', label: 'Motor de reglas' },
  { to: '/ahp', label: 'AHP' },
  { to: '/escenarios', label: 'Escenarios' },
  { to: '/expediente', label: 'Expediente' },
]

export function AppShell() {
  return (
    <div className="flex h-full min-h-screen flex-col bg-[#e8edf2] text-sade-ink">
      <header className="z-40 flex shrink-0 items-center gap-4 border-b border-sade-border bg-[#1e293b] px-4 py-2.5 text-slate-100">
        <div className="min-w-0">
          <p className="text-[0.65rem] font-bold tracking-[0.14em] text-emerald-300 uppercase">
            SADE
          </p>
          <h1 className="truncate text-sm font-semibold tracking-tight sm:text-base">
            Sistema de Apoyo a Decisiones Espaciales
          </h1>
        </div>
        <nav className="ml-auto flex flex-wrap items-center gap-1" aria-label="Principal">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                [
                  'rounded px-2.5 py-1.5 text-xs font-medium transition sm:text-sm',
                  isActive
                    ? 'bg-sade-accent text-white'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white',
                ].join(' ')
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <div className="min-h-0 flex-1">
        <Outlet />
      </div>
    </div>
  )
}
