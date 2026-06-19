import { useEffect, useId, useState } from 'react'
import { Alert } from '@/shared/components/Alert'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { useCrearUsuario } from '@/features/admin/hooks/useAdmin'
import type { UsuarioAdmin } from '@/features/admin/types'

interface CrearDocenteModalProps {
  initialSearch?: string
  onClose: () => void
  onCreated: (usuario: UsuarioAdmin) => void
}

function buildDraftFromSearch(search: string) {
  const trimmed = search.trim()
  if (!trimmed) {
    return { nombre: '', apellidos: '', email: '' }
  }

  if (trimmed.includes('@')) {
    return { nombre: '', apellidos: '', email: trimmed }
  }

  const [nombre = '', ...resto] = trimmed.split(/\s+/)
  return {
    nombre,
    apellidos: resto.join(' '),
    email: '',
  }
}

export function CrearDocenteModal({
  initialSearch = '',
  onClose,
  onCreated,
}: CrearDocenteModalProps) {
  const crearUsuario = useCrearUsuario()
  const nombreId = useId()
  const apellidosId = useId()
  const emailId = useId()
  const [nombre, setNombre] = useState('')
  const [apellidos, setApellidos] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const draft = buildDraftFromSearch(initialSearch)
    setNombre(draft.nombre)
    setApellidos(draft.apellidos)
    setEmail(draft.email)
    setError('')
  }, [initialSearch])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')

    if (!nombre.trim() || !apellidos.trim() || !email.trim()) {
      setError('Nombre, apellidos y email son obligatorios.')
      return
    }

    try {
      const usuario = await crearUsuario.mutateAsync({
        nombre: nombre.trim(),
        apellidos: apellidos.trim(),
        email: email.trim(),
      })
      onCreated(usuario)
      onClose()
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'No se pudo crear el docente.')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <Card className="w-full max-w-lg p-6" onClick={(event: React.MouseEvent) => event.stopPropagation()}>
        <h2 className="text-lg font-semibold text-gray-900">Crear nuevo docente</h2>
        <p className="mt-1 text-sm text-gray-500">
          Se agrega al selector apenas lo crees. El resto de los datos se puede completar luego desde Usuarios.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {error && <Alert variant="error">{error}</Alert>}

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1">
              <label htmlFor={nombreId} className="block text-sm font-medium text-gray-700">Nombre *</label>
              <input
                id={nombreId}
                type="text"
                value={nombre}
                onChange={(event) => setNombre(event.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div className="space-y-1">
              <label htmlFor={apellidosId} className="block text-sm font-medium text-gray-700">Apellidos *</label>
              <input
                id={apellidosId}
                type="text"
                value={apellidos}
                onChange={(event) => setApellidos(event.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label htmlFor={emailId} className="block text-sm font-medium text-gray-700">Email *</label>
            <input
              id={emailId}
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" loading={crearUsuario.isPending}>
              Crear docente
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
