import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Combobox } from '@/shared/components/Combobox'
import { Toast } from '@/shared/components/Toast'
import { useCrearAsignacionesEquipo } from '@/features/equipos-docentes/hooks/useEquipos'
import { useUsuarios, useCarreras, useCohortes, useMaterias } from '@/features/admin/hooks/useAdmin'
import type { RolAsignacionDocente } from '@/features/equipos-docentes/types'

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
  const [usuarioId, setUsuarioId] = useState('')
  const [rol, setRol] = useState<RolAsignacionDocente>('PROFESOR')
  const [desde, setDesde] = useState(todayIsoDate())
  const [hasta, setHasta] = useState('')
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const mutation = useCrearAsignacionesEquipo()

  const { data: carrerasResp, isLoading: loadingCarreras } = useCarreras()
  const { data: cohortesResp, isLoading: loadingCohortes } = useCohortes(carreraId || undefined)
  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias(carreraId || undefined, cohorteId || undefined)
  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()

  const carreraItems = (carrerasResp?.items ?? []).map((c) => ({ value: c.id, label: c.nombre }))
  const cohorteItems = (cohortesResp?.items ?? []).map((c) => ({ value: c.id, label: `${c.nombre} (${c.anio})` }))
  const materiaItems = (materiasResp?.items ?? []).map((m) => ({ value: m.id, label: `${m.nombre} (${m.codigo})` }))
  const usuarioItems = (usuariosResp?.items ?? [])
    .filter((u) => !usuarioIds.includes(u.id))
    .map((u) => ({ value: u.id, label: `${u.nombre} ${u.apellidos} (${u.email})` }))

  const selectedUsuarios = (usuariosResp?.items ?? []).filter((u) => usuarioIds.includes(u.id))

  const addUsuario = () => {
    if (!usuarioId || usuarioIds.includes(usuarioId)) return
    setUsuarioIds((prev) => [...prev, usuarioId])
    setUsuarioId('')
  }

  const removeUsuario = (id: string) => setUsuarioIds((prev) => prev.filter((i) => i !== id))

  const handleSubmit = async () => {
    if (usuarioIds.length === 0 || !carreraId || !cohorteId || !materiaId || !desde) {
      setErrorMsg('Completá todos los campos requeridos.')
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
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'No se pudo realizar la asignación masiva.')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <Card className="w-full max-w-lg p-6" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Asignación Masiva</h2>

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
            onChange={(v) => { setCarreraId(v); setCohorteId(''); setMateriaId('') }}
            placeholder="Buscar carrera..."
            isLoading={loadingCarreras}
          />
          <Combobox
            label="Cohorte *"
            items={cohorteItems}
            value={cohorteId}
            onChange={(v) => { setCohorteId(v); setMateriaId('') }}
            placeholder={carreraId ? 'Buscar cohorte...' : 'Seleccioná una carrera'}
            isLoading={loadingCohortes}
            disabled={!carreraId}
          />
          <Combobox
            label="Materia *"
            items={materiaItems}
            value={materiaId}
            onChange={setMateriaId}
            placeholder={cohorteId ? 'Buscar materia...' : 'Seleccioná carrera y cohorte'}
            isLoading={loadingMaterias}
            disabled={!carreraId || !cohorteId}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Docentes *</label>
            <div className="flex gap-2">
              <div className="flex-1">
                <Combobox
                  label=""
                  items={usuarioItems}
                  value={usuarioId}
                  onChange={setUsuarioId}
                  placeholder="Buscar docente..."
                  isLoading={loadingUsuarios}
                />
              </div>
              <Button type="button" variant="secondary" onClick={addUsuario} disabled={!usuarioId}>
                Agregar
              </Button>
            </div>
            {selectedUsuarios.length > 0 && (
              <div className="mt-2 rounded-lg border border-gray-200">
                {selectedUsuarios.map((u) => (
                  <div key={u.id} className="flex items-center justify-between border-b px-3 py-1.5 last:border-b-0">
                    <span className="text-sm text-gray-800">{u.nombre} {u.apellidos}</span>
                    <button type="button" onClick={() => removeUsuario(u.id)} className="text-xs text-red-600 hover:text-red-800">
                      Quitar
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Rol *</label>
              <select
                value={rol}
                onChange={(e) => setRol(e.target.value as RolAsignacionDocente)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vigencia desde *</label>
              <input
                type="date"
                value={desde}
                onChange={(e) => setDesde(e.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vigencia hasta</label>
              <input
                type="date"
                value={hasta}
                min={desde}
                onChange={(e) => setHasta(e.target.value)}
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
