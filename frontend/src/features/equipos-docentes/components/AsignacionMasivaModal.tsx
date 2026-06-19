import { useState } from 'react'
import { useCarreras, useCohortes, useMaterias } from '@/features/admin/hooks/useAdmin'
import { DocenteSelector } from '@/features/equipos-docentes/components/DocenteSelector'
import { useCrearAsignacionesEquipo } from '@/features/equipos-docentes/hooks/useEquipos'
import type { RolAsignacionDocente } from '@/features/equipos-docentes/types'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Combobox } from '@/shared/components/Combobox'
import { Toast } from '@/shared/components/Toast'

interface AsignacionMasivaModalProps {
  onClose: () => void
}

const ROLES: Array<{ value: RolAsignacionDocente; label: string }> = [
  { value: 'PROFESOR', label: 'Profesor' },
  { value: 'TUTOR', label: 'Tutor' },
  { value: 'COORDINADOR', label: 'Coordinador' },
  { value: 'NEXO', label: 'Nexo' },
]

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

export function AsignacionMasivaModal({ onClose }: AsignacionMasivaModalProps) {
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [usuarioIds, setUsuarioIds] = useState<string[]>([])
  const [rol, setRol] = useState<RolAsignacionDocente>('PROFESOR')
  const [desde, setDesde] = useState(todayIsoDate())
  const [hasta, setHasta] = useState('')
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const mutation = useCrearAsignacionesEquipo()

  const { data: carrerasResp, isLoading: loadingCarreras } = useCarreras()
  const { data: cohortesResp, isLoading: loadingCohortes } = useCohortes(carreraId || undefined)
  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias(carreraId || undefined, cohorteId || undefined)

  const carreraItems = (carrerasResp?.items ?? []).map((carrera) => ({ value: carrera.id, label: carrera.nombre }))
  const cohorteItems = (cohortesResp?.items ?? []).map((cohorte) => ({ value: cohorte.id, label: `${cohorte.nombre} (${cohorte.anio})` }))
  const materiaItems = (materiasResp?.items ?? []).map((materia) => ({ value: materia.id, label: `${materia.nombre} (${materia.codigo})` }))

  const handleSubmit = async () => {
    if (usuarioIds.length === 0 || !carreraId || !cohorteId || !materiaId || !desde) {
      setErrorMsg('Completa todos los campos requeridos.')
      return
    }

    try {
      await mutation.mutateAsync({
        usuario_ids: usuarioIds,
        materia_id: materiaId,
        carrera_id: carreraId,
        cohorte_id: cohorteId,
        rol,
        desde,
        hasta: hasta || undefined,
      })
      onClose()
    } catch (error) {
      setErrorMsg(error instanceof Error ? error.message : 'No se pudo realizar la asignacion masiva.')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <Card className="w-full max-w-lg p-6" onClick={(event: React.MouseEvent) => event.stopPropagation()}>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Asignacion masiva</h2>

        {errorMsg && (
          <div className="mb-4">
            <Toast message={errorMsg} variant="error" onClose={() => setErrorMsg(null)} />
          </div>
        )}

        <div className="space-y-4">
          <Combobox
            label="Carrera *"
            items={carreraItems}
            value={carreraId}
            onChange={(value) => {
              setCarreraId(value)
              setCohorteId('')
              setMateriaId('')
            }}
            placeholder="Buscar carrera..."
            isLoading={loadingCarreras}
          />

          <Combobox
            label="Cohorte *"
            items={cohorteItems}
            value={cohorteId}
            onChange={(value) => {
              setCohorteId(value)
              setMateriaId('')
            }}
            placeholder={carreraId ? 'Buscar cohorte...' : 'Selecciona una carrera'}
            isLoading={loadingCohortes}
            disabled={!carreraId}
          />

          <Combobox
            label="Materia *"
            items={materiaItems}
            value={materiaId}
            onChange={setMateriaId}
            placeholder={cohorteId ? 'Buscar materia...' : 'Selecciona carrera y cohorte'}
            isLoading={loadingMaterias}
            disabled={!carreraId || !cohorteId}
          />

          <DocenteSelector selectedIds={usuarioIds} onChange={setUsuarioIds} />

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Rol *</label>
              <select
                value={rol}
                onChange={(event) => setRol(event.target.value as RolAsignacionDocente)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {ROLES.map((role) => (
                  <option key={role.value} value={role.value}>{role.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vigencia desde *</label>
              <input
                type="date"
                value={desde}
                onChange={(event) => setDesde(event.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vigencia hasta</label>
              <input
                type="date"
                value={hasta}
                min={desde}
                onChange={(event) => setHasta(event.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSubmit} loading={mutation.isPending}>Asignar</Button>
        </div>
      </Card>
    </div>
  )
}
