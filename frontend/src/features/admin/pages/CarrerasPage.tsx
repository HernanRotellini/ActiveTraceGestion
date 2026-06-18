import { useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import { useCarreras, useCrearCarrera, useActualizarCarrera, useEliminarCarrera } from '@/features/admin/hooks/useAdmin'
import type { Carrera, CarreraPayload, CarreraUpdatePayload } from '@/features/admin/types'

interface ApiError {
  response?: {
    status?: number
    data?: {
      detail?: unknown
    }
  }
}

function errorDetailToText(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map(errorDetailToText).join(' ')
  }
  if (detail && typeof detail === 'object') {
    return Object.values(detail).map(errorDetailToText).join(' ')
  }
  return ''
}

function getCarreraSaveErrorMessage(err: unknown) {
  const response = (err as ApiError).response
  const detail = errorDetailToText(response?.data?.detail).toLowerCase()

  if (
    detail.includes('codigo') ||
    detail.includes('código') ||
    detail.includes('uq_carreras_tenant_codigo')
  ) {
    return 'Ya existe una carrera con ese código.'
  }
  if (
    detail.includes('nombre') ||
    detail.includes('uq_carreras_tenant_nombre')
  ) {
    return 'Ya existe una carrera con ese nombre.'
  }
  if (detail.includes('estado')) {
    return 'El estado de la carrera debe ser Activa o Inactiva.'
  }
  if (response?.status === 422) {
    return 'Revisá los campos obligatorios de la carrera.'
  }
  if (response?.status === 409) {
    return 'No se puede guardar la carrera porque ya existe un dato repetido.'
  }
  return 'Error al guardar la carrera.'
}

function getCarreraDeleteErrorMessage(err: unknown) {
  const response = (err as ApiError).response
  const detail = errorDetailToText(response?.data?.detail).toLowerCase()

  if (detail.includes('active carrera')) {
    return 'Solo se puede eliminar una carrera inactiva.'
  }
  if (detail.includes('cohortes')) {
    return 'No se puede eliminar la carrera porque tiene cohortes asociadas. Desactivala para conservar el historial.'
  }
  if (detail.includes('asignaciones')) {
    return 'No se puede eliminar la carrera porque tiene asignaciones asociadas. Desactivala para conservar el historial.'
  }
  if (response?.status === 409) {
    return 'No se puede eliminar la carrera porque tiene información asociada.'
  }
  return 'Error al eliminar la carrera.'
}

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

export default function CarrerasPage() {
  const [filterNombre, setFilterNombre] = useState('')
  const [filterCodigo, setFilterCodigo] = useState('')
  const [filterEstado, setFilterEstado] = useState<'todos' | 'activa' | 'inactiva'>('todos')
  const carreraFilters = {
    nombre: filterNombre.trim() || undefined,
    codigo: filterCodigo.trim() || undefined,
    estado: filterEstado === 'todos' ? undefined : filterEstado,
  }
  const { data, isLoading } = useCarreras(carreraFilters)
  const crear = useCrearCarrera()
  const actualizar = useActualizarCarrera()
  const eliminar = useEliminarCarrera()
  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [codigo, setCodigo] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [estado, setEstado] = useState<'activa' | 'inactiva'>('activa')
  const [showForm, setShowForm] = useState(false)
  const [toastError, setToastError] = useState('')
  const [toastSuccess, setToastSuccess] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<Carrera | null>(null)

  const resetForm = () => {
    setNombre('')
    setCodigo('')
    setDescripcion('')
    setEstado('activa')
    setEditId(null)
    setShowForm(false)
  }

  const handleEdit = (c: Carrera) => {
    setToastError('')
    setToastSuccess('')
    setEditId(c.id)
    setNombre(c.nombre)
    setCodigo(c.codigo)
    setDescripcion(c.descripcion ?? '')
    setEstado(c.activo ? 'activa' : 'inactiva')
    setShowForm(true)
  }

  const handleDelete = (c: Carrera) => {
    if (c.activo) return
    setToastError('')
    setToastSuccess('')
    setDeleteTarget(c)
  }

  const confirmDelete = async () => {
    if (!deleteTarget) return
    try {
      await eliminar.mutateAsync(deleteTarget.id)
      setToastSuccess('Carrera eliminada correctamente.')
      setDeleteTarget(null)
    } catch (err) {
      setDeleteTarget(null)
      setToastError(getCarreraDeleteErrorMessage(err))
    }
  }

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setToastError('')
    setToastSuccess('')
    if (!nombre.trim() || !codigo.trim()) {
      setToastError('Nombre y código son obligatorios.')
      return
    }
    try {
      const payload: CarreraPayload = {
        nombre: nombre.trim(),
        codigo: codigo.trim(),
        descripcion: descripcion.trim() || undefined,
        estado,
      }
      if (editId) {
        const updatePayload: CarreraUpdatePayload = { ...payload, estado }
        await actualizar.mutateAsync({ id: editId, ...updatePayload })
        setToastSuccess('Carrera actualizada correctamente.')
      } else {
        await crear.mutateAsync(payload)
        setToastSuccess('Carrera creada correctamente.')
      }
      resetForm()
    } catch (err) {
      setToastError(getCarreraSaveErrorMessage(err))
    }
  }

  return (
    <div className="space-y-6">
      {toastError ? (
        <Toast message={toastError} variant="error" onClose={() => setToastError('')} />
      ) : (
        <Toast message={toastSuccess} variant="success" onClose={() => setToastSuccess('')} />
      )}

      {deleteTarget && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 px-4" role="dialog" aria-modal="true" aria-labelledby="delete-carrera-title">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 id="delete-carrera-title" className="text-lg font-semibold text-gray-900">
              Eliminar carrera
            </h2>
            <p className="mt-3 text-sm text-gray-600">
              La carrera <span className="font-medium text-gray-900">{deleteTarget.nombre}</span> dejará de verse en el listado. Esta acción solo se permite si no tiene cohortes ni asignaciones asociadas.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setDeleteTarget(null)}
              >
                Cancelar
              </Button>
              <Button
                type="button"
                variant="danger"
                onClick={confirmDelete}
                loading={eliminar.isPending}
              >
                Eliminar
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Carreras</h1>
        <Button onClick={() => { resetForm(); setToastError(''); setToastSuccess(''); setShowForm(true); }}>Nueva carrera</Button>
      </div>

      {showForm && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{editId ? 'Editar carrera' : 'Nueva carrera'}</h3>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                <input
                  type="text"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Código *</label>
                <input
                  type="text"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="space-y-1 sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">Descripción</label>
                <textarea
                  value={descripcion}
                  onChange={(e) => setDescripcion(e.target.value)}
                  rows={3}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Estado</label>
                <button
                  type="button"
                  role="switch"
                  aria-checked={estado === 'activa'}
                  onClick={() => setEstado((current) => current === 'activa' ? 'inactiva' : 'activa')}
                  className={`inline-flex h-10 items-center gap-3 rounded-lg border px-3 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                    estado === 'activa'
                      ? 'border-green-200 bg-green-50 text-green-800'
                      : 'border-gray-300 bg-gray-50 text-gray-700'
                  }`}
                >
                  <span
                    className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                      estado === 'activa' ? 'bg-green-600' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform ${
                        estado === 'activa' ? 'translate-x-4' : 'translate-x-1'
                      }`}
                    />
                  </span>
                  {estado === 'activa' ? 'Activa' : 'Inactiva'}
                </button>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={resetForm} type="button">Cancelar</Button>
              <Button type="submit" loading={crear.isPending || actualizar.isPending}>{editId ? 'Actualizar' : 'Crear'}</Button>
            </div>
          </form>
        </Card>
      )}

      <Card className="overflow-hidden">
        <div className="grid grid-cols-1 gap-3 border-b border-gray-200 bg-gray-50 p-4 md:grid-cols-[1fr_1fr_auto]">
          <div className="space-y-1">
            <label className="block text-xs font-medium uppercase text-gray-500">Nombre</label>
            <input
              type="search"
              value={filterNombre}
              onChange={(e) => setFilterNombre(e.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium uppercase text-gray-500">Código</label>
            <input
              type="search"
              value={filterCodigo}
              onChange={(e) => setFilterCodigo(e.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium uppercase text-gray-500">Estado</label>
            <div className="flex h-10 overflow-hidden rounded-lg border border-gray-300 bg-white">
              {[
                ['todos', 'Todos'],
                ['activa', 'Activas'],
                ['inactiva', 'Inactivas'],
              ].map(([value, label]) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setFilterEstado(value as 'todos' | 'activa' | 'inactiva')}
                  className={`px-3 text-sm font-medium transition-colors ${
                    filterEstado === value
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12"><Spinner /></div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Nombre</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Código</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Descripción</th>
                <th className="px-4 py-3 text-center font-medium text-gray-600">Estado</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.items?.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{c.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{c.codigo}</td>
                  <td className="px-4 py-3 text-gray-500">{c.descripcion ?? '-'}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs ${c.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {c.activo ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-1">
                      <IconButton label="Editar" onClick={() => handleEdit(c)}>
                        <EditIcon />
                      </IconButton>
                      {!c.activo && (
                        <IconButton label="Eliminar" onClick={() => handleDelete(c)} loading={eliminar.isPending}>
                          <TrashIcon />
                        </IconButton>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {(!data?.items || data.items.length === 0) && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No hay carreras registradas.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
