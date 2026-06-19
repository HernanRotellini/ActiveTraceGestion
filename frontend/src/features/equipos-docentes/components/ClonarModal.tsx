import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Combobox } from '@/shared/components/Combobox'
import { Toast } from '@/shared/components/Toast'
import { useClonarEquipo } from '@/features/equipos-docentes/hooks/useEquipos'
import { useCarreras, useCohortes, useMaterias } from '@/features/admin/hooks/useAdmin'

interface ClonarModalProps {
  onClose: () => void
}

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

export function ClonarModal({ onClose }: ClonarModalProps) {
  const [origenCarreraId, setOrigenCarreraId] = useState('')
  const [origenCohorteId, setOrigenCohorteId] = useState('')
  const [origenMateriaId, setOrigenMateriaId] = useState('')

  const [destinoCarreraId, setDestinoCarreraId] = useState('')
  const [destinoCohorteId, setDestinoCohorteId] = useState('')
  const [desde, setDesde] = useState(todayIsoDate())
  const [hasta, setHasta] = useState('')

  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const mutation = useClonarEquipo()

  const { data: carrerasResp, isLoading: loadingCarreras } = useCarreras()
  const { data: origenCohortesResp, isLoading: loadingOrigenCohortes } = useCohortes(origenCarreraId || undefined)
  const { data: origenMateriasResp, isLoading: loadingOrigenMaterias } = useMaterias(origenCarreraId || undefined, origenCohorteId || undefined)
  const { data: destinoCohortesResp, isLoading: loadingDestinoCohortes } = useCohortes(destinoCarreraId || undefined)

  const carreraItems = (carrerasResp?.items ?? []).map((c) => ({ value: c.id, label: c.nombre }))
  const origenCohorteItems = (origenCohortesResp?.items ?? []).map((c) => ({ value: c.id, label: `${c.nombre} (${c.anio})` }))
  const origenMateriaItems = (origenMateriasResp?.items ?? []).map((m) => ({ value: m.id, label: `${m.nombre} (${m.codigo})` }))
  const destinoCohorteItems = (destinoCohortesResp?.items ?? []).map((c) => ({ value: c.id, label: `${c.nombre} (${c.anio})` }))

  const handleSubmit = async () => {
    if (!origenCarreraId || !origenCohorteId || !origenMateriaId || !destinoCarreraId || !destinoCohorteId || !desde) {
      setErrorMsg('Completá todos los campos requeridos.')
      return
    }
    try {
      await mutation.mutateAsync({
        origen: { materia_id: origenMateriaId, carrera_id: origenCarreraId, cohorte_id: origenCohorteId },
        destino: { carrera_id: destinoCarreraId, cohorte_id: destinoCohorteId, desde, hasta: hasta || undefined },
      })
      onClose()
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'No se pudo clonar el equipo.')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <Card className="w-full max-w-lg p-6" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Clonar Equipo</h2>

        {errorMsg && (
          <div className="mb-4">
            <Toast message={errorMsg} variant="error" onClose={() => setErrorMsg(null)} />
          </div>
        )}

        <div className="space-y-4">
          <p className="text-sm font-medium text-gray-700">Origen</p>

          <Combobox
            label="Carrera origen *"
            items={carreraItems}
            value={origenCarreraId}
            onChange={(v) => { setOrigenCarreraId(v); setOrigenCohorteId(''); setOrigenMateriaId('') }}
            placeholder="Buscar carrera..."
            isLoading={loadingCarreras}
          />
          <Combobox
            label="Cohorte origen *"
            items={origenCohorteItems}
            value={origenCohorteId}
            onChange={(v) => { setOrigenCohorteId(v); setOrigenMateriaId('') }}
            placeholder={origenCarreraId ? 'Buscar cohorte...' : 'Seleccioná carrera'}
            isLoading={loadingOrigenCohortes}
            disabled={!origenCarreraId}
          />
          <Combobox
            label="Materia origen *"
            items={origenMateriaItems}
            value={origenMateriaId}
            onChange={setOrigenMateriaId}
            placeholder={origenCohorteId ? 'Buscar materia...' : 'Seleccioná cohorte'}
            isLoading={loadingOrigenMaterias}
            disabled={!origenCarreraId || !origenCohorteId}
          />

          <p className="text-sm font-medium text-gray-700 pt-2">Destino</p>

          <Combobox
            label="Carrera destino *"
            items={carreraItems}
            value={destinoCarreraId}
            onChange={(v) => { setDestinoCarreraId(v); setDestinoCohorteId('') }}
            placeholder="Buscar carrera..."
            isLoading={loadingCarreras}
          />
          <Combobox
            label="Cohorte destino *"
            items={destinoCohorteItems}
            value={destinoCohorteId}
            onChange={setDestinoCohorteId}
            placeholder={destinoCarreraId ? 'Buscar cohorte...' : 'Seleccioná carrera'}
            isLoading={loadingDestinoCohortes}
            disabled={!destinoCarreraId}
          />

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vigencia desde *</label>
              <input
                type="date"
                value={desde}
                onChange={(e) => setDesde(e.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vigencia hasta</label>
              <input
                type="date"
                value={hasta}
                min={desde}
                onChange={(e) => setHasta(e.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSubmit} loading={mutation.isPending}>Clonar</Button>
        </div>
      </Card>
    </div>
  )
}
