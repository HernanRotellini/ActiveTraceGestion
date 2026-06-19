import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { useReportesRapidos } from '@/features/comisiones/hooks/useReportesRapidos'

interface ReportesRapidosProps {
  materiaId: string
}

export function ReportesRapidos({ materiaId }: ReportesRapidosProps) {
  const { data, isLoading } = useReportesRapidos(materiaId)

  if (isLoading) return <Spinner />

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Reportes Rápidos</h2>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-4">
          <p className="text-sm text-gray-500">Total Alumnos</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{data?.total_alumnos ?? 0}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">Calificaciones</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{data?.total_calificaciones ?? 0}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">Aprobados</p>
          <p className="mt-1 text-2xl font-bold text-green-600">{data?.total_aprobados ?? 0}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">No aprobados</p>
          <p className="mt-1 text-2xl font-bold text-red-600">{data?.total_no_aprobados ?? 0}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-gray-500">Promedio General</p>
          <p className="mt-1 text-2xl font-bold text-primary-600">
            {data ? data.promedio_general.toFixed(2) : '-'}
          </p>
        </Card>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-600">
              <th className="pb-2">Actividad</th>
              <th className="pb-2">Presentados</th>
              <th className="pb-2">Promedio</th>
              <th className="pb-2">Min</th>
              <th className="pb-2">Max</th>
            </tr>
          </thead>
          <tbody>
            {data?.desglose_por_actividad.map((item) => (
              <tr key={item.actividad} className="border-b last:border-0">
                <td className="py-2">{item.actividad}</td>
                <td className="py-2">{item.presentado}</td>
                <td className="py-2">{item.promedio?.toFixed(2) ?? '-'}</td>
                <td className="py-2">{item.min?.toFixed(2) ?? '-'}</td>
                <td className="py-2">{item.max?.toFixed(2) ?? '-'}</td>
              </tr>
            ))}
            {(!data || data.desglose_por_actividad.length === 0) && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-500">
                  No hay reportes disponibles.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
