import type { EntregaPendiente } from '@/features/entregas-sin-corregir/types/entregas'

interface EntregasTableProps {
  data?: EntregaPendiente[]
}

export function EntregasTable({ data }: EntregasTableProps) {
  if (!data || data.length === 0) {
    return (
      <div className="p-12 text-center">
        <p className="text-gray-500">No hay entregas pendientes de corrección.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-600">
            <th className="p-4 pb-2">Alumno</th>
            <th className="p-4 pb-2">Actividad</th>
            <th className="p-4 pb-2">Materia</th>
            <th className="p-4 pb-2">Fecha de entrega</th>
            <th className="p-4 pb-2">Días pendiente</th>
          </tr>
        </thead>
        <tbody>
          {data.map((e) => (
            <tr key={e.entrega_id} className="border-b last:border-0 hover:bg-gray-50">
              <td className="p-4 py-2">{e.alumno_nombre}</td>
              <td className="p-4 py-2">{e.actividad}</td>
              <td className="p-4 py-2">{e.materia}</td>
              <td className="p-4 py-2 text-gray-500">
                {new Date(e.fecha_entrega).toLocaleDateString()}
              </td>
              <td className="p-4 py-2">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                    e.dias_pendiente > 7
                      ? 'bg-red-100 text-red-700'
                      : e.dias_pendiente > 3
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {e.dias_pendiente} días
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
