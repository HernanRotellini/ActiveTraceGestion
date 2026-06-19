import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Toast } from '@/shared/components/Toast'
import { Combobox } from '@/shared/components/Combobox'
import { Spinner } from '@/shared/components/Spinner'
import { useAviso, useCrearAviso, useActualizarAviso } from '@/features/avisos/hooks/useAvisos'
import { useCarreras, useCohortes, useMaterias } from '@/features/admin/hooks/useAdmin'
import type { AvisoAlcance, AvisoSeveridad, AvisoPayload } from '@/features/avisos/types'

const ALCANCES: Array<{ value: AvisoAlcance; label: string }> = [
  { value: 'Global', label: 'Global (todos los usuarios)' },
  { value: 'PorRol', label: 'Por rol' },
  { value: 'PorMateria', label: 'Por materia' },
  { value: 'PorCohorte', label: 'Por cohorte' },
]

const SEVERIDADES: Array<{ value: AvisoSeveridad; label: string }> = [
  { value: 'Info', label: 'Info' },
  { value: 'Advertencia', label: 'Advertencia' },
  { value: 'Critico', label: 'Crítico' },
]

const ROL_OPTIONS = ['ALUMNO', 'TUTOR', 'PROFESOR', 'COORDINADOR', 'NEXO', 'ADMIN', 'FINANZAS']

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

export default function AvisoFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id
  const navigate = useNavigate()

  const { data: aviso, isLoading: loadingAviso } = useAviso(id ?? '')
  const crear = useCrearAviso()
  const actualizar = useActualizarAviso(id ?? '')

  const [titulo, setTitulo] = useState('')
  const [cuerpo, setCuerpo] = useState('')
  const [alcance, setAlcance] = useState<AvisoAlcance>('Global')
  const [severidad, setSeveridad] = useState<AvisoSeveridad>('Info')
  const [rolDestino, setRolDestino] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [inicioEn, setInicioEn] = useState(todayIsoDate())
  const [finEn, setFinEn] = useState('')
  const [requiereAck, setRequiereAck] = useState(false)
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  const { data: carrerasResp, isLoading: loadingCarreras } = useCarreras()
  const { data: cohortesResp, isLoading: loadingCohortes } = useCohortes(carreraId || undefined)
  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias(carreraId || undefined, cohorteId || undefined)

  const carreraItems = (carrerasResp?.items ?? []).map((c) => ({ value: c.id, label: c.nombre }))
  const cohorteItems = (cohortesResp?.items ?? []).map((c) => ({ value: c.id, label: `${c.nombre} (${c.anio})` }))
  const materiaItems = (materiasResp?.items ?? []).map((m) => ({ value: m.id, label: `${m.nombre} (${m.codigo})` }))

  useEffect(() => {
    if (aviso) {
      setTitulo(aviso.titulo)
      setCuerpo(aviso.cuerpo)
      setAlcance(aviso.alcance)
      setSeveridad(aviso.severidad)
      setRolDestino(aviso.rol_destino ?? '')
      setMateriaId(aviso.materia_id ?? '')
      setCohorteId(aviso.cohorte_id ?? '')
      setInicioEn(aviso.inicio_en.slice(0, 10))
      setFinEn(aviso.fin_en ? aviso.fin_en.slice(0, 10) : '')
      setRequiereAck(aviso.requiere_ack)
    }
  }, [aviso])

  const validate = () => {
    if (!titulo.trim()) return 'El título es obligatorio.'
    if (!cuerpo.trim()) return 'El cuerpo es obligatorio.'
    if (!inicioEn) return 'La fecha de inicio es obligatoria.'
    if (alcance === 'PorRol' && !rolDestino.trim()) return 'Seleccioná un rol para el alcance PorRol.'
    if (alcance === 'PorMateria' && !materiaId) return 'Seleccioná una materia para el alcance PorMateria.'
    if (alcance === 'PorCohorte' && !cohorteId) return 'Seleccioná una cohorte para el alcance PorCohorte.'
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const validationError = validate()
    if (validationError) {
      setToast({ message: validationError, variant: 'error' })
      return
    }

    const payload: AvisoPayload = {
      titulo: titulo.trim(),
      cuerpo: cuerpo.trim(),
      alcance,
      severidad,
      inicio_en: new Date(inicioEn).toISOString(),
      fin_en: finEn ? new Date(finEn).toISOString() : undefined,
      requiere_ack: requiereAck,
      rol_destino: alcance === 'PorRol' ? rolDestino : undefined,
      materia_id: alcance === 'PorMateria' ? materiaId : undefined,
      cohorte_id: alcance === 'PorCohorte' ? cohorteId : undefined,
    }

    try {
      if (isEdit) {
        await actualizar.mutateAsync(payload)
        setToast({ message: 'Aviso actualizado correctamente.', variant: 'success' })
        window.setTimeout(() => navigate('/coordinacion/avisos'), 800)
      } else {
        await crear.mutateAsync(payload)
        setToast({ message: 'Aviso creado correctamente.', variant: 'success' })
        window.setTimeout(() => navigate('/coordinacion/avisos'), 800)
      }
    } catch {
      setToast({ message: 'Error al guardar el aviso.', variant: 'error' })
    }
  }

  if (isEdit && loadingAviso) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {toast && <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />}

      <h1 className="text-2xl font-bold text-gray-900">
        {isEdit ? 'Editar Aviso' : 'Nuevo Aviso'}
      </h1>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
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
              value={cuerpo}
              onChange={(e) => setCuerpo(e.target.value)}
              rows={5}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Alcance *</label>
              <select
                value={alcance}
                onChange={(e) => { setAlcance(e.target.value as AvisoAlcance); setRolDestino(''); setMateriaId(''); setCohorteId('') }}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {ALCANCES.map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
              </select>
            </div>

            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Severidad</label>
              <select
                value={severidad}
                onChange={(e) => setSeveridad(e.target.value as AvisoSeveridad)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {SEVERIDADES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
          </div>

          {alcance === 'PorRol' && (
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Rol destinatario *</label>
              <select
                value={rolDestino}
                onChange={(e) => setRolDestino(e.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Seleccioná un rol</option>
                {ROL_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          )}

          {alcance === 'PorMateria' && (
            <div className="grid gap-4 md:grid-cols-2">
              <Combobox
                label="Carrera"
                items={carreraItems}
                value={carreraId}
                onChange={(v) => { setCarreraId(v); setCohorteId(''); setMateriaId('') }}
                placeholder="Buscar carrera..."
                isLoading={loadingCarreras}
              />
              <Combobox
                label="Materia *"
                items={materiaItems}
                value={materiaId}
                onChange={setMateriaId}
                placeholder="Buscar materia..."
                isLoading={loadingMaterias}
              />
            </div>
          )}

          {alcance === 'PorCohorte' && (
            <div className="grid gap-4 md:grid-cols-2">
              <Combobox
                label="Carrera"
                items={carreraItems}
                value={carreraId}
                onChange={(v) => { setCarreraId(v); setCohorteId('') }}
                placeholder="Buscar carrera..."
                isLoading={loadingCarreras}
              />
              <Combobox
                label="Cohorte *"
                items={cohorteItems}
                value={cohorteId}
                onChange={setCohorteId}
                placeholder={carreraId ? 'Buscar cohorte...' : 'Seleccioná una carrera'}
                isLoading={loadingCohortes}
                disabled={!carreraId}
              />
            </div>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Inicio *</label>
              <input
                type="date"
                value={inicioEn}
                onChange={(e) => setInicioEn(e.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Vencimiento</label>
              <input
                type="date"
                value={finEn}
                min={inicioEn}
                onChange={(e) => setFinEn(e.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={requiereAck}
              onChange={(e) => setRequiereAck(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">Requiere confirmación de lectura</span>
          </label>

          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => navigate('/coordinacion/avisos')}>
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
