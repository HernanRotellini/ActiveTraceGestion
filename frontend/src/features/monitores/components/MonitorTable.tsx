import type { MonitorItem } from '@/features/monitores/types/monitores'

interface MonitorTableProps {
  items?: MonitorItem[]
}

export function MonitorTable({ items }: MonitorTableProps) {
  if (!items || items.length === 0) {
    return (
      <div className="p-12 text-center">
        <p className="text-gray-500">No hay alumnos en el monitor.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-600">
            <th className="p-4 pb-2">Alumno</th>
            <th className="p-4 pb-2">Email</th>
            <th className="p-4 pb-2">Comisión</th>
            <th className="p-4 pb-2">Regional</th>
            <th className="p-4 pb-2">Total actividades</th>
            <th className="p-4 pb-2">Aprobadas</th>
            <th className="p-4 pb-2">Pendientes</th>
            <th className="p-4 pb-2">Estado</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.entrada_padron_id} className="border-b last:border-0 hover:bg-gray-50">
              <td className="p-4 py-2 font-medium">{item.alumno_nombre}</td>
              <td className="p-4 py-2 text-gray-500">{item.email}</td>
              <td className="p-4 py-2">{item.comision ?? '-'}</td>
              <td className="p-4 py-2">{item.regional ?? '-'}</td>
              <td className="p-4 py-2">{item.total_actividades}</td>
              <td className="p-4 py-2">{item.aprobadas}</td>
              <td className="p-4 py-2">{item.pendientes}</td>
              <td className="p-4 py-2">
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                  item.atrasado ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                }`}>
                  {item.atrasado ? 'Atrasado' : 'Al día'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
