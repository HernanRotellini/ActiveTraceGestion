import { Button } from '@/shared/components/Button'

interface ConfirmDialogProps {
  open: boolean
  titulo: string
  mensaje: string
  confirmLabel?: string
  isLoading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open,
  titulo,
  mensaje,
  confirmLabel = 'Confirmar',
  isLoading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
    >
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h2 id="confirm-dialog-title" className="text-lg font-semibold text-gray-900">
          {titulo}
        </h2>
        <p className="mt-2 text-sm text-gray-600">{mensaje}</p>
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="secondary" onClick={onCancel} type="button" disabled={isLoading}>
            Volver
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={isLoading} type="button">
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  )
}
