import { useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Toast } from '@/shared/components/Toast'
import { ApiError } from '@/shared/types/api'
import {
  useActivarPeriodo,
  useActualizarPeriodoMutation,
  useCrearPeriodo,
  useDesactivarPeriodo,
  useEliminarPeriodo,
} from '@/features/setup-cuatrimestre/hooks/usePeriodos'
import type { PeriodoAcademico, PeriodoPayload } from '@/features/setup-cuatrimestre/types'
import { formatDate, toInputDate } from '@/features/setup-cuatrimestre/utils'
import { ActionIconButton } from '@/features/setup-cuatrimestre/components/ActionIconButton'
import { ConfirmActionModal } from '@/features/setup-cuatrimestre/components/ConfirmActionModal'
import { EditIcon, PlusIcon, TrashIcon } from '@/features/setup-cuatrimestre/components/SetupIcons'

interface PeriodosPanelProps {
  periodos: PeriodoAcademico[]
  isLoading: boolean
}

type ConfirmAction =
  | { kind: 'activar' | 'desactivar' | 'eliminar'; periodo: PeriodoAcademico }
  | null

function getPeriodoErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.message.includes('fecha_fin')) {
      return 'La fecha de fin debe ser posterior o igual a la fecha de inicio.'
    }
    if (
      error.status === 409 ||
      error.message.includes('associated fechas') ||
      error.message.includes('associated programas')
    ) {
      return 'No se puede eliminar el periodo porque tiene fechas academicas o programas asociados. Desactivalo para conservar el historial.'
    }
    if (error.status === 404) {
      return 'El periodo seleccionado ya no esta disponible.'
    }
    return error.message || 'No se pudo guardar el periodo.'
  }
  return 'No se pudo guardar el periodo.'
}

export function PeriodosPanel({ periodos, isLoading }: PeriodosPanelProps) {
  const crearPeriodo = useCrearPeriodo()
  const actualizarPeriodo = useActualizarPeriodoMutation()
  const activarPeriodo = useActivarPeriodo()
  const desactivarPeriodo = useDesactivarPeriodo()
  const eliminarPeriodo = useEliminarPeriodo()

  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [formError, setFormError] = useState('')
  const [toastError, setToastError] = useState('')
  const [toastSuccess, setToastSuccess] = useState('')
  const [confirmAction, setConfirmAction] = useState<ConfirmAction>(null)

  const resetForm = () => {
    setShowForm(false)
    setEditId(null)
    setNombre('')
    setFechaInicio('')
    setFechaFin('')
    setFormError('')
  }

  const openEditForm = (periodo: PeriodoAcademico) => {
    setEditId(periodo.id)
    setNombre(periodo.nombre)
    setFechaInicio(toInputDate(periodo.fecha_inicio))
    setFechaFin(toInputDate(periodo.fecha_fin))
    setFormError('')
    setShowForm(true)
  }

  const handleGuardar = async (event: FormEvent) => {
    event.preventDefault()
    setFormError('')
    if (!nombre.trim() || !fechaInicio || !fechaFin) {
      setFormError('Completa nombre, fecha de inicio y fecha de fin.')
      return
    }
    if (fechaFin < fechaInicio) {
      setFormError('La fecha de fin debe ser posterior o igual a la fecha de inicio.')
      return
    }

    const payload: PeriodoPayload = { nombre: nombre.trim(), fecha_inicio: fechaInicio, fecha_fin: fechaFin }
    try {
      if (editId) {
        await actualizarPeriodo.mutateAsync({ id: editId, ...payload })
        setToastSuccess('Periodo actualizado correctamente.')
      } else {
        await crearPeriodo.mutateAsync(payload)
        setToastSuccess('Periodo creado correctamente.')
      }
      resetForm()
    } catch (error) {
      setFormError(getPeriodoErrorMessage(error))
    }
  }

  const handleConfirm = async () => {
    if (!confirmAction) return
    try {
      if (confirmAction.kind === 'activar') {
        await activarPeriodo.mutateAsync(confirmAction.periodo.id)
        setToastSuccess('Periodo activado. Los demas periodos quedaron inactivos.')
      }
      if (confirmAction.kind === 'desactivar') {
        await desactivarPeriodo.mutateAsync(confirmAction.periodo.id)
        setToastSuccess('Periodo desactivado correctamente.')
      }
      if (confirmAction.kind === 'eliminar') {
        await eliminarPeriodo.mutateAsync(confirmAction.periodo.id)
        setToastSuccess('Periodo eliminado del listado operativo.')
      }
    } catch (error) {
      setToastError(getPeriodoErrorMessage(error))
    } finally {
      setConfirmAction(null)
    }
  }

  const activePeriod = periodos.find((periodo) => periodo.activo)

  return (
    <section id="periodos" className="scroll-mt-24 space-y-4">
      {toastError ? <Toast message={toastError} variant="error" onClose={() => setToastError('')} /> : null}
      {!toastError && toastSuccess ? <Toast message={toastSuccess} variant="success" onClose={() => setToastSuccess('')} /> : null}
      <Card className="overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-slate-500">Paso 1</p>
              <h2 className="text-xl font-semibold text-slate-900">Periodo Lectivo</h2>
            </div>
            <Button type="button" onClick={showForm ? resetForm : () => setShowForm(true)}>
              <PlusIcon />
              {showForm ? 'Cancelar' : 'Nuevo Periodo'}
            </Button>
          </div>
          <p className="mt-2 text-sm text-slate-600">
            Solo puede quedar un periodo activo por tenant. La activacion desactiva el resto.
          </p>
          <p className="mt-3 text-sm text-slate-500">
            Activo ahora: <span className="font-medium text-slate-900">{activePeriod?.nombre ?? 'Sin periodo activo'}</span>
          </p>
        </div>
        <div className="space-y-4 p-6">
          {showForm ? (
            <form onSubmit={handleGuardar} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-4">
              <div className="grid gap-4 md:grid-cols-3">
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Nombre</span>
                  <input name="nombre_periodo" autoComplete="off" value={nombre} onChange={(event) => setNombre(event.target.value)} placeholder="Ej.: 1C 2026..." className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Fecha de Inicio</span>
                  <input name="fecha_inicio_periodo" autoComplete="off" type="date" value={fechaInicio} onChange={(event) => setFechaInicio(event.target.value)} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </label>
                <label className="space-y-1 text-sm text-slate-700">
                  <span className="font-medium">Fecha de Fin</span>
                  <input name="fecha_fin_periodo" autoComplete="off" type="date" value={fechaFin} onChange={(event) => setFechaFin(event.target.value)} className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </label>
              </div>
              {formError ? <p className="text-sm text-rose-700">{formError}</p> : null}
              <div className="flex justify-end gap-3">
                <Button type="button" variant="secondary" onClick={resetForm}>Cancelar</Button>
                <Button type="submit" loading={crearPeriodo.isPending || actualizarPeriodo.isPending}>{editId ? 'Guardar Cambios' : 'Crear Periodo'}</Button>
              </div>
            </form>
          ) : null}
          {isLoading ? <p className="text-sm text-slate-500">Cargando periodos...</p> : null}
          {!isLoading && periodos.length === 0 ? <p className="text-sm text-slate-500">Todavia no hay periodos registrados.</p> : null}
          {periodos.map((periodo) => (
            <div key={periodo.id} className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-base font-semibold text-slate-900">{periodo.nombre}</h3>
                    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${periodo.activo ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'}`}>{periodo.activo ? 'Activo' : 'Inactivo'}</span>
                  </div>
                  <p className="text-sm text-slate-500">{formatDate(periodo.fecha_inicio)} al {formatDate(periodo.fecha_fin)}</p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Button type="button" variant={periodo.activo ? 'secondary' : 'primary'} onClick={() => setConfirmAction({ kind: periodo.activo ? 'desactivar' : 'activar', periodo })}>
                    {periodo.activo ? 'Desactivar' : 'Activar'}
                  </Button>
                  <ActionIconButton label="Editar" onClick={() => openEditForm(periodo)}><EditIcon /></ActionIconButton>
                  <ActionIconButton label="Eliminar" onClick={() => setConfirmAction({ kind: 'eliminar', periodo })} disabled={periodo.activo}><TrashIcon /></ActionIconButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
      {confirmAction ? (
        <ConfirmActionModal
          title={`${confirmAction.kind === 'eliminar' ? 'Eliminar' : confirmAction.kind === 'activar' ? 'Activar' : 'Desactivar'} periodo`}
          description={confirmAction.kind === 'activar'
            ? `Vas a activar "${confirmAction.periodo.nombre}". Si hay otro periodo activo, el sistema lo va a desactivar automaticamente.`
            : confirmAction.kind === 'desactivar'
              ? `Vas a desactivar "${confirmAction.periodo.nombre}". El periodo seguira existiendo para consulta y auditoria.`
              : `Vas a quitar "${confirmAction.periodo.nombre}" del listado operativo. La baja es logica, no fisica.`}
          confirmLabel={confirmAction.kind === 'eliminar' ? 'Eliminar Periodo' : confirmAction.kind === 'activar' ? 'Activar Periodo' : 'Desactivar Periodo'}
          onConfirm={handleConfirm}
          onClose={() => setConfirmAction(null)}
          loading={activarPeriodo.isPending || desactivarPeriodo.isPending || eliminarPeriodo.isPending}
          danger={confirmAction.kind === 'eliminar'}
        />
      ) : null}
    </section>
  )
}
