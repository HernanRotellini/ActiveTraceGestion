import { useState } from 'react'
import type { FormEvent } from 'react'
import type { Carrera, Cohorte, Materia } from '@/features/admin/types'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Toast } from '@/shared/components/Toast'
import { ApiError } from '@/shared/types/api'
import {
  useActualizarFechaOficial,
  useCrearFechaOficial,
  useEliminarFechaOficial,
} from '@/features/setup-cuatrimestre/hooks/usePeriodos'
import type { FechaAcademicaOficial, PeriodoAcademico, TipoFechaAcademica } from '@/features/setup-cuatrimestre/types'
import { formatDate, getCarreraName, getCohorteName, getMateriaName, toInputDate } from '@/features/setup-cuatrimestre/utils'
import { ActionIconButton } from '@/features/setup-cuatrimestre/components/ActionIconButton'
import { ConfirmActionModal } from '@/features/setup-cuatrimestre/components/ConfirmActionModal'
import { EditIcon, PlusIcon, TrashIcon } from '@/features/setup-cuatrimestre/components/SetupIcons'

interface FechasPanelProps {
  fechas: FechaAcademicaOficial[]
  periodos: PeriodoAcademico[]
  carreras: Carrera[]
  cohortes: Cohorte[]
  materias: Materia[]
  isLoading: boolean
}

const fechaTypes: TipoFechaAcademica[] = ['Parcial', 'TP', 'Coloquio', 'Recuperatorio']

function getFechaErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 409) return 'Ya existe una fecha activa con ese contexto, tipo, numero y periodo.'
    if (error.status === 404) return 'La materia o cohorte de esta fecha ya no esta disponible.'
    return error.message || 'No se pudo guardar la fecha academica.'
  }
  return 'No se pudo guardar la fecha academica.'
}

export function FechasPanel({ fechas, periodos, carreras, cohortes, materias, isLoading }: FechasPanelProps) {
  const crearFecha = useCrearFechaOficial()
  const actualizarFecha = useActualizarFechaOficial()
  const eliminarFecha = useEliminarFechaOficial()

  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [periodoId, setPeriodoId] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [tipo, setTipo] = useState<TipoFechaAcademica>('Parcial')
  const [numero, setNumero] = useState('1')
  const [periodo, setPeriodo] = useState('')
  const [fecha, setFecha] = useState('')
  const [titulo, setTitulo] = useState('')
  const [formError, setFormError] = useState('')
  const [toastError, setToastError] = useState('')
  const [toastSuccess, setToastSuccess] = useState('')
  const [fechaAEliminar, setFechaAEliminar] = useState<FechaAcademicaOficial | null>(null)

  const activeCarreras = carreras.filter((carrera) => carrera.activo)
  const periodosDisponibles = periodos
  const cohortesDisponibles = cohortes.filter((cohorte) => cohorte.activo && cohorte.carrera_id === carreraId)
  const materiasDisponibles = materias.filter((materia) => {
    if (!materia.activo) return false
    if (carreraId && materia.carrera_id !== carreraId) return false
    if (cohorteId && materia.cohorte_id !== cohorteId) return false
    return true
  })

  const resetForm = () => {
    setShowForm(false)
    setEditId(null)
    setPeriodoId('')
    setCarreraId('')
    setCohorteId('')
    setMateriaId('')
    setTipo('Parcial')
    setNumero('1')
    setPeriodo('')
    setFecha('')
    setTitulo('')
    setFormError('')
  }

  const openEditForm = (item: FechaAcademicaOficial) => {
    const materia = materias.find((current) => current.id === item.materia_id)
    setEditId(item.id)
    setPeriodoId(item.periodo_id ?? '')
    setCarreraId(materia?.carrera_id ?? '')
    setCohorteId(item.cohorte_id)
    setMateriaId(item.materia_id)
    setTipo(item.tipo)
    setNumero(String(item.numero))
    setPeriodo(item.periodo)
    setFecha(toInputDate(item.fecha))
    setTitulo(item.titulo)
    setFormError('')
    setShowForm(true)
  }

  const handleGuardar = async (event: FormEvent) => {
    event.preventDefault()
    setFormError('')
    const selectedPeriodo = periodos.find((item) => item.id === periodoId)
    if (!periodoId || !cohorteId || !materiaId || !fecha || !titulo.trim()) {
      setFormError('Selecciona periodo, cohorte, materia, fecha y titulo.')
      return
    }
    if (!selectedPeriodo) {
      setFormError('El periodo seleccionado ya no esta disponible.')
      return
    }
    try {
      if (editId) {
        await actualizarFecha.mutateAsync({ id: editId, periodo_id: periodoId, numero: Number(numero), periodo: selectedPeriodo.nombre, fecha, titulo: titulo.trim() })
        setToastSuccess('Fecha academica actualizada correctamente.')
      } else {
        await crearFecha.mutateAsync({
          periodo_id: periodoId,
          cohorte_id: cohorteId,
          materia_id: materiaId,
          tipo,
          numero: Number(numero),
          periodo: selectedPeriodo.nombre,
          fecha,
          titulo: titulo.trim(),
        })
        setToastSuccess('Fecha academica registrada correctamente.')
      }
      resetForm()
    } catch (error) {
      setFormError(getFechaErrorMessage(error))
    }
  }

  const handleEliminar = async () => {
    if (!fechaAEliminar) return
    try {
      await eliminarFecha.mutateAsync(fechaAEliminar.id)
      setToastSuccess('Fecha academica eliminada correctamente.')
    } catch (error) {
      setToastError(getFechaErrorMessage(error))
    } finally {
      setFechaAEliminar(null)
    }
  }

  const prerequisitesReady = periodosDisponibles.length > 0 && activeCarreras.length > 0 && cohortes.length > 0 && materias.length > 0

  return (
    <section id="fechas" className="scroll-mt-24 space-y-4">
      {toastError ? <Toast message={toastError} variant="error" onClose={() => setToastError('')} /> : null}
      {!toastError && toastSuccess ? <Toast message={toastSuccess} variant="success" onClose={() => setToastSuccess('')} /> : null}
      <Card className="overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-slate-500">Paso 5</p>
              <h2 className="text-xl font-semibold text-slate-900">Fechas de Evaluacion</h2>
            </div>
            <Button type="button" onClick={showForm ? resetForm : () => setShowForm(true)} disabled={!prerequisitesReady}>
              <PlusIcon />
              {showForm ? 'Cancelar' : 'Nueva Fecha'}
            </Button>
          </div>
          <p className="mt-2 text-sm text-slate-600">
            Registra parciales, TPs, coloquios y recuperatorios por materia y cohorte.
          </p>
        </div>
        <div className="space-y-4 p-6">
          {!prerequisitesReady ? <p className="text-sm text-amber-700">Necesitas periodos, carreras, cohortes y materias activas para cargar el calendario.</p> : null}
          {showForm && prerequisitesReady ? (
            <form onSubmit={handleGuardar} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-4">
              <div className="grid gap-4 md:grid-cols-2">
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Periodo</span>
                  <select value={periodoId} onChange={(event) => { const value = event.target.value; setPeriodoId(value); setPeriodo(periodos.find((item) => item.id === value)?.nombre ?? '') }} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500">
                    <option value="">Selecciona un periodo...</option>
                    {periodosDisponibles.map((periodo) => <option key={periodo.id} value={periodo.id}>{periodo.nombre}</option>)}
                  </select>
                </label>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Carrera</span>
                  <select value={carreraId} onChange={(event) => { setCarreraId(event.target.value); setCohorteId(''); setMateriaId('') }} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" disabled={!!editId}>
                    <option value="">Selecciona una carrera...</option>
                    {activeCarreras.map((carrera) => <option key={carrera.id} value={carrera.id}>{carrera.nombre}</option>)}
                  </select>
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Cohorte</span>
                  <select value={cohorteId} onChange={(event) => { setCohorteId(event.target.value); setMateriaId('') }} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" disabled={!carreraId || !!editId}>
                    <option value="">Selecciona una cohorte...</option>
                    {cohortesDisponibles.map((cohorte) => <option key={cohorte.id} value={cohorte.id}>{cohorte.nombre}</option>)}
                  </select>
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Materia</span>
                  <select value={materiaId} onChange={(event) => setMateriaId(event.target.value)} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" disabled={!carreraId || !!editId}>
                    <option value="">Selecciona una materia...</option>
                    {materiasDisponibles.map((materia) => <option key={materia.id} value={materia.id}>{materia.nombre}</option>)}
                  </select>
                </label>
              </div>
              <div className="grid gap-4 md:grid-cols-4">
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Tipo</span>
                  <select value={tipo} onChange={(event) => setTipo(event.target.value as TipoFechaAcademica)} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" disabled={!!editId}>
                    {fechaTypes.map((item) => <option key={item} value={item}>{item}</option>)}
                  </select>
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Numero</span>
                  <input type="number" min={1} max={10} value={numero} onChange={(event) => setNumero(event.target.value)} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Periodo</span>
                  <input autoComplete="off" value={periodo} readOnly className="block w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-600 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Fecha</span>
                  <input type="date" value={fecha} onChange={(event) => setFecha(event.target.value)} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </label>
              </div>
              <label className="space-y-1 text-sm text-slate-700">
                <span className="font-medium">Titulo</span>
                <input autoComplete="off" value={titulo} onChange={(event) => setTitulo(event.target.value)} placeholder="Ej.: Primer parcial integrador..." className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </label>
              {formError ? <p className="text-sm text-rose-700">{formError}</p> : null}
              <div className="flex justify-end gap-3">
                <Button type="button" variant="secondary" onClick={resetForm}>Cancelar</Button>
                <Button type="submit" loading={crearFecha.isPending || actualizarFecha.isPending}>{editId ? 'Guardar Cambios' : 'Guardar Fecha'}</Button>
              </div>
            </form>
          ) : null}
          {isLoading ? <p className="text-sm text-slate-500">Cargando fechas academicas...</p> : null}
          {!isLoading && fechas.length === 0 ? <p className="text-sm text-slate-500">Todavia no hay fechas academicas registradas.</p> : null}
          {fechas.map((item) => (
            <div key={item.id} className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-0 space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="truncate text-base font-semibold text-slate-900">{item.titulo}</h3>
                    <span className="rounded-full bg-sky-100 px-2.5 py-1 text-xs font-medium text-sky-800">{item.tipo} #{item.numero}</span>
                  </div>
                  <p className="text-sm text-slate-600">{getMateriaName(materias, item.materia_id)} - {getCarreraName(carreras, materias.find((materia) => materia.id === item.materia_id)?.carrera_id)} - {getCohorteName(cohortes, item.cohorte_id)}</p>
                  <p className="text-xs text-slate-500">{periodos.find((periodo) => periodo.id === item.periodo_id)?.nombre ?? item.periodo} - {formatDate(item.fecha)}</p>
                </div>
                <div className="flex items-center gap-2">
                  <ActionIconButton label="Editar" onClick={() => openEditForm(item)}><EditIcon /></ActionIconButton>
                  <ActionIconButton label="Eliminar" onClick={() => setFechaAEliminar(item)}><TrashIcon /></ActionIconButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
      {fechaAEliminar ? (
        <ConfirmActionModal
          title="Eliminar fecha academica"
          description={`Vas a eliminar "${fechaAEliminar.titulo}" del calendario de ${getCohorteName(cohortes, fechaAEliminar.cohorte_id)}.`}
          confirmLabel="Eliminar Fecha"
          onConfirm={handleEliminar}
          onClose={() => setFechaAEliminar(null)}
          loading={eliminarFecha.isPending}
          danger
        />
      ) : null}
    </section>
  )
}
