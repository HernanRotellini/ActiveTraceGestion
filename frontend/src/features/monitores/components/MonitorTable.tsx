import type { MonitorAlumno } from '@/features/monitores/types/monitores'

interface MonitorTableProps {
  data?: MonitorAlumno[]
}

const estadoStyles: Record<string, string> = {
  al_dia: 'bg-green-100 text-green-700',
  atrasado: 'bg-yellow-100 text-yellow-700',
  critico: 'bg-red-100 text-red-700',
}

const estadoLabels: Record<string, string> = {
  al_dia: 'Al día',
  atrasado: 'Atrasado',
  critico: 'Crítico',
}

export function MonitorTable({ data }: MonitorTableProps) {
  if (!data || data.length === 0) {
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
            <th className="p-4 pb-2">Comisión</th>
            <th className="p-4 pb-2">Materia</th>
            <th className="p-4 pb-2">Act. Pendientes</th>
            <th className="p-4 pb-2">Entregas Sin Corregir</th>
            <th className="p-4 pb-2">Promedio</th>
            <th className="p-4 pb-2">Asistencias</th>
            <th className="p-4 pb-2">Estado</th>
            <th className="p-4 pb-2">Última Actividad</th>
          </tr>
        </thead>
        <tbody>
          {data.map((a) => (
            <tr key={a.alumno_id} className="border-b last:border-0 hover:bg-gray-50">
              <td className="p-4 py-2 font-medium">{a.alumno_nombre}</td>
              <td className="p-4 py-2">{a.comision}</td>
              <td className="p-4 py-2">{a.materia}</td>
              <td className="p-4 py-2">{a.actividades_pendientes}</td>
              <td className="p-4 py-2">{a.entregas_sin_corregir}</td>
              <td className="p-4 py-2">
                {a.promedio_actual !== null ? a.promedio_actual.toFixed(2) : '-'}
              </td>
              <td className="p-4 py-2">{a.asistencias}%</td>
              <td className="p-4 py-2">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${estadoStyles[a.estado]}`}
                >
                  {estadoLabels[a.estado]}
                </span>
              </td>
              <td className="p-4 py-2 text-gray-500">
                {a.ultima_actividad ?? '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
