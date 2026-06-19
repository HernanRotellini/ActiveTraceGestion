import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Toast } from '@/shared/components/Toast'
import { exportarEquiposCSV } from '@/features/equipos-docentes/services/api'
import type { ExportarEquiposParams } from '@/features/equipos-docentes/types'

interface ExportCsvButtonProps {
  params: ExportarEquiposParams
}

export function ExportCsvButton({ params }: ExportCsvButtonProps) {
  const [error, setError] = useState<string | null>(null)

  const handleExport = async () => {
    try {
      const blob = await exportarEquiposCSV(params)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'equipos-docentes.csv'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch {
      setError('No se pudo exportar el CSV.')
    }
  }

  return (
    <>
      {error && <Toast message={error} variant="error" onClose={() => setError(null)} />}
      <Button variant="secondary" onClick={handleExport}>
        Exportar CSV
      </Button>
    </>
  )
}
