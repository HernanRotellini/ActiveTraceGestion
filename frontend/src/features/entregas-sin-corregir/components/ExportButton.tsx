import { Button } from '@/shared/components/Button'

interface ExportButtonProps {
  onExport: () => void
  isLoading: boolean
}

export function ExportButton({ onExport, isLoading }: ExportButtonProps) {
  return (
    <Button variant="secondary" onClick={onExport} loading={isLoading}>
      Exportar
    </Button>
  )
}
