import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { useAsignacionMasiva } from '@/features/equipos-docentes/hooks/useEquipos'
import type { Asignacion, AsignacionMasivaPayload } from '@/features/equipos-docentes/types'

interface AsignacionMasivaModalProps {
  equipoId: string
  onClose: () => void
}

const ROLES: Asignacion['rol'][] = ['titular', 'adjunto', 'auxiliar', 'jefe_tp']

export function AsignacionMasivaModal({ equipoId, onClose }: AsignacionMasivaModalProps) {
  const [usuarios, setUsuarios] = useState<AsignacionMasivaPayload['usuarios']>([{ usuario_id: '', rol: 'auxiliar' }])
  const mutation = useAsignacionMasiva()

  const handleSubmit = async () => {
    const validos = usuarios.filter((u) => u.usuario_id.trim())
    if (validos.length === 0) return
    try {
      await mutation.mutateAsync({ equipo_id: equipoId, usuarios: validos })
      onClose()
    } catch {
      // error handled by mutation
    }
  }

  const agregarFila = () => setUsuarios([...usuarios, { usuario_id: '', rol: 'auxiliar' }])

  const actualizar = (index: number, field: 'usuario_id' | 'rol', value: string) => {
    const nuevos = [...usuarios]
    nuevos[index] = { ...nuevos[index], [field]: value }
    setUsuarios(nuevos)
  }

  const quitarFila = (index: number) => {
    if (usuarios.length > 1) setUsuarios(usuarios.filter((_, i) => i !== index))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <Card className="w-full max-w-lg p-6" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Asignación Masiva</h2>

        <div className="space-y-3">
          {usuarios.map((u, i) => (
            <div key={i} className="flex items-center gap-2">
              <input
                type="text"
                value={u.usuario_id}
                onChange={(e) => actualizar(i, 'usuario_id', e.target.value)}
                placeholder="ID de usuario"
                className="block flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <select
                value={u.rol}
                onChange={(e) => actualizar(i, 'rol', e.target.value)}
                className="block w-32 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => quitarFila(i)}
                className="text-red-500 hover:text-red-700 disabled:opacity-30"
                disabled={usuarios.length <= 1}
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        <div className="mt-3">
          <Button variant="ghost" onClick={agregarFila}>
            + Agregar usuario
          </Button>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSubmit} loading={mutation.isPending}>Asignar</Button>
        </div>
      </Card>
    </div>
  )
}
