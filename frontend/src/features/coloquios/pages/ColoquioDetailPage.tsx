import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { useColoquio, useConfirmarReserva, useCancelarReserva, useRegistrarResultado } from '@/features/coloquios/hooks/useColoquios'
import type { ResultadoColoquio } from '@/features/coloquios/types'

const RESULTADOS: ResultadoColoquio[] = ['pendiente', 'aprobado', 'desaprobado', 'ausente']

export default function ColoquioDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: coloquio, isLoading } = useColoquio(id!)
  const confirmar = useConfirmarReserva()
  const cancelar = useCancelarReserva()
  const registrarResultado = useRegistrarResultado()

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!coloquio) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Coloquio no encontrado</h1>
        <Link to="/coordinacion/coloquios" className="text-primary-600 hover:text-primary-800">Volver</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <Link to="/coordinacion/coloquios" className="text-sm text-primary-600 hover:text-primary-800">&larr; Volver</Link>
        <h1 className="text-2xl font-bold text-gray-900 mt-1">{coloquio.materia_nombre}</h1>
        <p className="text-sm text-gray-500">{coloquio.comision_nombre} - {new Date(coloquio.fecha).toLocaleDateString()}</p>
      </div>

      <Card className="p-4">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Estado:</span>
            <span className={`ml-2 inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
              coloquio.estado === 'finalizado' ? 'bg-green-100 text-green-700'
              : coloquio.estado === 'en_curso' ? 'bg-blue-100 text-blue-700'
              : 'bg-yellow-100 text-yellow-700'
            }`}>{coloquio.estado}</span>
          </div>
          <div><span className="text-gray-500">Aula:</span><span className="ml-2 text-gray-900">{coloquio.aula}</span></div>
          <div><span className="text-gray-500">Observaciones:</span><span className="ml-2 text-gray-900">{coloquio.observaciones ?? '-'}</span></div>
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Reservas</h2>
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Alumno</th>
                <th className="px-4 py-3">Confirmado</th>
                <th className="px-4 py-3">Resultado</th>
                <th className="px-4 py-3">Nota</th>
                <th className="px-4 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {coloquio.reservas?.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{r.alumno_nombre}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      r.confirmado ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>{r.confirmado ? 'Sí' : 'No'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={r.resultado}
                      onChange={(e) => registrarResultado.mutate({
                        coloquioId: coloquio.id,
                        reservaId: r.id,
                        resultado: e.target.value as ResultadoColoquio,
                      })}
                      className="block w-32 rounded-lg border border-gray-300 px-2 py-1 text-xs focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      {RESULTADOS.map((res) => (
                        <option key={res} value={res}>{res}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{r.nota ?? '-'}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => confirmar.mutate({ coloquioId: coloquio.id, reservaId: r.id })}
                        disabled={r.confirmado}
                      >
                        Confirmar
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => cancelar.mutate({ coloquioId: coloquio.id, reservaId: r.id })}
                        disabled={!r.confirmado}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
              {(!coloquio.reservas || coloquio.reservas.length === 0) && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">Sin reservas registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
