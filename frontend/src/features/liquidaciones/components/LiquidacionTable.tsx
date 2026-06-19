import type { LiquidacionResponse } from '@/features/liquidaciones/types'

interface LiquidacionTableProps {
  items: LiquidacionResponse[]
}

export function LiquidacionTable({ items }: LiquidacionTableProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 p-12 text-center">
        <p className="text-gray-500">No hay liquidaciones registradas.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Usuario</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Período</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Rol</th>
            <th className="px-4 py-3 text-center font-medium text-gray-600">Estado</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">Base</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">Plus</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">Total</th>
            <th className="px-4 py-3 text-center font-medium text-gray-600">NEXO</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {items.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-mono text-xs text-gray-600">{item.usuario_id}</td>
              <td className="px-4 py-3 text-gray-900">{item.periodo}</td>
              <td className="px-4 py-3 text-gray-600">{item.rol}</td>
              <td className="px-4 py-3 text-center">
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                  item.estado === 'Cerrada' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                }`}>
                  {item.estado}
                </span>
              </td>
              <td className="px-4 py-3 text-right text-gray-900">${Number(item.monto_base).toLocaleString()}</td>
              <td className="px-4 py-3 text-right text-gray-900">${Number(item.monto_plus).toLocaleString()}</td>
              <td className="px-4 py-3 text-right font-medium text-gray-900">${Number(item.monto_total).toLocaleString()}</td>
              <td className="px-4 py-3 text-center">
                {item.es_nexo && <span className="inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">NEXO</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
