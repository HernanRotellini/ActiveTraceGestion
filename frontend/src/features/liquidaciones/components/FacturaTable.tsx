import { Button } from '@/shared/components/Button'
import type { Factura } from '@/features/liquidaciones/types'

interface FacturaTableProps {
  facturas: Factura[]
  onCambiarEstado: (id: string, estado: 'pendiente' | 'abonada') => void
  loading?: boolean
}

export function FacturaTable({ facturas, onCambiarEstado, loading }: FacturaTableProps) {
  if (facturas.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 p-12 text-center">
        <p className="text-gray-500">No hay facturas registradas.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Docente</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Período</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">Importe</th>
            <th className="px-4 py-3 text-center font-medium text-gray-600">Estado</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Creada</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Abonada</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {facturas.map((f) => (
            <tr key={f.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-medium text-gray-900">{f.docente_nombre}</td>
              <td className="px-4 py-3 text-gray-600">{f.periodo}</td>
              <td className="px-4 py-3 text-right font-medium text-gray-900">${f.importe.toLocaleString()}</td>
              <td className="px-4 py-3 text-center">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                    f.estado === 'abonada' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}
                >
                  {f.estado}
                </span>
              </td>
              <td className="px-4 py-3 text-gray-500">{new Date(f.creada_en).toLocaleDateString()}</td>
              <td className="px-4 py-3 text-gray-500">{f.abonada_en ? new Date(f.abonada_en).toLocaleDateString() : '-'}</td>
              <td className="px-4 py-3 text-right">
                {f.estado === 'pendiente' && (
                  <Button
                    variant="ghost"
                    onClick={() => onCambiarEstado(f.id, 'abonada')}
                    loading={loading}
                  >
                    Marcar abonada
                  </Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
