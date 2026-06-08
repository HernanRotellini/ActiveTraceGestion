import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { useEquipo, useActualizarEquipo, useActualizarVigencia } from '@/features/equipos-docentes/hooks/useEquipos'
import { AsignacionMasivaModal } from '@/features/equipos-docentes/components/AsignacionMasivaModal'
import { ClonarModal } from '@/features/equipos-docentes/components/ClonarModal'
import { ExportCsvButton } from '@/features/equipos-docentes/components/ExportCsvButton'

export default function EquipoDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: equipo, isLoading } = useEquipo(id!)
  const actualizarEquipo = useActualizarEquipo(id!)
  const actualizarVigencia = useActualizarVigencia()
  const [showMasiva, setShowMasiva] = useState(false)
  const [showClonar, setShowClonar] = useState(false)

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!equipo) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Equipo no encontrado</h1>
        <Link to="/coordinacion/equipos-docentes" className="text-primary-600 hover:text-primary-800">
          Volver al listado
        </Link>
      </div>
    )
  }

  const toggleEstado = () => {
    actualizarEquipo.mutate({ estado: equipo.estado === 'activo' ? 'inactivo' : 'activo' })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link to="/coordinacion/equipos-docentes" className="text-sm text-primary-600 hover:text-primary-800">
            &larr; Volver
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">{equipo.materia_nombre}</h1>
          <p className="text-sm text-gray-500">{equipo.carrera}</p>
        </div>
        <div className="flex items-center gap-3">
          <ExportCsvButton />
          <Button variant="secondary" onClick={() => setShowClonar(true)}>Clonar</Button>
          <Button variant="secondary" onClick={() => setShowMasiva(true)}>Asignación masiva</Button>
          <Button variant={equipo.estado === 'activo' ? 'danger' : 'primary'} onClick={toggleEstado}>
            {equipo.estado === 'activo' ? 'Desactivar' : 'Activar'}
          </Button>
        </div>
      </div>

      <Card className="p-4">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Estado:</span>
            <span className={`ml-2 inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
              equipo.estado === 'activo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
            }`}>{equipo.estado}</span>
          </div>
          <div><span className="text-gray-500">Creado:</span><span className="ml-2 text-gray-900">{new Date(equipo.creado_en).toLocaleDateString()}</span></div>
          <div><span className="text-gray-500">Actualizado:</span><span className="ml-2 text-gray-900">{new Date(equipo.actualizado_en).toLocaleDateString()}</span></div>
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Asignaciones</h2>
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Usuario</th>
                <th className="px-4 py-3">Rol</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3">Desde</th>
                <th className="px-4 py-3">Hasta</th>
                <th className="px-4 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {equipo.asignaciones?.map((asig) => (
                <tr key={asig.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{asig.usuario_nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{asig.rol}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      asig.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>{asig.activo ? 'Activo' : 'Inactivo'}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{new Date(asig.desde).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-gray-600">{asig.hasta ? new Date(asig.hasta).toLocaleDateString() : '-'}</td>
                  <td className="px-4 py-3">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => actualizarVigencia.mutate({ id: asig.id, payload: { desde: asig.desde, hasta: asig.activo ? new Date().toISOString() : undefined } })}
                    >
                      {asig.activo ? 'Finalizar' : 'Reactivar'}
                    </Button>
                  </td>
                </tr>
              ))}
              {(!equipo.asignaciones || equipo.asignaciones.length === 0) && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    Sin asignaciones.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {showMasiva && <AsignacionMasivaModal equipoId={equipo.id} onClose={() => setShowMasiva(false)} />}
      {showClonar && <ClonarModal origenEquipoId={equipo.id} onClose={() => setShowClonar(false)} />}
    </div>
  )
}
