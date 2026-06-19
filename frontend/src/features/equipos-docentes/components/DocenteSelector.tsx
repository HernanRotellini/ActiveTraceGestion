import { useState } from 'react'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { UsuarioAdmin } from '@/features/admin/types'
import { CrearDocenteModal } from '@/features/equipos-docentes/components/CrearDocenteModal'
import { Button } from '@/shared/components/Button'
import { Combobox } from '@/shared/components/Combobox'

const DOCENTE_ROLES = new Set(['PROFESOR', 'TUTOR', 'COORDINADOR', 'NEXO'])

interface DocenteSelectorProps {
  selectedIds: string[]
  onChange: (usuarioIds: string[]) => void
  label?: string
}

function mergeUsuarios(base: UsuarioAdmin[], created: UsuarioAdmin[]) {
  const byId = new Map<string, UsuarioAdmin>()
  base.forEach((usuario) => byId.set(usuario.id, usuario))
  created.forEach((usuario) => byId.set(usuario.id, usuario))
  return Array.from(byId.values())
}

function isDocente(usuario: UsuarioAdmin) {
  if (usuario.estado !== 'activo') return false
  if (!usuario.roles?.length) return true
  return usuario.roles.some((rol) => DOCENTE_ROLES.has(rol))
}

function docenteLabel(usuario: UsuarioAdmin) {
  return `${usuario.nombre} ${usuario.apellidos} (${usuario.email})`
}

export function DocenteSelector({
  selectedIds,
  onChange,
  label = 'Docentes *',
}: DocenteSelectorProps) {
  const { data: usuariosResp, isLoading } = useUsuarios()
  const [usuarioId, setUsuarioId] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [initialSearch, setInitialSearch] = useState('')
  const [createdUsuarios, setCreatedUsuarios] = useState<UsuarioAdmin[]>([])

  const usuariosDocentes = mergeUsuarios(usuariosResp?.items ?? [], createdUsuarios).filter(isDocente)
  const selectedUsuarios = usuariosDocentes.filter((usuario) => selectedIds.includes(usuario.id))
  const usuarioItems = usuariosDocentes
    .filter((usuario) => !selectedIds.includes(usuario.id))
    .map((usuario) => ({
      value: usuario.id,
      label: docenteLabel(usuario),
    }))

  const addUsuario = () => {
    if (!usuarioId || selectedIds.includes(usuarioId)) return
    onChange([...selectedIds, usuarioId])
    setUsuarioId('')
  }

  const removeUsuario = (id: string) => {
    onChange(selectedIds.filter((usuarioIdItem) => usuarioIdItem !== id))
  }

  const handleCreated = (usuario: UsuarioAdmin) => {
    setCreatedUsuarios((current) => mergeUsuarios(current, [usuario]))
    setUsuarioId('')
    if (!selectedIds.includes(usuario.id)) {
      onChange([...selectedIds, usuario.id])
    }
  }

  return (
    <>
      <section className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">{label}</label>
        <div className="flex gap-2">
          <div className="flex-1">
            <Combobox
              label=""
              items={usuarioItems}
              value={usuarioId}
              onChange={setUsuarioId}
              placeholder="Buscar docente..."
              isLoading={isLoading}
              noResultsText="No hay docentes disponibles."
              actions={[
                {
                  id: 'crear-docente',
                  label: 'Crear nuevo docente',
                  onSelect: (search) => {
                    setInitialSearch(search)
                    setShowCreateModal(true)
                  },
                },
              ]}
            />
          </div>
          <Button type="button" variant="secondary" onClick={addUsuario} disabled={!usuarioId}>
            Agregar
          </Button>
        </div>

        {selectedUsuarios.length > 0 ? (
          <div className="rounded-lg border border-gray-200">
            {selectedUsuarios.map((usuario) => (
              <div key={usuario.id} className="flex items-center justify-between border-b px-3 py-2 last:border-b-0">
                <div>
                  <p className="text-sm font-medium text-gray-900">{usuario.nombre} {usuario.apellidos}</p>
                  <p className="text-xs text-gray-500">{usuario.email}</p>
                </div>
                <button
                  type="button"
                  onClick={() => removeUsuario(usuario.id)}
                  className="rounded px-2 py-1 text-sm text-red-600 hover:bg-red-50"
                >
                  Quitar
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Todavía no agregaste docentes.</p>
        )}
      </section>

      {showCreateModal && (
        <CrearDocenteModal
          initialSearch={initialSearch}
          onClose={() => setShowCreateModal(false)}
          onCreated={handleCreated}
        />
      )}
    </>
  )
}
