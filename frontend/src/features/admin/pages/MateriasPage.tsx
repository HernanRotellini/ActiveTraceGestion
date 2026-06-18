import { useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { isAxiosError } from 'axios'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import {
  useActualizarMateria,
  useCarreras,
  useCohortes,
  useCrearMateria,
  useMaterias,
} from '@/features/admin/hooks/useAdmin'
import type { Materia, MateriaPayload, MateriaUpdatePayload } from '@/features/admin/types'
import { ApiError } from '@/shared/types/api'

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

function getMateriaErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.message.includes('inactive carrera')) {
      return 'La carrera seleccionada esta inactiva. Activala antes de crear nuevas materias.'
    }
    if (error.message.includes('inactive cohorte')) {
      return 'La cohorte seleccionada esta inactiva. Activala antes de crear nuevas materias.'
    }
    if (error.message.includes('already exists')) {
      return 'Ya existe una materia con ese codigo.'
    }
    if (error.status === 404) {
      return 'No se encontro la carrera, cohorte o materia seleccionada.'
    }
    return error.message || 'No se pudo guardar la materia.'
  }

  if (isAxiosError<{ detail?: string }>(error)) {
    const detail = error.response?.data?.detail ?? ''
    if (detail.includes('inactive carrera')) {
      return 'La carrera seleccionada esta inactiva. Activala antes de crear nuevas materias.'
    }
    if (detail.includes('inactive cohorte')) {
      return 'La cohorte seleccionada esta inactiva. Activala antes de crear nuevas materias.'
    }
    if (detail.includes('already exists')) {
      return 'Ya existe una materia con ese codigo.'
    }
    if (error.response?.status === 404) {
      return 'No se encontro la carrera, cohorte o materia seleccionada.'
    }
    return detail || 'No se pudo guardar la materia.'
  }

  return 'No se pudo guardar la materia.'
}

export default function MateriasPage() {
  const { data: carreras } = useCarreras()
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const { data: cohortes } = useCohortes(carreraId || undefined)
  const { data, isLoading } = useMaterias(carreraId || undefined, cohorteId || undefined)
  const crear = useCrearMateria()
  const actualizar = useActualizarMateria()
  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [codigo, setCodigo] = useState('')
  const [cargaHoraria, setCargaHoraria] = useState('')
  const [estado, setEstado] = useState<'activa' | 'inactiva'>('activa')
  const [formCarreraId, setFormCarreraId] = useState('')
  const [formCohorteId, setFormCohorteId] = useState('')
  const { data: formCohortes } = useCohortes(formCarreraId || undefined)
  const [showForm, setShowForm] = useState(false)
  const [toastError, setToastError] = useState('')
  const [toastSuccess, setToastSuccess] = useState('')

  const selectedFormCarrera = carreras?.items?.find((c) => c.id === formCarreraId)
  const selectedFormCohorte = formCohortes?.items?.find((c) => c.id === formCohorteId)

  const resetForm = () => {
    setNombre('')
    setCodigo('')
    setCargaHoraria('')
    setEstado('activa')
    setFormCarreraId('')
    setFormCohorteId('')
    setEditId(null)
    setShowForm(false)
  }

  const handleCreate = () => {
    resetForm()
    setToastError('')
    setToastSuccess('')
    setFormCarreraId(carreraId)
    setFormCohorteId(cohorteId)
    setShowForm(true)
  }

  const handleEdit = (m: Materia) => {
    setToastError('')
    setToastSuccess('')
    setEditId(m.id)
    setNombre(m.nombre)
    setCodigo(m.codigo)
    setCargaHoraria(m.carga_horaria.toString())
    setEstado(m.activo ? 'activa' : 'inactiva')
    setFormCarreraId(m.carrera_id ?? '')
    setFormCohorteId(m.cohorte_id ?? '')
    setShowForm(true)
  }

  const handleFormCarreraChange = (value: string) => {
    setFormCarreraId(value)
    setFormCohorteId('')
    const carrera = carreras?.items?.find((c) => c.id === value)
    if (carrera && !carrera.activo) {
      setToastError('La carrera seleccionada esta inactiva. No se pueden crear materias nuevas hasta activarla.')
      setToastSuccess('')
    } else {
      setToastError('')
    }
  }

  const handleFormCohorteChange = (value: string) => {
    setFormCohorteId(value)
    const cohorte = formCohortes?.items?.find((c) => c.id === value)
    if (cohorte && !cohorte.activo) {
      setToastError('La cohorte seleccionada esta inactiva. No se pueden crear materias nuevas hasta activarla.')
      setToastSuccess('')
    } else {
      setToastError('')
    }
  }

  const handleCarreraChange = (value: string) => {
    setCarreraId(value)
    setCohorteId('')
    resetForm()
    const carrera = carreras?.items?.find((c) => c.id === value)
    if (carrera && !carrera.activo) {
      setToastError('La carrera seleccionada esta inactiva. No se pueden crear materias nuevas hasta activarla.')
      setToastSuccess('')
    } else {
      setToastError('')
    }
  }

  const handleCohorteChange = (value: string) => {
    setCohorteId(value)
    resetForm()
    const cohorte = cohortes?.items?.find((c) => c.id === value)
    if (cohorte && !cohorte.activo) {
      setToastError('La cohorte seleccionada esta inactiva. No se pueden crear materias nuevas hasta activarla.')
      setToastSuccess('')
    } else {
      setToastError('')
    }
  }

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setToastError('')
    setToastSuccess('')
    if (!nombre.trim() || !codigo.trim() || !cargaHoraria || !formCarreraId || !formCohorteId) {
      setToastError('Nombre, codigo, carga horaria, carrera y cohorte son obligatorios.')
      return
    }
    if (selectedFormCarrera && !selectedFormCarrera.activo) {
      setToastError('La carrera seleccionada esta inactiva. Activala antes de crear nuevas materias.')
      return
    }
    if (selectedFormCohorte && !selectedFormCohorte.activo) {
      setToastError('La cohorte seleccionada esta inactiva. Activala antes de crear nuevas materias.')
      return
    }
    try {
      const basePayload = {
        nombre: nombre.trim(),
        codigo: codigo.trim(),
        carga_horaria: Number(cargaHoraria),
        estado,
      }
      if (editId) {
        const payload: MateriaUpdatePayload = {
          ...basePayload,
          carrera_id: formCarreraId,
          cohorte_id: formCohorteId,
        }
        await actualizar.mutateAsync({ id: editId, ...payload })
        setToastSuccess('Materia actualizada correctamente.')
      } else {
        const payload: MateriaPayload = {
          ...basePayload,
          carrera_id: formCarreraId,
          cohorte_id: formCohorteId,
        }
        await crear.mutateAsync(payload)
        setToastSuccess('Materia creada correctamente.')
      }
      resetForm()
    } catch (caughtError) {
      setToastError(getMateriaErrorMessage(caughtError))
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
        <h1 className="text-2xl font-bold text-gray-900">Materias</h1>
        <Button onClick={handleCreate}>
          Nueva materia
        </Button>
      </div>

      <Card className="p-4">
        <div className="space-y-3">
          <div className="flex flex-wrap gap-4">
            <div className="space-y-1">
              <label className="block text-xs font-medium text-gray-600">Carrera</label>
              <select
                value={carreraId}
                onChange={(e) => handleCarreraChange(e.target.value)}
                className="block w-52 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Todas</option>
                {carreras?.items?.map((c) => (
                  <option key={c.id} value={c.id}>{c.nombre}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <label className="block text-xs font-medium text-gray-600">Cohorte</label>
              <select
                value={cohorteId}
                onChange={(e) => handleCohorteChange(e.target.value)}
                disabled={!carreraId}
                className="block w-52 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
              >
                <option value="">Todos</option>
                {cohortes?.items?.map((c) => (
                  <option key={c.id} value={c.id}>{c.nombre}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </Card>

      {showForm && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{editId ? 'Editar materia' : 'Nueva materia'}</h3>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Carrera *</label>
                <select
                  value={formCarreraId}
                  onChange={(e) => handleFormCarreraChange(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                >
                  <option value="">Seleccione una carrera</option>
                  {carreras?.items?.map((c) => (
                    <option key={c.id} value={c.id}>{c.nombre}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Cohorte *</label>
                <select
                  value={formCohorteId}
                  onChange={(e) => handleFormCohorteChange(e.target.value)}
                  disabled={!formCarreraId}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
                  required
                >
                  <option value="">Seleccione una cohorte</option>
                  {formCohortes?.items?.map((c) => (
                    <option key={c.id} value={c.id}>{c.nombre}</option>
                  ))}
                </select>
              </div>
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
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Carga horaria *</label>
                <input
                  type="number"
                  value={cargaHoraria}
                  onChange={(e) => setCargaHoraria(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                  min={1}
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
                <th className="px-4 py-3 text-left font-medium text-gray-600">Código</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Carrera</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Cohorte</th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">Carga horaria</th>
                <th className="px-4 py-3 text-center font-medium text-gray-600">Estado</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.items?.map((m) => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{m.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{m.codigo}</td>
                  <td className="px-4 py-3 text-gray-500">{m.carrera_nombre ?? '-'}</td>
                  <td className="px-4 py-3 text-gray-500">{m.cohorte_nombre ?? '-'}</td>
                  <td className="px-4 py-3 text-right">{m.carga_horaria}h</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs ${m.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {m.activo ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-1">
                      <IconButton label="Editar" onClick={() => handleEdit(m)}>
                        <EditIcon />
                      </IconButton>
                    </div>
                  </td>
                </tr>
              ))}
              {(!data?.items || data.items.length === 0) && (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-500">No hay materias registradas.</td></tr>
              )}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
