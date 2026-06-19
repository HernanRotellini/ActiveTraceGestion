import type { MouseEvent } from 'react'
import { useId } from 'react'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'

interface ConfirmActionModalProps {
  title: string
  description: string
  confirmLabel: string
  onConfirm: () => void
  onClose: () => void
  loading?: boolean
  danger?: boolean
}

export function ConfirmActionModal({
  title,
  description,
  confirmLabel,
  onConfirm,
  onClose,
  loading = false,
  danger = false,
}: ConfirmActionModalProps) {
  const titleId = useId()
  const descriptionId = useId()

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
    >
      <Card
        className="w-full max-w-lg overflow-hidden"
        onClick={(event: MouseEvent) => event.stopPropagation()}
      >
        <div className="border-b border-gray-200 bg-white px-6 py-4">
          <h2 id={titleId} className="text-lg font-semibold text-gray-900">{title}</h2>
        </div>
        <div className="space-y-4 bg-white px-6 py-5">
          <p id={descriptionId} className="text-sm leading-6 text-gray-600">{description}</p>
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Esta accion impacta datos del periodo actual y se registra en auditoria.
          </div>
        </div>
        <div className="flex justify-end gap-3 border-t border-gray-200 bg-gray-50 px-6 py-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            type="button"
            variant={danger ? 'danger' : 'primary'}
            onClick={onConfirm}
            loading={loading}
          >
            {confirmLabel}
          </Button>
        </div>
      </Card>
    </div>
  )
}
