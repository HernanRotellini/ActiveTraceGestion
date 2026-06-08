import type { NotasFinalesItem } from '@/features/comisiones/types/calificaciones'

interface NotasFinalesTableProps {
  data?: NotasFinalesItem[]
}

const condicionStyles: Record<string, string> = {
  promocionado: 'bg-green-100 text-green-700',
  regular: 'bg-yellow-100 text-yellow-700',
  libre: 'bg-red-100 text-red-700',
}

export function NotasFinalesTable({ data }: NotasFinalesTableProps) {
  if (!data || data.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-500">No hay notas finales registradas.</p>
      </div>
    )
  }

  const grouped = {
    promocionado: data.filter((i) => i.condicion === 'promocionado'),
    regular: data.filter((i) => i.condicion === 'regular'),
    libre: data.filter((i) => i.condicion === 'libre'),
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Notas Finales</h2>

      {(['promocionado', 'regular', 'libre'] as const).map((cond) => {
        const items = grouped[cond]
        if (items.length === 0) return null

        return (
          <div key={cond}>
            <h3 className="mb-2 text-sm font-medium text-gray-700 capitalize">{cond}</h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-600">
                  <th className="pb-2">Alumno</th>
                  <th className="pb-2">Nota Final</th>
                  <th className="pb-2">Condición</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.alumno_id} className="border-b last:border-0">
                    <td className="py-2">{item.alumno_nombre}</td>
                    <td className="py-2 font-medium">
                      {item.nota_final !== null ? item.nota_final.toFixed(2) : '-'}
                    </td>
                    <td className="py-2">
                      <span
                        className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${condicionStyles[item.condicion]}`}
                      >
                        {item.condicion}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      })}
    </div>
  )
}
