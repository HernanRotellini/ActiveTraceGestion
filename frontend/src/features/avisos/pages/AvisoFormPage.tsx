import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { Combobox } from '@/shared/components/Combobox'
import { useAviso, useCrearAviso, useActualizarAviso } from '@/features/avisos/hooks/useAvisos'
import { Spinner } from '@/shared/components/Spinner'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { AvisoScope, AvisoAlcance, AvisoPayload } from '@/features/avisos/types'

const SCOPES: { value: AvisoScope; label: string }[] = [
  { value: 'todos', label: 'Todos los usuarios' },
  { value: 'por_rol', label: 'Por rol' },
  { value: 'por_comision', label: 'Por comisión' },
  { value: 'por_usuario', label: 'Por usuario' },
]

export default function AvisoFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id
  const navigate = useNavigate()

  const { data: aviso, isLoading: loadingAviso } = useAviso(id ?? '')
  const crear = useCrearAviso()
  const actualizar = useActualizarAviso(id ?? '')

  const [titulo, setTitulo] = useState('')
  const [contenido, setContenido] = useState('')
  const [scope, setScope] = useState<AvisoScope>('todos')
  const [scopeValor, setScopeValor] = useState('')
  const [error, setError] = useState('')

  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()

  // Map API alcance back to form scope
  function alcanceToScope(alcance: string): AvisoScope {
    const map: Record<string, AvisoScope> = {
      Global: 'todos',
      PorRol: 'por_rol',
      PorMateria: 'por_comision',
      PorCohorte: 'todos',
    }
    return map[alcance] ?? 'todos'
  }
  const usuarioItems = (usuariosResp?.items ?? []).map((u) => ({
    value: u.id,
    label: `${u.nombre} (${u.email})`,
  }))

  useState(() => {
    if (aviso) {
      setTitulo(aviso.titulo)
      setContenido(aviso.contenido ?? aviso.cuerpo ?? '')
      setScope(alcanceToScope(aviso.scope ?? aviso.alcance ?? ''))
      setScopeValor(aviso.scope_valor ?? aviso.materia_id ?? aviso.rol_destino ?? '')
    }
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!titulo.trim() || !contenido.trim()) {
      setError('El título y el contenido son obligatorios.')
      return
    }

    // Map form scope/scope_valor to API alcance + target fields
    const alcanceMap: Record<string, AvisoAlcance> = {
      todos: 'Global',
      por_rol: 'PorRol',
      por_comision: 'PorMateria',
      por_usuario: 'Global', // fallback
    }

    const payload: AvisoPayload = {
      titulo: titulo.trim(),
      cuerpo: contenido.trim(),
      alcance: alcanceMap[scope] ?? 'Global',
      inicio_en: new Date().toISOString(),
    }

    if (scope === 'por_rol' && scopeValor) {
      payload.rol_destino = scopeValor
    }
    if (scope === 'por_comision' && scopeValor) {
      payload.materia_id = scopeValor
    }

    try {
      if (isEdit) {
        await actualizar.mutateAsync(payload)
      } else {
        await crear.mutateAsync(payload)
      }
      navigate('/coordinacion/avisos')
    } catch {
      setError('Error al guardar el aviso.')
    }
  }

  if (isEdit && loadingAviso) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">
        {isEdit ? 'Editar Aviso' : 'Nuevo Aviso'}
      </h1>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <Alert variant="error">{error}</Alert>}

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Título *</label>
            <input
              type="text"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Contenido *</label>
            <textarea
              value={contenido}
              onChange={(e) => setContenido(e.target.value)}
              rows={5}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Alcance</label>
            <select
              value={scope}
              onChange={(e) => setScope(e.target.value as AvisoScope)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {SCOPES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>

          {scope !== 'todos' && scope === 'por_usuario' && (
            <Combobox
              label="Usuario"
              items={usuarioItems}
              value={scopeValor}
              onChange={setScopeValor}
              placeholder="Buscar usuario..."
              isLoading={loadingUsuarios}
            />
          )}

          {scope !== 'todos' && scope !== 'por_usuario' && (
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">
                {scope === 'por_rol' ? 'Rol' : 'Comisión ID'}
              </label>
              <input
                type="text"
                value={scopeValor}
                onChange={(e) => setScopeValor(e.target.value)}
                placeholder={scope === 'por_rol' ? 'Ej: PROFESOR, ALUMNO' : 'ID de comisión'}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" onClick={() => navigate('/coordinacion/avisos')}>
              Cancelar
            </Button>
            <Button type="submit" loading={crear.isPending || actualizar.isPending}>
              {isEdit ? 'Guardar cambios' : 'Crear aviso'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
