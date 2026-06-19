import { useQuery, useMutation } from '@tanstack/react-query'
import {
  detectarEntregas,
  exportarEntregas,
  importarReporteLms,
} from '@/features/entregas-sin-corregir/services/entregas'

function descargarBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export function useEntregasPendientes(comision?: string) {
  const query = useQuery({
    queryKey: ['entregasPendientes', comision],
    queryFn: () => detectarEntregas(comision),
    staleTime: 30_000,
  })

  const exportMutation = useMutation({
    mutationFn: () => exportarEntregas(comision),
    onSuccess: (blob) => {
      const fecha = new Date().toISOString().slice(0, 10)
      descargarBlob(blob, `entregas-sin-corregir-${fecha}.csv`)
    },
  })

  const importMutation = useMutation({
    mutationFn: ({ materiaId, cohorteId, file }: { materiaId: string; cohorteId: string; file: File }) =>
      importarReporteLms(materiaId, cohorteId, file),
  })

  return { query, exportMutation, importMutation }
}
