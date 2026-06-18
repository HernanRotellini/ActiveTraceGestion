import { useMemo, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { isAxiosError } from 'axios'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import { ApiError } from '@/shared/types/api'
import {
  useActualizarCohorte,
  useCarreras,
  useCohortes,
  useCrearCohorte,
} from '@/features/admin/hooks/useAdmin'
import type { Cohorte, CohortePayload, CohorteUpdatePayload } from '@/features/admin/types'

function EditIcon() {
  return (
    <svg className="h-5 w-5" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487 19.5 7.125M18.225 3.125a1.75 1.75 0 0 1 2.475 2.475L8.25 18.05 4.5 19.125l1.075-3.75 12.65-12.25Z" />
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

function formatDate(value?: string | null) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('es-AR', { timeZone: 'UTC' }).format(new Date(value))
}

function getCohorteErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.message.includes('inactive carrera')) {
      return 'La carrera seleccionada esta inactiva. Activala antes de crear nuevas cohortes.'
    }
    if (error.message.includes('already exists')) {
      return 'Ya existe una cohorte con ese nombre para la carrera seleccionada.'
    }
    if (error.status === 404) {
      return 'No se encontro la carrera o cohorte seleccionada.'
    }
    return error.message || 'No se pudo guardar la cohorte.'
  }

  if (isAxiosError<{ detail?: string }>(error)) {
    const detail = error.response?.data?.detail ?? ''
    if (detail.includes('inactive carrera')) {
      return 'La carrera seleccionada esta inactiva. Activala antes de crear nuevas cohortes.'
    }
    if (detail.includes('already exists')) {
      return 'Ya existe una cohorte con ese nombre para la carrera seleccionada.'
    }
    if (error.response?.status === 404) {
      return 'No se encontro la carrera o cohorte seleccionada.'
    }
    return detail || 'No se pudo guardar la cohorte.'
  }

  return 'No se pudo guardar la cohorte.'
}

export default function CohortesPage() {
  const { data: carreras } = useCarreras()
  const [carreraId, setCarreraId] = useState('')
  const { data, isLoading } = useCohortes(carreraId || undefined)
  const crear = useCrearCohorte()
  const actualizar = useActualizarCohorte()
  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [anio, setAnio] = useState(String(new Date().getFullYear()))
  const [vigDesde, setVigDesde] = useState('')
  const [vigHasta, setVigHasta] = useState('')
  const [estado, setEstado] = useState<'activa' | 'inactiva'>('activa')
  const [showForm, setShowForm] = useState(false)
  const [toastError, setToastError] = useState('')
  const [toastSuccess, setToastSuccess] = useState('')

  const selectedCarrera = carreras?.items?.find((c) => c.id === carreraId)
  const years = useMemo(() => Array.from({ length: 101 }, (_, index) => 2000 + index), [])

  const resetForm = () => {
    setNombre('')
    setAnio(String(new Date().getFullYear()))
    setVigDesde('')
    setVigHasta('')
    setEstado('activa')
    setEditId(null)
    setShowForm(false)
  }

  const handleEdit = (c: Cohorte) => {
    setToastError('')
    setToastSuccess('')
    setEditId(c.id)
    setNombre(c.nombre)
    setAnio(c.anio.toString())
    setVigDesde(c.vig_desde)
    setVigHasta(c.vig_hasta ?? '')
    setEstado(c.activo ? 'activa' : 'inactiva')
    setShowForm(true)
  }

  const handleCarreraChange = (value: string) => {
    setCarreraId(value)
    resetForm()
    const carrera = carreras?.items?.find((c) => c.id === value)
    if (carrera && !carrera.activo) {
      setToastError('La carrera seleccionada esta inactiva. No se pueden crear cohortes nuevas hasta activarla.')
      setToastSuccess('')
    } else {
      setToastError('')
    }
  }

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setToastError('')
    setToastSuccess('')
    if (!nombre.trim() || !anio || !vigDesde || !carreraId) {
      setToastError('Nombre, año, vigencia desde y carrera son obligatorios.')
      return
    }
    if (!editId && selectedCarrera && !selectedCarrera.activo) {
      setToastError('La carrera seleccionada esta inactiva. Activala antes de crear nuevas cohortes.')
      return
    }
    try {
      const basePayload = {
        nombre: nombre.trim(),
        anio: Number(anio),
        vig_desde: vigDesde,
        vig_hasta: vigHasta || undefined,
        estado,
      }
      if (editId) {
        const payload: CohorteUpdatePayload = {
          ...basePayload,
          vig_hasta: vigHasta || null,
        }
        await actualizar.mutateAsync({ id: editId, ...payload })
        setToastSuccess('Cohorte actualizada correctamente.')
      } else {
        const payload: CohortePayload = { carrera_id: carreraId, ...basePayload }
        await crear.mutateAsync(payload)
        setToastSuccess('Cohorte creada correctamente.')
      }
      resetForm()
    } catch (caughtError) {
      setToastError(getCohorteErrorMessage(caughtError))
    }
  }

  return (
    <div className="space-y-6">
      {toastError ? (
        <Toast message={toastError} variant="error" onClose={() => setToastError('')} />
      ) : (
        <Toast message={toastSuccess} variant="success" onClose={() => setToastSuccess('')} />
      )}

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Cohortes</h1>
        <Button onClick={() => { resetForm(); setToastError(''); setToastSuccess(''); setShowForm(true) }} disabled={!carreraId}>
          Nueva cohorte
        </Button>
      </div>

      <Card className="p-4">
        <div className="space-y-3">
          <div className="space-y-1 max-w-xs">
            <label className="block text-xs font-medium text-gray-600">Carrera *</label>
            <select
              value={carreraId}
              onChange={(e) => handleCarreraChange(e.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Seleccione una carrera</option>
              {carreras?.items?.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {showForm && carreraId && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{editId ? 'Editar cohorte' : 'Nueva cohorte'}</h3>
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
                <label className="block text-sm font-medium text-gray-700">Año *</label>
                <select
                  value={anio}
                  onChange={(e) => setAnio(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                >
                  {years.map((year) => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Vigencia desde *</label>
                <input
                  type="date"
                  value={vigDesde}
                  onChange={(e) => setVigDesde(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Vigencia hasta</label>
                <input
                  type="date"
                  value={vigHasta}
                  onChange={(e) => setVigHasta(e.target.value)}
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
              <Button type="submit" loading={crear.isPending || actualizar.isPending}>
                {editId && <EditIcon />}
                {editId ? 'Actualizar' : 'Crear'}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <Card className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Nombre</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Año</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Vigencia desde</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Vigencia hasta</th>
                <th className="px-4 py-3 text-center font-medium text-gray-600">Estado</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.items?.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{c.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{c.anio}</td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(c.vig_desde)}</td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(c.vig_hasta)}</td>
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
                    </div>
                  </td>
                </tr>
              ))}
              {(!data?.items || data.items.length === 0) && (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-500">No hay cohortes registradas.</td></tr>
              )}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
