import type { RankingResponse } from '@/features/comisiones/types/calificaciones'

interface RankingTableProps {
  data?: RankingResponse
}

export function RankingTable({ data }: RankingTableProps) {
  if (!data || data.items.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-500">No hay datos de ranking disponibles.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Ranking de Alumnos</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-600">
              <th className="pb-2">#</th>
              <th className="pb-2">Alumno</th>
              <th className="pb-2">Actividades aprobadas</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => (
              <tr
                key={item.entrada_padron_id}
                className={`border-b last:border-0 ${item.ranking <= 3 ? 'bg-primary-50' : ''}`}
              >
                <td className="py-2 font-medium">
                  {item.ranking <= 3 ? (
                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700">
                      {item.ranking}
                    </span>
                  ) : (
                    item.ranking
                  )}
                </td>
                <td className="py-2">{item.alumno_nombre}</td>
                <td className="py-2 text-gray-500">{item.actividades_aprobadas}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
