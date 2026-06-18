import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'

type SetupStatus = 'completo' | 'en-curso' | 'pendiente' | 'bloqueado'

interface SetupActionCardProps {
  step: string
  title: string
  description: string
  status: SetupStatus
  ctaLabel: string
  href: string
  meta: string
}

const statusStyles: Record<SetupStatus, string> = {
  completo: 'bg-emerald-100 text-emerald-800',
  'en-curso': 'bg-sky-100 text-sky-800',
  pendiente: 'bg-amber-100 text-amber-900',
  bloqueado: 'bg-rose-100 text-rose-800',
}

const statusLabel: Record<SetupStatus, string> = {
  completo: 'Completo',
  'en-curso': 'En Curso',
  pendiente: 'Pendiente',
  bloqueado: 'Bloqueado',
}

export function SetupActionCard({
  step,
  title,
  description,
  status,
  ctaLabel,
  href,
  meta,
}: SetupActionCardProps) {
  const linkClassName = 'inline-flex items-center rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900'

  return (
    <Card className="flex h-full flex-col justify-between border-slate-200 p-5">
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <span className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            Paso {step}
          </span>
          <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${statusStyles[status]}`}>
            {statusLabel[status]}
          </span>
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          <p className="text-sm leading-6 text-slate-600">{description}</p>
        </div>
        <p className="rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-500">{meta}</p>
      </div>
      <div className="pt-5">
        {href.startsWith('#') ? (
          <a href={href} className={linkClassName}>
            {ctaLabel}
          </a>
        ) : (
          <Link to={href} className={linkClassName}>
            {ctaLabel}
          </Link>
        )}
      </div>
    </Card>
  )
}
