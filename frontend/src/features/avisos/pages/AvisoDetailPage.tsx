import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { Toast } from '@/shared/components/Toast'
import { useAviso, useActualizarAviso, useDesactivarAviso, useAvisoStats } from '@/features/avisos/hooks/useAvisos'
import { AckProgressBar } from '@/features/avisos/components/AckProgressBar'

const SEVERIDAD_BADGES: Record<string, string> = {
  Info: 'bg-blue-100 text-blue-700',
  Advertencia: 'bg-yellow-100 text-yellow-700',
  Critico: 'bg-red-100 text-red-700',
}

const ALCANCE_LABELS: Record<string, string> = {
  Global: 'Global',
  PorMateria: 'Por materia',
  PorCohorte: 'Por cohorte',
  PorRol: 'Por rol',
}

export default function AvisoDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: aviso, isLoading } = useAviso(id!)
  const { data: stats } = useAvisoStats(id!)
  const actualizar = useActualizarAviso(id!)
  const desactivar = useDesactivarAviso()
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!aviso) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Aviso no encontrado</h1>
        <Link to="/coordinacion/avisos" className="text-primary-600 hover:text-primary-800">Volver</Link>
      </div>
    )
  }

  const handleActivar = async () => {
    try {
      await actualizar.mutateAsync({ activo: true })
      setToast({ message: 'Aviso activado.', variant: 'success' })
    } catch {
      setToast({ message: 'No se pudo activar el aviso.', variant: 'error' })
    }
  }

  const handleDesactivar = async () => {
    try {
      await desactivar.mutateAsync(aviso.id)
      setToast({ message: 'Aviso desactivado.', variant: 'success' })
    } catch {
      setToast({ message: 'No se pudo desactivar el aviso.', variant: 'error' })
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {toast && <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />}

      <div className="flex items-center justify-between">
        <div>
          <Link to="/coordinacion/avisos" className="text-sm text-primary-600 hover:text-primary-800">
            &larr; Volver
          </Link>
          <h1 className="mt-1 text-2xl font-bold text-gray-900">{aviso.titulo}</h1>
        </div>
        <div className="flex items-center gap-3">
          <Link to={`/coordinacion/avisos/${id}/editar`}>
            <Button variant="secondary">Editar</Button>
          </Link>
          {!aviso.activo && (
            <Button onClick={handleActivar} loading={actualizar.isPending}>
              Activar
            </Button>
          )}
          {aviso.activo && (
            <Button variant="danger" onClick={handleDesactivar} loading={desactivar.isPending}>
              Desactivar
            </Button>
          )}
        </div>
      </div>

      <Card className="p-6 space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${aviso.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
            {aviso.activo ? 'Activo' : 'Inactivo'}
          </span>
          <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${SEVERIDAD_BADGES[aviso.severidad] ?? 'bg-gray-100 text-gray-600'}`}>
            {aviso.severidad}
          </span>
          <span className="text-sm text-gray-500">Alcance: {ALCANCE_LABELS[aviso.alcance] ?? aviso.alcance}</span>
          {aviso.rol_destino && <span className="text-sm text-gray-500">Rol: {aviso.rol_destino}</span>}
          {aviso.requiere_ack && <span className="text-sm font-medium text-amber-600">Requiere confirmación</span>}
        </div>

        <div className="flex gap-6 text-xs text-gray-400">
          <span>Inicio: {new Date(aviso.inicio_en).toLocaleDateString()}</span>
          {aviso.fin_en && <span>Vence: {new Date(aviso.fin_en).toLocaleDateString()}</span>}
          <span>Creado: {new Date(aviso.created_at).toLocaleDateString()}</span>
        </div>

        <div className="whitespace-pre-wrap text-gray-800">{aviso.cuerpo}</div>
      </Card>

      {aviso.requiere_ack && stats && (
        <>
          <h2 className="text-lg font-semibold text-gray-900">Seguimiento de lectura</h2>
          <Card className="p-4">
            <AckProgressBar
              total_acks={stats.total_acks}
              sin_confirmar={stats.usuarios_sin_confirmar?.length ?? 0}
            />
          </Card>
        </>
      )}
    </div>
  )
}
