import type { NotasFinalesResponse } from '@/features/comisiones/types/calificaciones'

interface NotasFinalesTableProps {
  data?: NotasFinalesResponse
  hasActivities: boolean
}

export function NotasFinalesTable({ data, hasActivities }: NotasFinalesTableProps) {
  if (!hasActivities) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-500">Importá calificaciones para calcular notas finales.</p>
      </div>
    )
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-500">No hay notas finales registradas.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Notas Finales</h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-600">
              <th className="pb-2">Alumno</th>
              <th className="pb-2">Promedio</th>
              <th className="pb-2">Condición</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => (
              <tr key={item.entrada_padron_id} className="border-b last:border-0">
                <td className="py-2">{item.alumno_nombre}</td>
                <td className="py-2 font-medium">{item.promedio.toFixed(2)}</td>
                <td className="py-2">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      item.aprobado ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {item.aprobado ? 'Aprobado' : 'No aprobado'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
