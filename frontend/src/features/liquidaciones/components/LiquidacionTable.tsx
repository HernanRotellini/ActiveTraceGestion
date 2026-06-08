import type { LiquidacionItem } from '@/features/liquidaciones/types'

interface LiquidacionTableProps {
  items: LiquidacionItem[]
  segmento: string
  titulo: string
  subtotal: number
}

export function LiquidacionTable({ items, segmento, titulo, subtotal }: LiquidacionTableProps) {
  const filtrados = items.filter((i) => i.segmento === segmento)

  if (filtrados.length === 0) return null

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold text-gray-900">{titulo}</h3>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Docente</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Materia</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Comisión</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Rol</th>
              <th className="px-4 py-3 text-right font-medium text-gray-600">Horas</th>
              <th className="px-4 py-3 text-right font-medium text-gray-600">Valor hora</th>
              <th className="px-4 py-3 text-right font-medium text-gray-600">Subtotal</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtrados.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{item.docente_nombre}</td>
                <td className="px-4 py-3 text-gray-600">{item.materia}</td>
                <td className="px-4 py-3 text-gray-600">{item.comision}</td>
                <td className="px-4 py-3 text-gray-600">{item.rol}</td>
                <td className="px-4 py-3 text-right text-gray-900">{item.horas}</td>
                <td className="px-4 py-3 text-right text-gray-900">${item.valor_hora.toLocaleString()}</td>
                <td className="px-4 py-3 text-right font-medium text-gray-900">${item.subtotal.toLocaleString()}</td>
              </tr>
            ))}
            <tr className="bg-gray-50 font-semibold">
              <td colSpan={6} className="px-4 py-3 text-right text-gray-700">Subtotal {titulo}</td>
              <td className="px-4 py-3 text-right text-gray-900">${subtotal.toLocaleString()}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
