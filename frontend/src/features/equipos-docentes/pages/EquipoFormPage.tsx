import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Combobox } from '@/shared/components/Combobox'
import { Toast } from '@/shared/components/Toast'
import { Spinner } from '@/shared/components/Spinner'
import { useCrearAsignacionesEquipo } from '@/features/equipos-docentes/hooks/useEquipos'
import { useCarreras, useCohortes, useMaterias, useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { RolAsignacionDocente } from '@/features/equipos-docentes/types'

const ROLES: Array<{ value: RolAsignacionDocente; label: string }> = [
  { value: 'PROFESOR', label: 'Profesor' },
  { value: 'TUTOR', label: 'Tutor' },
  { value: 'COORDINADOR', label: 'Coordinador' },
  { value: 'NEXO', label: 'Nexo' },
]

const DOCENTE_ROLES = new Set(['PROFESOR', 'TUTOR', 'COORDINADOR', 'NEXO'])

function splitComisiones(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

export default function EquipoFormPage() {
  const navigate = useNavigate()
  const crearAsignaciones = useCrearAsignacionesEquipo()

  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [rol, setRol] = useState<RolAsignacionDocente>('PROFESOR')
  const [desde, setDesde] = useState(todayIsoDate())
  const [hasta, setHasta] = useState('')
  const [comisiones, setComisiones] = useState('')
  const [usuarioId, setUsuarioId] = useState('')
  const [usuarioIds, setUsuarioIds] = useState<string[]>([])
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  const { data: carrerasResp, isLoading: loadingCarreras } = useCarreras()
  const { data: cohortesResp, isLoading: loadingCohortes } = useCohortes(carreraId || undefined)
  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias(carreraId || undefined, cohorteId || undefined)
  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()

  const carreraItems = (carrerasResp?.items ?? [])
    .filter((carrera) => carrera.estado === 'activa')
    .map((carrera) => ({ value: carrera.id, label: `${carrera.nombre} (${carrera.codigo})` }))

  const cohorteItems = (cohortesResp?.items ?? [])
    .filter((cohorte) => cohorte.estado === 'activa')
    .map((cohorte) => ({ value: cohorte.id, label: `${cohorte.nombre} (${cohorte.anio})` }))

  const materiaItems = (materiasResp?.items ?? [])
    .filter((materia) => materia.estado === 'activa')
    .map((materia) => ({ value: materia.id, label: `${materia.nombre} (${materia.codigo})` }))

  const usuariosDocentes = useMemo(() => {
    return (usuariosResp?.items ?? []).filter((usuario) => {
      if (usuario.estado !== 'activo') return false
      if (!usuario.roles?.length) return true
      return usuario.roles.some((userRole) => DOCENTE_ROLES.has(userRole))
    })
  }, [usuariosResp?.items])

  const usuarioItems = usuariosDocentes
    .filter((usuario) => !usuarioIds.includes(usuario.id))
    .map((usuario) => ({
      value: usuario.id,
      label: `${usuario.nombre} ${usuario.apellidos} (${usuario.email})`,
    }))

  const selectedUsuarios = usuariosDocentes.filter((usuario) => usuarioIds.includes(usuario.id))

  const handleCarreraChange = (value: string) => {
    setCarreraId(value)
    setCohorteId('')
    setMateriaId('')
  }

  const handleCohorteChange = (value: string) => {
    setCohorteId(value)
    setMateriaId('')
  }

  const addUsuario = () => {
    if (!usuarioId || usuarioIds.includes(usuarioId)) return
    setUsuarioIds((current) => [...current, usuarioId])
    setUsuarioId('')
  }

  const removeUsuario = (id: string) => {
    setUsuarioIds((current) => current.filter((item) => item !== id))
  }

  const validate = () => {
    if (usuarioIds.length === 0) return 'Seleccioná al menos un docente.'
    if (!carreraId) return 'Seleccioná una carrera.'
    if (!cohorteId) return 'Seleccioná una cohorte.'
    if (!materiaId) return 'Seleccioná una materia.'
    if (!desde) return 'Indicá la fecha de inicio de vigencia.'
    if (hasta && hasta < desde) return 'La fecha de fin no puede ser anterior al inicio.'
    return null
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    const validationError = validate()
    if (validationError) {
      setToast({ message: validationError, variant: 'error' })
      return
    }

    try {
      await crearAsignaciones.mutateAsync({
        usuario_ids: usuarioIds,
        materia_id: materiaId,
        carrera_id: carreraId,
        cohorte_id: cohorteId,
        rol,
        comisiones: splitComisiones(comisiones),
        desde,
        hasta: hasta || undefined,
      })
      setToast({ message: 'Asignaciones creadas correctamente.', variant: 'success' })
      window.setTimeout(() => navigate('/coordinacion/equipos-docentes'), 800)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'No se pudieron crear las asignaciones.'
      setToast({ message, variant: 'error' })
    }
  }

  const isLoadingCatalogs = loadingCarreras || loadingCohortes || loadingMaterias || loadingUsuarios

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {toast && (
        <Toast
          message={toast.message}
          variant={toast.variant}
          onClose={() => setToast(null)}
        />
      )}

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Nueva asignación de equipo</h1>
        <p className="mt-1 text-sm text-gray-500">
          Asigná docentes a una materia, carrera, cohorte, rol, vigencia y comisiones.
        </p>
      </div>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <section className="grid gap-4 md:grid-cols-2">
            <Combobox
              label="Carrera *"
              items={carreraItems}
              value={carreraId}
              onChange={handleCarreraChange}
              placeholder="Buscar carrera..."
              isLoading={loadingCarreras}
            />

            <Combobox
              label="Cohorte *"
              items={cohorteItems}
              value={cohorteId}
              onChange={handleCohorteChange}
              placeholder={carreraId ? 'Buscar cohorte...' : 'Seleccioná una carrera'}
              isLoading={loadingCohortes}
              disabled={!carreraId}
            />

            <div className="md:col-span-2">
              <Combobox
                label="Materia *"
                items={materiaItems}
                value={materiaId}
                onChange={setMateriaId}
                placeholder={cohorteId ? 'Buscar materia...' : 'Seleccioná carrera y cohorte'}
                isLoading={loadingMaterias}
                disabled={!carreraId || !cohorteId}
              />
            </div>
          </section>

          <section className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">Docentes *</label>
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

            {selectedUsuarios.length > 0 ? (
              <div className="rounded-lg border border-gray-200">
                {selectedUsuarios.map((usuario) => (
                  <div key={usuario.id} className="flex items-center justify-between border-b px-3 py-2 last:border-b-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{usuario.nombre} {usuario.apellidos}</p>
                      <p className="text-xs text-gray-500">{usuario.email}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeUsuario(usuario.id)}
                      className="rounded px-2 py-1 text-sm text-red-600 hover:bg-red-50"
                    >
                      Quitar
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">Todavía no agregaste docentes.</p>
            )}
          </section>

          <section className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Rol *</label>
              <select
                value={rol}
                onChange={(event) => setRol(event.target.value as RolAsignacionDocente)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {ROLES.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Comisiones</label>
              <input
                type="text"
                value={comisiones}
                onChange={(event) => setComisiones(event.target.value)}
                placeholder="Ej: A, B, Turno noche"
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vigencia desde *</label>
              <input
                type="date"
                value={desde}
                onChange={(event) => setDesde(event.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vigencia hasta</label>
              <input
                type="date"
                value={hasta}
                onChange={(event) => setHasta(event.target.value)}
                min={desde}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </section>

          {isLoadingCatalogs && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Spinner />
              Cargando datos...
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => navigate('/coordinacion/equipos-docentes')}>
              Cancelar
            </Button>
            <Button type="submit" loading={crearAsignaciones.isPending}>
              Crear asignación
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
