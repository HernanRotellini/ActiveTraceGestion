import { Button } from '@/shared/components/Button'

interface ExportButtonProps {
  onExport: () => void
  isLoading: boolean
  disabled?: boolean
}

function DownloadIcon() {
  return (
    <svg className="h-5 w-5" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v12m0 0 4-4m-4 4-4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
    </svg>
  )
}

export function ExportButton({ onExport, isLoading, disabled = false }: ExportButtonProps) {
  return (
    <div className="group relative inline-flex">
      <Button
        variant="secondary"
        onClick={onExport}
        loading={isLoading}
        disabled={disabled}
        aria-label="Exportar entregas sin corregir a CSV"
      >
        <DownloadIcon />
        Exportar
      </Button>
      <span className="pointer-events-none absolute left-1/2 top-full z-10 mt-1 -translate-x-1/2 whitespace-nowrap rounded bg-gray-900 px-2 py-1 text-xs text-white opacity-0 shadow-sm transition-opacity group-hover:opacity-100">
        Descargar CSV con los filtros aplicados
      </span>
    </div>
  )
}
