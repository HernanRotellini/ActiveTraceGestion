import type { RankingItem } from '@/features/comisiones/types/calificaciones'

interface RankingTableProps {
  data?: RankingItem[]
}

export function RankingTable({ data }: RankingTableProps) {
  if (!data || data.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-500">No hay datos de ranking disponibles.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Ranking de Alumnos</h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-600">
            <th className="pb-2">#</th>
            <th className="pb-2">Alumno</th>
            <th className="pb-2">Promedio</th>
            <th className="pb-2">Actividades</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr
              key={item.alumno_id}
              className={`border-b last:border-0 ${
                item.puesto <= 3 ? 'bg-primary-50' : ''
              }`}
            >
              <td className="py-2 font-medium">
                {item.puesto <= 3 ? (
                  <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700">
                    {item.puesto}
                  </span>
                ) : (
                  item.puesto
                )}
              </td>
              <td className="py-2">{item.alumno_nombre}</td>
              <td className="py-2 font-medium">{item.promedio.toFixed(2)}</td>
              <td className="py-2 text-gray-500">{item.total_actividades}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
