import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { Spinner } from '@/shared/components/Spinner'
import { useSession } from '@/shared/hooks/useSession'
import { useUsuarios, useCrearUsuario, useActualizarUsuario } from '@/features/admin/hooks/useAdmin'
import type { UsuarioAdmin, UsuarioAdminPayload, UsuarioAdminFilters } from '@/features/admin/types'

const ROLES_DISPONIBLES = ['ALUMNO', 'TUTOR', 'PROFESOR', 'COORDINADOR', 'NEXO', 'ADMIN', 'FINANZAS']

export default function UsuariosPage() {
  const { hasPermission } = useSession()
  const [filters, setFilters] = useState<UsuarioAdminFilters>({ page: 1, limit: 20 })
  const { data, isLoading } = useUsuarios(filters)
  const crear = useCrearUsuario()
  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [dni, setDni] = useState('')
  const [cbu, setCbu] = useState('')
  const [roles, setRoles] = useState<string[]>([])
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [showPII, setShowPII] = useState(false)

  const puedeVerPII = hasPermission('usuarios:gestionar')

  const resetForm = () => {
    setNombre('')
    setEmail('')
    setPassword('')
    setDni('')
    setCbu('')
    setRoles([])
    setEditId(null)
    setShowForm(false)
    setError('')
  }

  const handleEdit = (u: UsuarioAdmin) => {
    setEditId(u.id)
    setNombre(u.nombre)
    setEmail(u.email)
    setDni(u.dni ?? '')
    setCbu(u.cbu ?? '')
    setRoles(u.roles)
    setPassword('')
    setShowForm(true)
  }

  const toggleRol = (rol: string) => {
    setRoles((prev) => prev.includes(rol) ? prev.filter((r) => r !== rol) : [...prev, rol])
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!nombre.trim() || !email.trim() || roles.length === 0) {
      setError('Nombre, email y al menos un rol son obligatorios.')
      return
    }
    if (!editId && !password.trim()) {
      setError('La contraseña es obligatoria para nuevos usuarios.')
      return
    }
    try {
      const payload: UsuarioAdminPayload = {
        nombre: nombre.trim(),
        email: email.trim(),
        password: password.trim() || 'temp123',
        dni: dni.trim() || undefined,
        cbu: cbu.trim() || undefined,
        roles,
      }
      if (editId) {
        const actualizar = useActualizarUsuario(editId)
        await actualizar.mutateAsync(payload)
      } else {
        await crear.mutateAsync(payload)
      }
      resetForm()
    } catch {
      setError('Error al guardar el usuario.')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Usuarios</h1>
        <Button onClick={() => { resetForm(); setShowForm(true) }}>Nuevo usuario</Button>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Nombre</label>
            <input
              type="text"
              value={filters.nombre ?? ''}
              onChange={(e) => setFilters({ ...filters, nombre: e.target.value || undefined, page: 1 })}
              placeholder="Buscar nombre"
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Email</label>
            <input
              type="text"
              value={filters.email ?? ''}
              onChange={(e) => setFilters({ ...filters, email: e.target.value || undefined, page: 1 })}
              placeholder="Buscar email"
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Rol</label>
            <select
              value={filters.rol ?? ''}
              onChange={(e) => setFilters({ ...filters, rol: e.target.value || undefined, page: 1 })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              {ROLES_DISPONIBLES.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
          {puedeVerPII && (
            <div className="flex items-end">
              <label className="flex items-center gap-2 text-sm text-gray-600">
                <input
                  type="checkbox"
                  checked={showPII}
                  onChange={(e) => setShowPII(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                Mostrar PII
              </label>
            </div>
          )}
        </div>
      </Card>

      {showForm && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{editId ? 'Editar usuario' : 'Nuevo usuario'}</h3>
          <form onSubmit={handleSave} className="space-y-4">
            {error && <Alert variant="error">{error}</Alert>}
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
                <label className="block text-sm font-medium text-gray-700">Email *</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              {!editId && (
                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-700">Contraseña *</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required={!editId}
                  />
                </div>
              )}
              {showPII && (
                <>
                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-700">DNI</label>
                    <input
                      type="text"
                      value={dni}
                      onChange={(e) => setDni(e.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-700">CBU</label>
                    <input
                      type="text"
                      value={cbu}
                      onChange={(e) => setCbu(e.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </>
              )}
              <div className="space-y-1 sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">Roles *</label>
                <div className="flex flex-wrap gap-2">
                  {ROLES_DISPONIBLES.map((rol) => (
                    <label key={rol} className="flex items-center gap-1.5 text-sm">
                      <input
                        type="checkbox"
                        checked={roles.includes(rol)}
                        onChange={() => toggleRol(rol)}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      {rol}
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={resetForm} type="button">Cancelar</Button>
              <Button type="submit" loading={crear.isPending}>{editId ? 'Actualizar' : 'Crear'}</Button>
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
                <th className="px-4 py-3 text-left font-medium text-gray-600">Email</th>
                {showPII && <th className="px-4 py-3 text-left font-medium text-gray-600">DNI</th>}
                {showPII && <th className="px-4 py-3 text-left font-medium text-gray-600">CBU</th>}
                <th className="px-4 py-3 text-left font-medium text-gray-600">Roles</th>
                <th className="px-4 py-3 text-center font-medium text-gray-600">Activo</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.items.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{u.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{u.email}</td>
                  {showPII && <td className="px-4 py-3 text-gray-600">{u.dni ?? '••••'}</td>}
                  {showPII && <td className="px-4 py-3 text-gray-600">{u.cbu ?? '••••'}</td>}
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {u.roles.map((r) => (
                        <span key={r} className="inline-flex rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
                          {r}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs ${u.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {u.activo ? 'Sí' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" onClick={() => handleEdit(u)}>Editar</Button>
                  </td>
                </tr>
              ))}
              {(!data?.items || data.items.length === 0) && (
                <tr><td colSpan={showPII ? 7 : 5} className="px-4 py-8 text-center text-gray-500">No hay usuarios registrados.</td></tr>
              )}
            </tbody>
          </table>
        </Card>
      )}

      {data && data.total > (filters.limit ?? 20) && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">
            {((filters.page ?? 1) - 1) * (filters.limit ?? 20) + 1}-{Math.min((filters.page ?? 1) * (filters.limit ?? 20), data.total)} de {data.total}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) - 1 })}
              disabled={(filters.page ?? 1) <= 1}
              className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
            >
              Anterior
            </button>
            <button
              onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) + 1 })}
              disabled={(filters.page ?? 1) * (filters.limit ?? 20) >= data.total}
              className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
