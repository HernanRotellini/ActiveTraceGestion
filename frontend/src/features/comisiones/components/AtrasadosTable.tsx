import type { AtrasadoItem } from '@/features/comisiones/types/calificaciones'

interface AtrasadosTableProps {
  data?: AtrasadoItem[]
}

export function AtrasadosTable({ data }: AtrasadosTableProps) {
  if (!data || data.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-500">No hay alumnos atrasados.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">
        Alumnos Atrasados <span className="text-sm font-normal text-gray-500">({data.length} total)</span>
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-600">
              <th className="pb-2">Alumno</th>
              <th className="pb-2">Actividades atrasadas</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={item.entrada_padron_id} className="border-b last:border-0">
                <td className="py-2">{item.alumno_nombre}</td>
                <td className="py-2 text-gray-600">
                  {item.actividades_atrasadas.map((actividad) => (
                    <span
                      key={`${item.entrada_padron_id}-${actividad.actividad}`}
                      className="mr-2 inline-flex rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700"
                    >
                      {actividad.actividad}: {actividad.motivo}
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
