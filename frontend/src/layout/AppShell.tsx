import { NavLink, Outlet, useLocation } from 'react-router-dom'

const NAV: Array<{ to: string; label: string; end?: boolean; desc: string }> = [
  { to: '/', label: 'Visor', end: true, desc: 'Mapa de aptitud' },
  { to: '/reglas', label: 'Motor de reglas', desc: '21 criterios NOM-083' },
  { to: '/ahp', label: 'AHP', desc: 'Pesos y consistencia' },
  { to: '/escenarios', label: 'Escenarios', desc: 'Ejecución y sensibilidad' },
  { to: '/expediente', label: 'Expediente', desc: 'PDF y reproducibilidad' },
]

const TITLE_BY_PATH: Record<string, string> = {
  '/': 'Visor cartográfico',
  '/reglas': 'Motor de reglas',
  '/ahp': 'Análisis AHP',
  '/escenarios': 'Escenarios y sensibilidad',
  '/expediente': 'Expediente documental',
}

export function AppShell() {
  const { pathname } = useLocation()
  const pageTitle = TITLE_BY_PATH[pathname] ?? 'SADE'

  return (
    <div className="flex h-full min-h-screen flex-col bg-[#e8edf2] text-sade-ink">
      <header className="z-40 shrink-0 border-b border-slate-700 bg-[#0f172a] text-slate-100 shadow-sm">
        <div className="flex items-center gap-4 px-4 py-3">
          <div className="min-w-0">
            <p className="text-[0.65rem] font-bold tracking-[0.16em] text-emerald-400 uppercase">
              SADE · Valles de Jalisco
            </p>
            <h1 className="truncate text-base font-semibold tracking-tight sm:text-lg">
              Sistema de Apoyo a Decisiones Espaciales
            </h1>
            <p className="mt-0.5 hidden text-xs text-slate-400 sm:block">
              Localización de sitios de disposición final · NOM-083-SEMARNAT-2003
            </p>
          </div>
          <div className="ml-auto hidden text-right text-xs text-slate-400 lg:block">
            <div className="font-medium text-slate-200">{pageTitle}</div>
            <div>Aplicación web</div>
          </div>
        </div>
        <nav
          className="flex gap-0.5 overflow-x-auto border-t border-slate-800 bg-[#1e293b] px-2 py-1.5 sm:px-4"
          aria-label="Secciones de la aplicación"
        >
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              title={item.desc}
              className={({ isActive }) =>
                [
                  'shrink-0 rounded-md px-3 py-2 text-sm font-medium transition',
                  isActive
                    ? 'bg-sade-accent text-white shadow-sm'
                    : 'text-slate-300 hover:bg-slate-700/80 hover:text-white',
                ].join(' ')
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="min-h-0 flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
