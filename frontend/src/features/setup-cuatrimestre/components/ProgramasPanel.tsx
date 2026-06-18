import { useState } from 'react'
import type { FormEvent } from 'react'
import type { Carrera, Cohorte, Materia } from '@/features/admin/types'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Toast } from '@/shared/components/Toast'
import { ApiError } from '@/shared/types/api'
import {
  useActualizarProgramaOficial,
  useCrearProgramaOficial,
  useEliminarProgramaOficial,
} from '@/features/setup-cuatrimestre/hooks/usePeriodos'
import type { ProgramaOficial } from '@/features/setup-cuatrimestre/types'
import { formatDateTime, getCarreraName, getCohorteName, getMateriaName } from '@/features/setup-cuatrimestre/utils'
import { ActionIconButton } from '@/features/setup-cuatrimestre/components/ActionIconButton'
import { ConfirmActionModal } from '@/features/setup-cuatrimestre/components/ConfirmActionModal'
import { EditIcon, PlusIcon, TrashIcon } from '@/features/setup-cuatrimestre/components/SetupIcons'

interface ProgramasPanelProps {
  programas: ProgramaOficial[]
  carreras: Carrera[]
  cohortes: Cohorte[]
  materias: Materia[]
  isLoading: boolean
}

function getProgramaErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 409) return 'Ya existe un programa activo con ese titulo para el mismo contexto.'
    if (error.status === 404) return 'El contexto academico del programa ya no existe o cambio.'
    return error.message || 'No se pudo guardar el programa.'
  }
  return 'No se pudo guardar el programa.'
}

export function ProgramasPanel({ programas, carreras, cohortes, materias, isLoading }: ProgramasPanelProps) {
  const crearPrograma = useCrearProgramaOficial()
  const actualizarPrograma = useActualizarProgramaOficial()
  const eliminarPrograma = useEliminarProgramaOficial()

  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [titulo, setTitulo] = useState('')
  const [referencia, setReferencia] = useState('')
  const [formError, setFormError] = useState('')
  const [toastError, setToastError] = useState('')
  const [toastSuccess, setToastSuccess] = useState('')
  const [programaAEliminar, setProgramaAEliminar] = useState<ProgramaOficial | null>(null)

  const activeCarreras = carreras.filter((carrera) => carrera.activo)
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
    setCarreraId('')
    setCohorteId('')
    setMateriaId('')
    setTitulo('')
    setReferencia('')
    setFormError('')
  }

  const openEditForm = (programa: ProgramaOficial) => {
    setEditId(programa.id)
    setCarreraId(programa.carrera_id)
    setCohorteId(programa.cohorte_id)
    setMateriaId(programa.materia_id)
    setTitulo(programa.titulo)
    setReferencia(programa.referencia_archivo)
    setFormError('')
    setShowForm(true)
  }

  const handleGuardar = async (event: FormEvent) => {
    event.preventDefault()
    setFormError('')
    if (!carreraId || !cohorteId || !materiaId || !titulo.trim() || !referencia.trim()) {
      setFormError('Selecciona carrera, cohorte, materia, titulo y referencia de archivo.')
      return
    }
    try {
      if (editId) {
        await actualizarPrograma.mutateAsync({ id: editId, titulo: titulo.trim(), referencia_archivo: referencia.trim() })
        setToastSuccess('Programa actualizado correctamente.')
      } else {
        await crearPrograma.mutateAsync({
          carrera_id: carreraId,
          cohorte_id: cohorteId,
          materia_id: materiaId,
          titulo: titulo.trim(),
          referencia_archivo: referencia.trim(),
        })
        setToastSuccess('Programa registrado correctamente.')
      }
      resetForm()
    } catch (error) {
      setFormError(getProgramaErrorMessage(error))
    }
  }

  const handleEliminar = async () => {
    if (!programaAEliminar) return
    try {
      await eliminarPrograma.mutateAsync(programaAEliminar.id)
      setToastSuccess('Programa eliminado correctamente.')
    } catch (error) {
      setToastError(getProgramaErrorMessage(error))
    } finally {
      setProgramaAEliminar(null)
    }
  }

  const prerequisitesReady = activeCarreras.length > 0 && cohortes.length > 0 && materias.length > 0

  return (
    <section id="programas" className="scroll-mt-24 space-y-4">
      {toastError ? <Toast message={toastError} variant="error" onClose={() => setToastError('')} /> : null}
      {!toastError && toastSuccess ? <Toast message={toastSuccess} variant="success" onClose={() => setToastSuccess('')} /> : null}
      <Card className="overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-slate-500">Paso 4</p>
              <h2 className="text-xl font-semibold text-slate-900">Programas Oficiales</h2>
            </div>
            <Button type="button" onClick={showForm ? resetForm : () => setShowForm(true)} disabled={!prerequisitesReady}>
              <PlusIcon />
              {showForm ? 'Cancelar' : 'Nuevo Programa'}
            </Button>
          </div>
          <p className="mt-2 text-sm text-slate-600">
            Esta seccion usa el modelo oficial de programa por materia, carrera y cohorte.
          </p>
        </div>
        <div className="space-y-4 p-6">
          {!prerequisitesReady ? <p className="text-sm text-amber-700">Antes de cargar programas necesitas carreras, cohortes y materias activas.</p> : null}
          {showForm && prerequisitesReady ? (
            <form onSubmit={handleGuardar} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-4">
              <div className="grid gap-4 md:grid-cols-2">
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Carrera</span>
                  <select name="carrera_programa" value={carreraId} onChange={(event) => { setCarreraId(event.target.value); setCohorteId(''); setMateriaId('') }} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500">
                    <option value="">Selecciona una carrera...</option>
                    {activeCarreras.map((carrera) => <option key={carrera.id} value={carrera.id}>{carrera.nombre}</option>)}
                  </select>
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Cohorte</span>
                  <select name="cohorte_programa" value={cohorteId} onChange={(event) => { setCohorteId(event.target.value); setMateriaId('') }} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" disabled={!carreraId}>
                    <option value="">Selecciona una cohorte...</option>
                    {cohortesDisponibles.map((cohorte) => <option key={cohorte.id} value={cohorte.id}>{cohorte.nombre}</option>)}
                  </select>
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Materia</span>
                  <select name="materia_programa" value={materiaId} onChange={(event) => setMateriaId(event.target.value)} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" disabled={!carreraId}>
                    <option value="">Selecciona una materia...</option>
                    {materiasDisponibles.map((materia) => <option key={materia.id} value={materia.id}>{materia.nombre}</option>)}
                  </select>
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Titulo</span>
                  <input name="titulo_programa" autoComplete="off" value={titulo} onChange={(event) => setTitulo(event.target.value)} placeholder="Ej.: Programa 2026 v1..." className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </label>
              </div>
              <label className="space-y-1 text-sm text-slate-700">
                <span className="font-medium">Referencia Opaca del Archivo</span>
                <input name="referencia_archivo" autoComplete="off" value={referencia} onChange={(event) => setReferencia(event.target.value)} placeholder="Ej.: storage://programas/prog-i-2026..." className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </label>
              {formError ? <p className="text-sm text-rose-700">{formError}</p> : null}
              <div className="flex justify-end gap-3">
                <Button type="button" variant="secondary" onClick={resetForm}>Cancelar</Button>
                <Button type="submit" loading={crearPrograma.isPending || actualizarPrograma.isPending}>{editId ? 'Reemplazar Programa' : 'Guardar Programa'}</Button>
              </div>
            </form>
          ) : null}
          {isLoading ? <p className="text-sm text-slate-500">Cargando programas...</p> : null}
          {!isLoading && programas.length === 0 ? <p className="text-sm text-slate-500">Todavia no hay programas oficiales registrados.</p> : null}
          {programas.map((programa) => (
            <div key={programa.id} className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-0 space-y-1">
                  <h3 className="truncate text-base font-semibold text-slate-900">{programa.titulo}</h3>
                  <p className="text-sm text-slate-600">{getMateriaName(materias, programa.materia_id)} - {getCarreraName(carreras, programa.carrera_id)} - {getCohorteName(cohortes, programa.cohorte_id)}</p>
                  <p className="truncate text-xs text-slate-500" translate="no">{programa.referencia_archivo}</p>
                  <p className="text-xs text-slate-400">Registrado en {formatDateTime(programa.created_at)}</p>
                </div>
                <div className="flex items-center gap-2">
                  <ActionIconButton label="Editar" onClick={() => openEditForm(programa)}><EditIcon /></ActionIconButton>
                  <ActionIconButton label="Eliminar" onClick={() => setProgramaAEliminar(programa)}><TrashIcon /></ActionIconButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
      {programaAEliminar ? (
        <ConfirmActionModal
          title="Eliminar programa"
          description={`Vas a eliminar "${programaAEliminar.titulo}" del contexto ${getCohorteName(cohortes, programaAEliminar.cohorte_id)}.`}
          confirmLabel="Eliminar Programa"
          onConfirm={handleEliminar}
          onClose={() => setProgramaAEliminar(null)}
          loading={eliminarPrograma.isPending}
          danger
        />
      ) : null}
    </section>
  )
}
