import type { EntregaPendiente } from '@/features/entregas-sin-corregir/types/entregas'

interface EntregasTableProps {
  data?: EntregaPendiente[]
}

function DiasBadge({ dias }: { dias: number }) {
  return (
    <span
      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
        dias > 7
          ? 'bg-red-100 text-red-700'
          : dias > 3
            ? 'bg-yellow-100 text-yellow-700'
            : 'bg-gray-100 text-gray-700'
      }`}
    >
      {dias} días
    </span>
  )
}

export function EntregasTable({ data }: EntregasTableProps) {
  if (!data || data.length === 0) {
    return (
      <div className="p-12 text-center">
        <p className="text-gray-500">No hay entregas pendientes de corrección.</p>
      </div>
    )
  }

  // Agrupar por actividad: la actividad es el eje principal del listado (HU-02).
  const grupos = new Map<string, EntregaPendiente[]>()
  for (const entrega of data) {
    const lista = grupos.get(entrega.actividad) ?? []
    lista.push(entrega)
    grupos.set(entrega.actividad, lista)
  }
  const actividades = Array.from(grupos.keys()).sort((a, b) => a.localeCompare(b))

  return (
    <div className="overflow-x-auto">
      <p className="px-4 pt-4 text-sm text-gray-600">
        {data.length} {data.length === 1 ? 'entrega pendiente' : 'entregas pendientes'} en{' '}
        {actividades.length} {actividades.length === 1 ? 'actividad' : 'actividades'}.
      </p>
      {actividades.map((actividad) => {
        const entregas = grupos.get(actividad) ?? []
        return (
          <section key={actividad} className="mt-2">
            <h3 className="bg-gray-50 px-4 py-2 text-sm font-semibold text-gray-800">
              {actividad}
              <span className="ml-2 text-xs font-normal text-gray-500">({entregas.length})</span>
            </h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-600">
                  <th className="p-4 pb-2">Alumno</th>
                  <th className="p-4 pb-2">Materia</th>
                  <th className="p-4 pb-2">Comisión</th>
                  <th className="p-4 pb-2">Fecha de entrega</th>
                  <th className="p-4 pb-2">Días pendiente</th>
                </tr>
              </thead>
              <tbody>
                {entregas.map((e) => (
                  <tr key={e.entrega_id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="p-4 py-2">{e.alumno_nombre}</td>
                    <td className="p-4 py-2">{e.materia}</td>
                    <td className="p-4 py-2">{e.comision}</td>
                    <td className="p-4 py-2 text-gray-500">
                      {new Date(e.fecha_entrega).toLocaleDateString()}
                    </td>
                    <td className="p-4 py-2">
                      <DiasBadge dias={e.dias_pendiente} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )
      })}
    </div>
  )
}
