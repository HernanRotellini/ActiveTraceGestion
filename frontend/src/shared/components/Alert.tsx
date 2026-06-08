import type { ReactNode } from 'react'

type AlertVariant = 'success' | 'error' | 'info'

interface AlertProps {
  variant: AlertVariant
  children: ReactNode
  className?: string
}

const variantStyles: Record<AlertVariant, string> = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
}

export function Alert({ variant, children, className = '' }: AlertProps) {
  return (
    <div
      className={`rounded-lg border px-4 py-3 text-sm ${variantStyles[variant]} ${className}`}
      role="alert"
    >
      {children}
    </div>
  )
}
