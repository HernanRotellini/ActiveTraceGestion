import { useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { ApiError } from '@/shared/types/api'
import {
  useActualizarPeriodoMutation,
  useAgregarFechaMutation,
  useAgregarProgramaMutation,
  useActivarPeriodo,
  useCrearPeriodo,
  useDesactivarPeriodo,
  useEliminarPeriodo,
  usePeriodosList,
  useQuitarFechaMutation,
  useQuitarProgramaMutation,
} from '@/features/setup-cuatrimestre/hooks/usePeriodos'
import type { PeriodoAcademico, PeriodoPayload } from '@/features/setup-cuatrimestre/types'
import { useMaterias } from '@/features/admin/hooks/useAdmin'

function EditIcon() {
  return (
    <svg className="h-5 w-5" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487 19.5 7.125M18.225 3.125a1.75 1.75 0 0 1 2.475 2.475L8.25 18.05 4.5 19.125l1.075-3.75 12.65-12.25Z" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg className="h-5 w-5" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 7h12M9 7V5.75A1.75 1.75 0 0 1 10.75 4h2.5A1.75 1.75 0 0 1 15 5.75V7m-7.5 0 .75 11.25A1.75 1.75 0 0 0 10 20h4a1.75 1.75 0 0 0 1.75-1.75L16.5 7M10 11v5M14 11v5" />
    </svg>
  )
}

function PlusIcon() {
  return (
    <svg className="h-4 w-4" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 5v14M5 12h14" />
    </svg>
  )
}

function IconButton({
  label,
  onClick,
  children,
  loading = false,
}: {
  label: string
  onClick: () => void
  children: ReactNode
  loading?: boolean
}) {
  return (
    <div className="group relative inline-flex">
      <Button
        variant="ghost"
        size="sm"
        onClick={onClick}
        loading={loading}
        aria-label={label}
        className="h-10 w-10 p-0"
      >
        {children}
      </Button>
      <span className="pointer-events-none absolute left-1/2 top-full z-10 mt-1 -translate-x-1/2 whitespace-nowrap rounded bg-gray-900 px-2 py-1 text-xs text-white opacity-0 shadow-sm transition-opacity group-hover:opacity-100">
        {label}
      </span>
    </div>
  )
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-AR', { timeZone: 'UTC' }).format(new Date(value))
}

function toInputDate(value: string) {
  return value.slice(0, 10)
}

function getPeriodoErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.message.includes('fecha_fin')) {
      return 'La fecha de fin debe ser posterior o igual a la fecha de inicio.'
    }
    if (error.status === 404) {
      return 'No se encontro el período seleccionado.'
    }
    return error.message || 'No se pudo guardar el período.'
  }
  return 'No se pudo guardar el período.'
}

export default function SetupCuatrimestrePage() {
  const { data, isLoading, error } = usePeriodosList()
  const { data: materias } = useMaterias()
  const crearPeriodo = useCrearPeriodo()
  const actualizarPeriodo = useActualizarPeriodoMutation()
  const activarPeriodo = useActivarPeriodo()
  const desactivarPeriodo = useDesactivarPeriodo()
  const eliminarPeriodo = useEliminarPeriodo()
  const agregarFecha = useAgregarFechaMutation()
  const quitarFecha = useQuitarFechaMutation()
  const agregarPrograma = useAgregarProgramaMutation()
  const quitarPrograma = useQuitarProgramaMutation()

  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [formError, setFormError] = useState('')
  const [fechaPeriodoId, setFechaPeriodoId] = useState<string | null>(null)
  const [fechaKey, setFechaKey] = useState('')
  const [fechaLabel, setFechaLabel] = useState('')
  const [fechaValor, setFechaValor] = useState('')
  const [fechaError, setFechaError] = useState('')
  const [programaPeriodoId, setProgramaPeriodoId] = useState<string | null>(null)
  const [programaMateriaId, setProgramaMateriaId] = useState('')
  const [programaCarrera, setProgramaCarrera] = useState('')
  const [programaAnio, setProgramaAnio] = useState(String(new Date().getFullYear()))
  const [programaError, setProgramaError] = useState('')

  const resetForm = () => {
    setShowForm(false)
    setEditId(null)
    setNombre('')
    setFechaInicio('')
    setFechaFin('')
    setFormError('')
  }

  const resetFechaForm = () => {
    setFechaPeriodoId(null)
    setFechaKey('')
    setFechaLabel('')
    setFechaValor('')
    setFechaError('')
  }

  const resetProgramaForm = () => {
    setProgramaPeriodoId(null)
    setProgramaMateriaId('')
    setProgramaCarrera('')
    setProgramaAnio(String(new Date().getFullYear()))
    setProgramaError('')
  }

  const openNewForm = () => {
    resetForm()
    setShowForm(true)
  }

  const openEditForm = (periodo: PeriodoAcademico) => {
    setEditId(periodo.id)
    setNombre(periodo.nombre)
    setFechaInicio(toInputDate(periodo.fecha_inicio))
    setFechaFin(toInputDate(periodo.fecha_fin))
    setFormError('')
    setShowForm(true)
  }

  const handleGuardar = async (e: FormEvent) => {
    e.preventDefault()
    setFormError('')
    if (!nombre.trim() || !fechaInicio || !fechaFin) {
      setFormError('Nombre, fecha de inicio y fecha de fin son obligatorios.')
      return
    }
    if (fechaFin < fechaInicio) {
      setFormError('La fecha de fin debe ser posterior o igual a la fecha de inicio.')
      return
    }

    const payload: PeriodoPayload = {
      nombre: nombre.trim(),
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
    }

    try {
      if (editId) {
        await actualizarPeriodo.mutateAsync({ id: editId, ...payload })
      } else {
        await crearPeriodo.mutateAsync(payload)
      }
      resetForm()
    } catch (caughtError) {
      setFormError(getPeriodoErrorMessage(caughtError))
    }
  }

  const handleActivar = (periodo: PeriodoAcademico) => {
    const confirmed = window.confirm(`Activar el período "${periodo.nombre}"? Se desactivara cualquier otro período activo.`)
    if (confirmed) {
      activarPeriodo.mutate(periodo.id)
    }
  }

  const handleDesactivar = (periodo: PeriodoAcademico) => {
    const confirmed = window.confirm(`Desactivar el período "${periodo.nombre}"?`)
    if (confirmed) {
      desactivarPeriodo.mutate(periodo.id)
    }
  }

  const handleEliminar = (periodo: PeriodoAcademico) => {
    if (periodo.activo) return
    const confirmed = window.confirm(`Eliminar el período "${periodo.nombre}"? Esta accion no lo mostrara mas en el listado.`)
    if (confirmed) {
      eliminarPeriodo.mutate(periodo.id)
    }
  }

  const openFechaForm = (periodo: PeriodoAcademico) => {
    setFechaPeriodoId(periodo.id)
    setFechaKey('')
    setFechaLabel('')
    setFechaValor('')
    setFechaError('')
  }

  const handleAgregarFecha = async (e: FormEvent) => {
    e.preventDefault()
    setFechaError('')
    if (!fechaPeriodoId || !fechaKey.trim() || !fechaLabel.trim() || !fechaValor) {
      setFechaError('Clave, etiqueta y fecha son obligatorias.')
      return
    }
    try {
      await agregarFecha.mutateAsync({
        periodoId: fechaPeriodoId,
        key: fechaKey.trim(),
        label: fechaLabel.trim(),
        fecha: fechaValor,
      })
      resetFechaForm()
    } catch {
      setFechaError('No se pudo agregar la fecha académica.')
    }
  }

  const handleQuitarFecha = (periodoId: string, fechaId: string, label: string) => {
    const confirmed = window.confirm(`Quitar la fecha "${label}" del período?`)
    if (confirmed) {
      quitarFecha.mutate({ periodoId, fechaId })
    }
  }

  const openProgramaForm = (periodo: PeriodoAcademico) => {
    setProgramaPeriodoId(periodo.id)
    setProgramaMateriaId('')
    setProgramaCarrera('')
    setProgramaAnio(String(new Date(periodo.fecha_inicio).getUTCFullYear()))
    setProgramaError('')
  }

  const handleMateriaProgramaChange = (materiaId: string) => {
    setProgramaMateriaId(materiaId)
    const materia = materias?.items?.find((item) => item.id === materiaId)
    if (materia?.carrera_nombre) {
      setProgramaCarrera(materia.carrera_nombre)
    }
  }

  const handleAgregarPrograma = async (e: FormEvent) => {
    e.preventDefault()
    setProgramaError('')
    if (!programaPeriodoId || !programaMateriaId || !programaCarrera.trim() || !programaAnio) {
      setProgramaError('Materia, carrera y año son obligatorios.')
      return
    }
    try {
      await agregarPrograma.mutateAsync({
        periodoId: programaPeriodoId,
        materia_id: programaMateriaId,
        carrera: programaCarrera.trim(),
        anio: Number(programaAnio),
      })
      resetProgramaForm()
    } catch {
      setProgramaError('No se pudo asignar el programa.')
    }
  }

  const handleQuitarPrograma = (periodoId: string, programaId: string, materiaNombre: string) => {
    const confirmed = window.confirm(`Quitar "${materiaNombre}" del período?`)
    if (confirmed) {
      quitarPrograma.mutate({ periodoId, programaId })
    }
  }

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Setup de Cuatrimestre</h1>
        <Button onClick={showForm ? resetForm : openNewForm}>
          {showForm ? 'Cancelar' : 'Nuevo Período'}
        </Button>
      </div>

      {error && (
        <Alert variant="error">No se pudieron cargar los períodos académicos.</Alert>
      )}

      {showForm && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{editId ? 'Editar período' : 'Nuevo período'}</h3>
          <form onSubmit={handleGuardar} className="space-y-4">
            {formError && <Alert variant="error">{formError}</Alert>}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                <input
                  type="text"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                  placeholder="Ej: 1C 2026"
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Fecha inicio *</label>
                <input
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Fecha fin *</label>
                <input
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={resetForm} type="button">Cancelar</Button>
              <Button type="submit" loading={crearPeriodo.isPending || actualizarPeriodo.isPending}>
                {editId ? 'Actualizar' : 'Crear'}
              </Button>
            </div>
          </form>
        </Card>
      )}

      <div className="space-y-4">
        {data?.items?.map((periodo) => (
          <Card key={periodo.id} className="p-4">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{periodo.nombre}</h3>
                <p className="text-sm text-gray-500">
                  {formatDate(periodo.fecha_inicio)} - {formatDate(periodo.fecha_fin)}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                  periodo.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                }`}>{periodo.activo ? 'Activo' : 'Inactivo'}</span>
                {periodo.activo ? (
                  <Button variant="secondary" onClick={() => handleDesactivar(periodo)} loading={desactivarPeriodo.isPending}>
                    Desactivar
                  </Button>
                ) : (
                  <Button onClick={() => handleActivar(periodo)} loading={activarPeriodo.isPending}>
                    Activar
                  </Button>
                )}
                <IconButton label="Editar" onClick={() => openEditForm(periodo)}>
                  <EditIcon />
                </IconButton>
                {!periodo.activo && (
                  <IconButton label="Eliminar" onClick={() => handleEliminar(periodo)} loading={eliminarPeriodo.isPending}>
                    <TrashIcon />
                  </IconButton>
                )}
              </div>
            </div>

            <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <h4 className="text-xs font-medium uppercase text-gray-500">Fechas Académicas ({periodo.fechas?.length ?? 0})</h4>
                  <Button size="sm" variant="secondary" onClick={() => openFechaForm(periodo)}>
                    <PlusIcon />
                    Agregar
                  </Button>
                </div>
                {fechaPeriodoId === periodo.id && (
                  <form onSubmit={handleAgregarFecha} className="mb-3 space-y-2 rounded-lg border border-gray-200 p-3">
                    {fechaError && <Alert variant="error">{fechaError}</Alert>}
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                      <input
                        type="text"
                        value={fechaKey}
                        onChange={(e) => setFechaKey(e.target.value)}
                        placeholder="clave"
                        className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <input
                        type="text"
                        value={fechaLabel}
                        onChange={(e) => setFechaLabel(e.target.value)}
                        placeholder="etiqueta"
                        className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <input
                        type="date"
                        value={fechaValor}
                        onChange={(e) => setFechaValor(e.target.value)}
                        className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="secondary" size="sm" onClick={resetFechaForm}>Cancelar</Button>
                      <Button type="submit" size="sm" loading={agregarFecha.isPending}>Guardar</Button>
                    </div>
                  </form>
                )}
                {periodo.fechas && periodo.fechas.length > 0 ? (
                  <div className="space-y-1">
                    {periodo.fechas.map((f) => (
                      <div key={f.id} className="flex items-center justify-between gap-3 text-sm">
                        <span className="text-gray-700">{f.label} ({f.key})</span>
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500">{formatDate(f.fecha)}</span>
                          <IconButton label="Quitar" onClick={() => handleQuitarFecha(periodo.id, f.id, f.label)} loading={quitarFecha.isPending}>
                            <TrashIcon />
                          </IconButton>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">Sin fechas cargadas.</p>
                )}
              </div>
              <div>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <h4 className="text-xs font-medium uppercase text-gray-500">Programas ({periodo.programas?.length ?? 0})</h4>
                  <Button size="sm" variant="secondary" onClick={() => openProgramaForm(periodo)}>
                    <PlusIcon />
                    Agregar
                  </Button>
                </div>
                {programaPeriodoId === periodo.id && (
                  <form onSubmit={handleAgregarPrograma} className="mb-3 space-y-2 rounded-lg border border-gray-200 p-3">
                    {programaError && <Alert variant="error">{programaError}</Alert>}
                    <div className="grid grid-cols-1 gap-2">
                      <select
                        value={programaMateriaId}
                        onChange={(e) => handleMateriaProgramaChange(e.target.value)}
                        className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">Seleccione una materia</option>
                        {materias?.items?.filter((materia) => materia.activo).map((materia) => (
                          <option key={materia.id} value={materia.id}>
                            {materia.nombre} ({materia.codigo})
                          </option>
                        ))}
                      </select>
                      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                        <input
                          type="text"
                          value={programaCarrera}
                          onChange={(e) => setProgramaCarrera(e.target.value)}
                          placeholder="carrera"
                          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                        <input
                          type="number"
                          value={programaAnio}
                          onChange={(e) => setProgramaAnio(e.target.value)}
                          min={2000}
                          max={2100}
                          placeholder="año"
                          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="secondary" size="sm" onClick={resetProgramaForm}>Cancelar</Button>
                      <Button type="submit" size="sm" loading={agregarPrograma.isPending}>Guardar</Button>
                    </div>
                  </form>
                )}
                {periodo.programas && periodo.programas.length > 0 ? (
                  <div className="space-y-1">
                    {periodo.programas.map((p) => (
                      <div key={p.id} className="flex items-center justify-between gap-3 text-sm">
                        <span className="text-gray-700">{p.materia_nombre}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500">{p.carrera} - A{p.anio}</span>
                          <IconButton label="Quitar" onClick={() => handleQuitarPrograma(periodo.id, p.id, p.materia_nombre)} loading={quitarPrograma.isPending}>
                            <TrashIcon />
                          </IconButton>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">Sin programas asignados.</p>
                )}
              </div>
            </div>
          </Card>
        ))}
        {(!data?.items || data.items.length === 0) && (
          <Card className="p-12 text-center">
            <p className="text-gray-500">No hay períodos académicos registrados.</p>
          </Card>
        )}
      </div>
    </div>
  )
}
