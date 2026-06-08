import { Button } from '@/shared/components/Button'
import { exportarEquiposCSV } from '@/features/equipos-docentes/services/api'
import type { EquiposFilters } from '@/features/equipos-docentes/types'

interface ExportCsvButtonProps {
  filters?: EquiposFilters
}

export function ExportCsvButton({ filters }: ExportCsvButtonProps) {
  const handleExport = async () => {
    try {
      const blob = await exportarEquiposCSV(filters)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'equipos-docentes.csv'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch {
      // Error al exportar
    }
  }

  return (
    <Button variant="secondary" onClick={handleExport}>
      Exportar CSV
    </Button>
  )
}
