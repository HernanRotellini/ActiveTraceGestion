import { Card } from '@/shared/components/Card'
import { useCalificaciones } from '@/features/comisiones/hooks/useCalificaciones'
import { useAtrasados } from '@/features/comisiones/hooks/useAtrasados'
import { Spinner } from '@/shared/components/Spinner'

interface ReportesRapidosProps {
  comisionId: string
}

export function ReportesRapidos({ comisionId }: ReportesRapidosProps) {
  const { data: calificaciones, isLoading: loadingCalif } = useCalificaciones(comisionId)
  const { data: atrasados, isLoading: loadingAtrasos } = useAtrasados(comisionId)

  if (loadingCalif || loadingAtrasos) return <Spinner />

  const totalAlumnos = calificaciones?.length ?? 0
  const aprobados = calificaciones?.filter((c) => c.estado === 'aprobado').length ?? 0
  const desaprobados = calificaciones?.filter((c) => c.estado === 'desaprobado').length ?? 0
  const sinNota = calificaciones?.filter((c) => c.estado === 'sin_nota').length ?? 0
  const totalAtrasados = atrasados?.total ?? 0
  const promedioGeneral =
    calificaciones && calificaciones.length > 0
      ? calificaciones.reduce((acc, c) => acc + (c.nota ?? 0), 0) / calificaciones.filter((c) => c.nota !== null).length
      : 0

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Reportes Rápidos</h2>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-4">
          <p className="text-sm text-gray-500">Total Alumnos</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{totalAlumnos}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">Aprobados</p>
          <p className="mt-1 text-2xl font-bold text-green-600">{aprobados}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">Desaprobados</p>
          <p className="mt-1 text-2xl font-bold text-red-600">{desaprobados}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">Sin Nota</p>
          <p className="mt-1 text-2xl font-bold text-gray-500">{sinNota}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">Atrasados</p>
          <p className="mt-1 text-2xl font-bold text-orange-600">{totalAtrasados}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">Promedio General</p>
          <p className="mt-1 text-2xl font-bold text-primary-600">
            {Number.isFinite(promedioGeneral) ? promedioGeneral.toFixed(2) : '-'}
          </p>
        </Card>
      </div>
    </div>
  )
}
