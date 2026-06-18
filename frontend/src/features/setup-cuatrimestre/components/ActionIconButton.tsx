import type { ReactNode } from 'react'
import { Button } from '@/shared/components/Button'

interface ActionIconButtonProps {
  label: string
  onClick: () => void
  children: ReactNode
  loading?: boolean
  disabled?: boolean
}

export function ActionIconButton({
  label,
  onClick,
  children,
  loading = false,
  disabled = false,
}: ActionIconButtonProps) {
  return (
    <div className="group relative inline-flex">
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={onClick}
        loading={loading}
        disabled={disabled}
        aria-label={label}
        title={label}
        className="h-10 w-10 p-0"
      >
        {children}
      </Button>
      <span className="pointer-events-none absolute left-1/2 top-full z-10 mt-1 -translate-x-1/2 whitespace-nowrap rounded bg-gray-900 px-2 py-1 text-xs text-white opacity-0 shadow-sm transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
        {label}
      </span>
    </div>
  )
}
