import { Button } from '@/shared/components/Button'
import type { FacturaResponse } from '@/features/liquidaciones/types'

interface FacturaTableProps {
  facturas: FacturaResponse[]
  onMarcarAbonada: (id: string) => void
  onEliminar: (id: string) => void
  loading?: boolean
}

export function FacturaTable({ facturas, onMarcarAbonada, onEliminar, loading }: FacturaTableProps) {
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
            <th className="px-4 py-3 text-left font-medium text-gray-600">Usuario</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Período</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Detalle</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">Tamaño</th>
            <th className="px-4 py-3 text-center font-medium text-gray-600">Estado</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Creada</th>
            <th className="px-4 py-3 text-left font-medium text-gray-600">Abonada</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {facturas.map((f) => {
            const usuarioNombre = [f.usuario_nombre, f.usuario_apellidos]
              .filter((value): value is string => Boolean(value))
              .join(' ')
              .trim() || f.usuario_id
            const usuarioRoles = Array.isArray(f.usuario_roles) ? f.usuario_roles : []

            return (
              <tr key={f.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <p className="font-medium text-gray-900">{usuarioNombre}</p>
                  <p className="text-xs text-gray-500">
                    {usuarioRoles.length > 0 ? usuarioRoles.join(', ') : 'Sin rol'}
                  </p>
                </td>
                <td className="px-4 py-3 text-gray-900">{f.periodo}</td>
                <td className="px-4 py-3 text-gray-600">{f.detalle}</td>
                <td className="px-4 py-3 text-right text-gray-500">{(f.archivo_size_bytes / 1024).toFixed(1)} KB</td>
                <td className="px-4 py-3 text-center">
                  <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                    f.estado === 'Abonada' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {f.estado}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">{new Date(f.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3 text-gray-500">{f.abonada_at ? new Date(f.abonada_at).toLocaleDateString() : '-'}</td>
                <td className="px-4 py-3 text-right">
                  <div className="flex justify-end gap-2">
                    {f.estado === 'Pendiente' && (
                      <Button variant="ghost" onClick={() => onMarcarAbonada(f.id)} loading={loading}>
                        Abonar
                      </Button>
                    )}
                    <Button variant="danger" onClick={() => onEliminar(f.id)}>
                      Eliminar
                    </Button>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
