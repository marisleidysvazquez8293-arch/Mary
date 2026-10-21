interface StatusLineProps {
  loading?: boolean
  tone?: 'info' | 'warn' | 'ok' | 'danger'
  children: React.ReactNode
}

const TONE: Record<NonNullable<StatusLineProps['tone']>, string> = {
  info: 'border-slate-200 bg-slate-50 text-slate-700',
  warn: 'border-amber-200 bg-amber-50 text-amber-900',
  ok: 'border-emerald-200 bg-emerald-50 text-emerald-900',
  danger: 'border-red-200 bg-red-50 text-red-800',
}

export function StatusLine({ loading, tone = 'info', children }: StatusLineProps) {
  return (
    <p
      className={`rounded border px-2.5 py-1.5 text-xs leading-snug ${TONE[tone]}`}
      role="status"
    >
      {loading && <span className="mr-1.5 inline-block animate-pulse">●</span>}
      {children}
    </p>
  )
}
