import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { useEncuentro } from '@/features/encuentros/hooks/useEncuentros'

export default function EncuentroDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: encuentro, isLoading } = useEncuentro(id!)

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!encuentro) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Encuentro no encontrado</h1>
        <Link to="/coordinacion/encuentros" className="text-primary-600 hover:text-primary-800">Volver</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <Link to="/coordinacion/encuentros" className="text-sm text-primary-600 hover:text-primary-800">&larr; Volver</Link>
        <h1 className="text-2xl font-bold text-gray-900 mt-1">{encuentro.comision_nombre}</h1>
        <p className="text-sm text-gray-500">{encuentro.materia_nombre} - {new Date(encuentro.fecha).toLocaleDateString()}</p>
      </div>

      <Card className="p-4">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div><span className="text-gray-500">Aula:</span><span className="ml-2 text-gray-900">{encuentro.aula}</span></div>
          <div><span className="text-gray-500">Duración:</span><span className="ml-2 text-gray-900">{encuentro.duracion_minutos} min</span></div>
          <div><span className="text-gray-500">Tema:</span><span className="ml-2 text-gray-900">{encuentro.tema ?? '-'}</span></div>
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Slots Horarios</h2>
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Inicio</th>
                <th className="px-4 py-3">Fin</th>
                <th className="px-4 py-3">Docente</th>
                <th className="px-4 py-3">Tema</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {encuentro.slots?.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900">{s.hora_inicio}</td>
                  <td className="px-4 py-3 text-gray-900">{s.hora_fin}</td>
                  <td className="px-4 py-3 text-gray-600">{s.docente_nombre ?? 'Sin asignar'}</td>
                  <td className="px-4 py-3 text-gray-600">{s.tema ?? '-'}</td>
                </tr>
              ))}
              {(!encuentro.slots || encuentro.slots.length === 0) && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">Sin slots registrados.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Instancias de Dictado</h2>
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Materia</th>
                <th className="px-4 py-3">Comisión</th>
                <th className="px-4 py-3">Docente</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {encuentro.instancias?.map((inst) => (
                <tr key={inst.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900">{inst.materia_nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{inst.comision_nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{inst.docente_nombre}</td>
                </tr>
              ))}
              {(!encuentro.instancias || encuentro.instancias.length === 0) && (
                <tr><td colSpan={3} className="px-4 py-8 text-center text-gray-500">Sin instancias registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Guardias</h2>
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Docente</th>
                <th className="px-4 py-3">Inicio</th>
                <th className="px-4 py-3">Fin</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {encuentro.guardias?.map((g) => (
                <tr key={g.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900">{g.docente_nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{g.hora_inicio}</td>
                  <td className="px-4 py-3 text-gray-600">{g.hora_fin}</td>
                </tr>
              ))}
              {(!encuentro.guardias || encuentro.guardias.length === 0) && (
                <tr><td colSpan={3} className="px-4 py-8 text-center text-gray-500">Sin guardias registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
