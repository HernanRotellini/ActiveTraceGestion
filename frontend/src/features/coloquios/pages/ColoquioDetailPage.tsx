import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { Toast } from '@/shared/components/Toast'
import {
  useColoquio,
  useReservas,
  useResultados,
  useRegistrarResultado,
  useCerrarConvocatoria,
} from '@/features/coloquios/hooks/useColoquios'
import type { ResultadoCreate } from '@/features/coloquios/types'

export default function ColoquioDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: coloquio, isLoading } = useColoquio(id!)
  const { data: reservas } = useReservas(id!)
  const { data: resultados } = useResultados(id!)
  const registrar = useRegistrarResultado(id!)
  const cerrar = useCerrarConvocatoria()
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)
  const [notaForm, setNotaForm] = useState<{ alumno_id: string; nota_final: string } | null>(null)

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!coloquio) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">Convocatoria no encontrada</h1>
        <Link to="/coordinacion/coloquios" className="text-primary-600 hover:text-primary-800">Volver</Link>
      </div>
    )
  }

  const handleCerrar = async () => {
    if (!id) return
    if (!window.confirm('¿Confirmar cierre de la convocatoria?')) return
    try {
      await cerrar.mutateAsync(id)
      setToast({ message: 'Convocatoria cerrada.', variant: 'success' })
    } catch {
      setToast({ message: 'Error al cerrar la convocatoria.', variant: 'error' })
    }
  }

  const handleRegistrarNota = async (payload: ResultadoCreate) => {
    try {
      await registrar.mutateAsync(payload)
      setToast({ message: 'Nota registrada.', variant: 'success' })
      setNotaForm(null)
    } catch {
      setToast({ message: 'Error al registrar la nota.', variant: 'error' })
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {toast && <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />}

      <div className="flex items-start justify-between">
        <div>
          <Link to="/coordinacion/coloquios" className="text-sm text-primary-600 hover:text-primary-800">&larr; Volver</Link>
          <h1 className="mt-1 text-2xl font-bold text-gray-900">{coloquio.instancia}</h1>
          <p className="text-sm text-gray-500">Tipo: {coloquio.tipo}</p>
        </div>
        {coloquio.estado !== 'cerrado' && (
          <Button variant="danger" size="sm" onClick={handleCerrar} loading={cerrar.isPending}>
            Cerrar convocatoria
          </Button>
        )}
      </div>

      <Card className="p-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Estado:</span>
            <span className={`ml-2 inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
              coloquio.estado === 'cerrado' ? 'bg-gray-100 text-gray-600' : 'bg-green-100 text-green-700'
            }`}>{coloquio.estado}</span>
          </div>
          <div>
            <span className="text-gray-500">Creada:</span>
            <span className="ml-2 text-gray-900">{new Date(coloquio.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Turnos</h2>
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Fecha</th>
                <th className="px-4 py-3">Inicio</th>
                <th className="px-4 py-3">Fin</th>
                <th className="px-4 py-3">Cupo máximo</th>
                <th className="px-4 py-3">Cupo restante</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {coloquio.turnos.map((t) => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900">{new Date(t.fecha).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-gray-600">{t.hora_inicio ?? '-'}</td>
                  <td className="px-4 py-3 text-gray-600">{t.hora_fin ?? '-'}</td>
                  <td className="px-4 py-3 text-center text-gray-600">{t.cupo_maximo}</td>
                  <td className="px-4 py-3 text-center text-gray-600">{t.cupo_restante}</td>
                </tr>
              ))}
              {coloquio.turnos.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">Sin turnos registrados.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Reservas</h2>
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Alumno (ID)</th>
                <th className="px-4 py-3">Turno (ID)</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {(reservas ?? []).map((r) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-700 font-mono text-xs">{r.alumno_id.slice(0, 8)}</td>
                  <td className="px-4 py-3 text-gray-600 font-mono text-xs">{r.turno_id.slice(0, 8)}</td>
                  <td className="px-4 py-3 text-gray-600">{r.estado}</td>
                  <td className="px-4 py-3 text-gray-600">{new Date(r.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {(!reservas || reservas.length === 0) && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">Sin reservas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Resultados</h2>
        <Button
          size="sm"
          onClick={() => setNotaForm({ alumno_id: '', nota_final: '' })}
        >
          Registrar nota
        </Button>
      </div>
      {notaForm && (
        <Card className="p-4">
          <div className="flex items-end gap-3">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">UUID del alumno</label>
              <input
                type="text"
                value={notaForm.alumno_id}
                onChange={(e) => setNotaForm({ ...notaForm, alumno_id: e.target.value })}
                className="block w-64 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="xxxxxxxx-xxxx-..."
              />
            </div>
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Nota final</label>
              <input
                type="text"
                value={notaForm.nota_final}
                onChange={(e) => setNotaForm({ ...notaForm, nota_final: e.target.value })}
                className="block w-32 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Ej: 7 o Ausente"
              />
            </div>
            <Button
              size="sm"
              onClick={() => handleRegistrarNota(notaForm)}
              loading={registrar.isPending}
              disabled={!notaForm.alumno_id || !notaForm.nota_final}
            >
              Guardar
            </Button>
            <Button size="sm" variant="secondary" onClick={() => setNotaForm(null)}>Cancelar</Button>
          </div>
        </Card>
      )}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Alumno (ID)</th>
                <th className="px-4 py-3">Nota final</th>
                <th className="px-4 py-3">Registrado</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {(resultados ?? []).map((r) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs text-gray-700">{r.alumno_id.slice(0, 8)}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{r.nota_final}</td>
                  <td className="px-4 py-3 text-gray-600">{new Date(r.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {(!resultados || resultados.length === 0) && (
                <tr><td colSpan={3} className="px-4 py-8 text-center text-gray-500">Sin resultados registrados.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
