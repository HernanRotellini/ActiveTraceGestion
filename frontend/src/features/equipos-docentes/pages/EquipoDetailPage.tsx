import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/shared/components/Button'
import { AsignacionMasivaModal } from '@/features/equipos-docentes/components/AsignacionMasivaModal'
import { ClonarModal } from '@/features/equipos-docentes/components/ClonarModal'

export default function EquipoDetailPage() {
  const [showMasiva, setShowMasiva] = useState(false)
  const [showClonar, setShowClonar] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link to="/coordinacion/equipos-docentes" className="text-sm text-primary-600 hover:text-primary-800">
            &larr; Volver al listado
          </Link>
          <h1 className="mt-1 text-2xl font-bold text-gray-900">Gestión de equipo</h1>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={() => setShowClonar(true)}>Clonar equipo</Button>
          <Button variant="secondary" onClick={() => setShowMasiva(true)}>Asignación masiva</Button>
        </div>
      </div>

      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        La vista de detalle por equipo no está disponible aún. Para ver las asignaciones existentes usá el listado.
        Las acciones de asignación masiva y clonar equipo están disponibles en los botones de arriba.
      </div>

      {showMasiva && <AsignacionMasivaModal onClose={() => setShowMasiva(false)} />}
      {showClonar && <ClonarModal onClose={() => setShowClonar(false)} />}
    </div>
  )
}
