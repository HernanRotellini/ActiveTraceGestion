import type { AtrasadosResponse } from '@/features/comisiones/types/calificaciones'

interface AtrasadosTableProps {
  data?: AtrasadosResponse
}

export function AtrasadosTable({ data }: AtrasadosTableProps) {
  if (!data || data.items.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-500">No hay alumnos atrasados.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">
        Alumnos Atrasados <span className="text-sm font-normal text-gray-500">({data.total} total)</span>
      </h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-600">
            <th className="pb-2">Alumno</th>
            <th className="pb-2">Materia</th>
            <th className="pb-2">Días de atraso</th>
            <th className="pb-2">Última actividad</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((item, idx) => (
            <tr key={`${item.alumno_id}-${idx}`} className="border-b last:border-0">
              <td className="py-2">{item.alumno_nombre}</td>
              <td className="py-2">{item.materia}</td>
              <td className="py-2">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                    item.atraso_dias > 30
                      ? 'bg-red-100 text-red-700'
                      : item.atraso_dias > 15
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-orange-100 text-orange-700'
                  }`}
                >
                  {item.atraso_dias} días
                </span>
              </td>
              <td className="py-2 text-gray-500">{item.ultima_actividad ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
