import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'
import { categoryColor, NEEDS_REVIEW, percent } from '../utils/format.js'

export function Spinner({ label = 'Loading…' }) {
  return (
    <div className="flex items-center justify-center gap-2 py-16 text-sm text-navy-500" role="status">
      <Loader2 className="h-4 w-4 animate-spin" /> {label}
    </div>
  )
}

export function Alert({ type = 'error', title, children }) {
  const styles =
    type === 'success'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-900'
      : type === 'warning'
        ? 'border-amber-200 bg-amber-50 text-amber-900'
        : 'border-red-200 bg-red-50 text-red-900'
  const Icon = type === 'success' ? CheckCircle2 : AlertCircle
  return (
    <div className={`flex gap-3 rounded-lg border p-4 text-sm ${styles}`} role={type === 'error' ? 'alert' : 'status'}>
      <Icon className="mt-0.5 h-4 w-4 shrink-0" />
      <div>
        {title && <p className="font-medium">{title}</p>}
        {children && <div className={title ? 'mt-1' : ''}>{children}</div>}
      </div>
    </div>
  )
}

export function EmptyState({ title, children, action }) {
  return (
    <div className="px-6 py-14 text-center">
      <p className="font-medium text-navy-800">{title}</p>
      {children && <p className="mx-auto mt-1 max-w-sm text-sm text-navy-500">{children}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold text-navy-950">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-navy-500">{subtitle}</p>}
      </div>
      {actions}
    </div>
  )
}

export function StatCard({ label, value, hint }) {
  return (
    <div className="card p-5">
      <p className="text-sm text-navy-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-navy-950">{value}</p>
      {hint && <p className="mt-1 text-xs text-navy-400">{hint}</p>}
    </div>
  )
}

// Shows the category, or "Needs Manual Review" when the model was not confident enough.
export function CategoryBadge({ doc, size = 'sm' }) {
  const label = doc.needs_review ? NEEDS_REVIEW : doc.category
  const color = categoryColor(label)
  const pad = size === 'lg' ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs'
  return (
    <span
      className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full font-medium ${pad}`}
      style={{ backgroundColor: `${color}1a`, color }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
      {label}
    </span>
  )
}

export function ConfidenceBar({ value, muted = false, showLabel = true }) {
  const color = muted ? '#d97706' : value >= 0.75 ? '#0f9d8a' : '#2f5bea'
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-full min-w-[60px] overflow-hidden rounded-full bg-navy-100">
        <div className="h-full rounded-full" style={{ width: `${Math.round(value * 100)}%`, backgroundColor: color }} />
      </div>
      {showLabel && <span className="w-10 text-right text-xs tabular-nums text-navy-600">{percent(value)}</span>}
    </div>
  )
}
