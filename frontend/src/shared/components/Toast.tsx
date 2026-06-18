import { useEffect } from 'react'

type ToastVariant = 'error' | 'success'

interface ToastProps {
  message: string
  variant?: ToastVariant
  onClose: () => void
  autoCloseMs?: number
}

const variantStyles: Record<ToastVariant, {
  container: string
  icon: string
  button: string
  role: 'alert' | 'status'
  closeLabel: string
}> = {
  error: {
    container: 'border-red-200 bg-red-50 text-red-800',
    icon: 'text-red-700',
    button: 'text-red-700 hover:bg-red-100 focus:ring-red-500',
    role: 'alert',
    closeLabel: 'Cerrar error',
  },
  success: {
    container: 'border-emerald-200 bg-emerald-50 text-emerald-800',
    icon: 'text-emerald-700',
    button: 'text-emerald-700 hover:bg-emerald-100 focus:ring-emerald-500',
    role: 'status',
    closeLabel: 'Cerrar mensaje',
  },
}

function ErrorIcon() {
  return (
    <svg className="h-5 w-5" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01M10.3 4.3 2.8 17.4A1.8 1.8 0 0 0 4.4 20h15.2a1.8 1.8 0 0 0 1.6-2.6L13.7 4.3a1.9 1.9 0 0 0-3.4 0Z" />
    </svg>
  )
}

function SuccessIcon() {
  return (
    <svg className="h-5 w-5" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75 9 17.25 19.5 6.75" />
    </svg>
  )
}

function CloseIcon() {
  return (
    <svg className="h-4 w-4" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M18 6 6 18" />
    </svg>
  )
}

export function Toast({ message, variant = 'error', onClose, autoCloseMs = 5000 }: ToastProps) {
  useEffect(() => {
    if (!message) return
    const timeoutId = window.setTimeout(onClose, autoCloseMs)
    return () => window.clearTimeout(timeoutId)
  }, [autoCloseMs, message, onClose])

  if (!message) return null

  const styles = variantStyles[variant]
  const Icon = variant === 'success' ? SuccessIcon : ErrorIcon

  return (
    <div
      className={`fixed right-4 top-4 z-50 max-w-sm rounded-lg border px-4 py-3 text-sm shadow-lg ${styles.container}`}
      role={styles.role}
      aria-live={variant === 'error' ? 'assertive' : 'polite'}
    >
      <div className="flex items-start gap-3">
        <span className={`mt-0.5 shrink-0 ${styles.icon}`}>
          <Icon />
        </span>
        <p className="flex-1">{message}</p>
        <button
          type="button"
          onClick={onClose}
          className={`rounded px-1 focus:outline-none focus:ring-2 ${styles.button}`}
          aria-label={styles.closeLabel}
        >
          <CloseIcon />
        </button>
      </div>
    </div>
  )
}
