import { useState } from 'react'
import { useCrearUsuario, useActualizarUsuario, useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { UsuarioAdmin, UsuarioAdminFilters, UsuarioAdminPayload } from '@/features/admin/types'
import { Alert } from '@/shared/components/Alert'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { useSession } from '@/shared/hooks/useSession'

export default function UsuariosPage() {
  const { hasPermission } = useSession()
  const [filters, setFilters] = useState<UsuarioAdminFilters>({})
  const { data, isLoading } = useUsuarios(filters)
  const crear = useCrearUsuario()
  const actualizar = useActualizarUsuario()

  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [apellidos, setApellidos] = useState('')
  const [email, setEmail] = useState('')
  const [dni, setDni] = useState('')
  const [cuil, setCuil] = useState('')
  const [cbu, setCbu] = useState('')
  const [telefono, setTelefono] = useState('')
  const [direccion, setDireccion] = useState('')
  const [legajo, setLegajo] = useState('')
  const [banco, setBanco] = useState('')
  const [facturador, setFacturador] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [showPII, setShowPII] = useState(false)

  const puedeVerPII = hasPermission('usuarios:gestionar')

  const resetForm = () => {
    setNombre('')
    setApellidos('')
    setEmail('')
    setDni('')
    setCuil('')
    setCbu('')
    setTelefono('')
    setDireccion('')
    setLegajo('')
    setBanco('')
    setFacturador(false)
    setEditId(null)
    setShowForm(false)
    setError('')
  }

  const handleEdit = (usuario: UsuarioAdmin) => {
    setEditId(usuario.id)
    setNombre(usuario.nombre)
    setApellidos(usuario.apellidos ?? '')
    setEmail(usuario.email)
    setDni(usuario.dni ?? '')
    setCuil(usuario.cuil ?? '')
    setCbu(usuario.cbu ?? '')
    setTelefono(usuario.telefono ?? '')
    setDireccion(usuario.direccion ?? '')
    setLegajo(usuario.legajo ?? '')
    setBanco(usuario.banco ?? '')
    setFacturador(usuario.facturador ?? false)
    setShowForm(true)
  }

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')

    if (!nombre.trim() || !apellidos.trim() || !email.trim()) {
      setError('Nombre, apellidos y email son obligatorios.')
      return
    }

    try {
      const payload: UsuarioAdminPayload = {
        nombre: nombre.trim(),
        apellidos: apellidos.trim(),
        email: email.trim(),
        dni: dni.trim() || undefined,
        cuil: cuil.trim() || undefined,
        cbu: cbu.trim() || undefined,
        telefono: telefono.trim() || undefined,
        direccion: direccion.trim() || undefined,
        legajo: legajo.trim() || undefined,
        banco: banco.trim() || undefined,
        facturador,
      }

      if (editId) {
        await actualizar.mutateAsync({ id: editId, ...payload })
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
              onChange={(event) => setFilters({ ...filters, nombre: event.target.value || undefined })}
              placeholder="Buscar nombre"
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Email</label>
            <input
              type="text"
              value={filters.email ?? ''}
              onChange={(event) => setFilters({ ...filters, email: event.target.value || undefined })}
              placeholder="Buscar email"
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {puedeVerPII && (
            <div className="flex items-end">
              <label className="flex items-center gap-2 text-sm text-gray-600">
                <input
                  type="checkbox"
                  checked={showPII}
                  onChange={(event) => setShowPII(event.target.checked)}
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
                  onChange={(event) => setNombre(event.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Apellidos *</label>
                <input
                  type="text"
                  value={apellidos}
                  onChange={(event) => setApellidos(event.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Email *</label>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              {showPII && (
                <>
                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-700">DNI</label>
                    <input
                      type="text"
                      value={dni}
                      onChange={(event) => setDni(event.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-700">CUIL</label>
                    <input
                      type="text"
                      value={cuil}
                      onChange={(event) => setCuil(event.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-700">CBU</label>
                    <input
                      type="text"
                      value={cbu}
                      onChange={(event) => setCbu(event.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-700">Telefono</label>
                    <input
                      type="text"
                      value={telefono}
                      onChange={(event) => setTelefono(event.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div className="space-y-1 sm:col-span-2">
                    <label className="block text-sm font-medium text-gray-700">Direccion</label>
                    <input
                      type="text"
                      value={direccion}
                      onChange={(event) => setDireccion(event.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-700">Legajo</label>
                    <input
                      type="text"
                      value={legajo}
                      onChange={(event) => setLegajo(event.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-700">Banco</label>
                    <input
                      type="text"
                      value={banco}
                      onChange={(event) => setBanco(event.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="flex items-center gap-2 pt-6 text-sm">
                      <input
                        type="checkbox"
                        checked={facturador}
                        onChange={(event) => setFacturador(event.target.checked)}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      Facturador
                    </label>
                  </div>
                </>
              )}

              <div className="sm:col-span-2">
                <p className="rounded-lg bg-gray-50 px-3 py-2 text-sm text-gray-600">
                  Los roles y permisos del usuario se administran desde el modulo RBAC, no desde esta pantalla.
                </p>
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
                <th className="px-4 py-3 text-center font-medium text-gray-600">Activo</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100">
              {data?.items?.map((usuario) => (
                <tr key={usuario.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{usuario.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{usuario.email}</td>
                  {showPII && <td className="px-4 py-3 text-gray-600">{usuario.dni ?? '----'}</td>}
                  {showPII && <td className="px-4 py-3 text-gray-600">{usuario.cbu ?? '----'}</td>}
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs ${usuario.estado === 'activo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {usuario.estado === 'activo' ? 'Si' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" onClick={() => handleEdit(usuario)}>Editar</Button>
                  </td>
                </tr>
              ))}

              {(!data?.items || data.items.length === 0) && (
                <tr>
                  <td colSpan={showPII ? 6 : 4} className="px-4 py-8 text-center text-gray-500">
                    No hay usuarios registrados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
