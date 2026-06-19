import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { useSession } from '@/shared/hooks/useSession'
import { useCalificaciones } from '@/features/comisiones/hooks/useCalificaciones'
import { useAtrasados } from '@/features/comisiones/hooks/useAtrasados'
import { useRanking } from '@/features/comisiones/hooks/useRanking'
import { useNotasFinales } from '@/features/comisiones/hooks/useNotasFinales'
import { useMiComision } from '@/features/comisiones/hooks/useMisComisiones'
import { ImportPreview } from '@/features/comisiones/components/ImportPreview'
import { UmbralForm } from '@/features/comisiones/components/UmbralForm'
import { AtrasadosTable } from '@/features/comisiones/components/AtrasadosTable'
import { RankingTable } from '@/features/comisiones/components/RankingTable'
import { NotasFinalesTable } from '@/features/comisiones/components/NotasFinalesTable'
import { ReportesRapidos } from '@/features/comisiones/components/ReportesRapidos'
import { Spinner } from '@/shared/components/Spinner'

type Tab = 'calificaciones' | 'importar' | 'umbral' | 'atrasados' | 'ranking' | 'notas' | 'reportes'

const tabs: { key: Tab; label: string }[] = [
  { key: 'calificaciones', label: 'Calificaciones' },
  { key: 'importar', label: 'Importar' },
  { key: 'umbral', label: 'Configuración' },
  { key: 'atrasados', label: 'Atrasados' },
  { key: 'ranking', label: 'Ranking' },
  { key: 'notas', label: 'Notas Finales' },
  { key: 'reportes', label: 'Reportes' },
]

const ROLE_LABELS: Record<string, string> = {
  PROFESOR: 'Profesor',
  TUTOR: 'Tutor',
  COORDINADOR: 'Coordinador',
  NEXO: 'Nexo',
}

function formatDate(value: string | null) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString()
}

function shortId(value: string | null) {
  return value ? `${value.slice(0, 8)}...` : '-'
}

export default function ComisionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const asignacionId = id ?? ''
  const [activeTab, setActiveTab] = useState<Tab>('calificaciones')
  const { hasPermission } = useSession()
  const canImport = hasPermission('calificaciones:importar')
  const visibleTabs = tabs.filter((tab) => tab.key !== 'importar' || canImport)

  const { data: asignacion, isLoading: loadingAsignacion } = useMiComision(asignacionId)
  const materiaId = asignacion?.materia_id ?? ''
  const cohorteId = asignacion?.cohorte_id ?? ''
  const carreraId = asignacion?.carrera_id ?? ''

  const { data: calificaciones, isLoading: loadingCalif } = useCalificaciones(materiaId)
  const actividades = useMemo(
    () => Array.from(new Set((calificaciones?.items ?? []).map((item) => item.actividad))),
    [calificaciones?.items],
  )
  const { data: atrasados, isLoading: loadingAtrasados } = useAtrasados(materiaId)
  const { data: ranking, isLoading: loadingRanking } = useRanking(materiaId)
  const { data: notasFinales, isLoading: loadingNotas } = useNotasFinales(materiaId, actividades)

  useEffect(() => {
    if (activeTab === 'importar' && !canImport) {
      setActiveTab('calificaciones')
    }
  }, [activeTab, canImport])

  if (loadingAsignacion) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!asignacion) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Comisión no encontrada</h1>
        <Link to="/docente/comisiones" className="text-primary-600 hover:text-primary-800">
          Volver a mis comisiones
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/docente/comisiones" className="text-sm text-primary-600 hover:text-primary-500">
          &larr; Volver a comisiones
        </Link>
        <div className="mt-2">
          <h1 className="text-2xl font-bold text-gray-900">
            {asignacion.materia_nombre ?? `Materia ${shortId(materiaId)}`}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {asignacion.carrera_nombre ?? `Carrera ${shortId(carreraId)}`} · {asignacion.cohorte_nombre ?? `Cohorte ${shortId(cohorteId)}`} · {ROLE_LABELS[asignacion.rol] ?? asignacion.rol}
          </p>
        </div>
      </div>

      <Card className="p-4">
        <div className="grid gap-4 text-sm md:grid-cols-4">
          <div>
            <span className="text-gray-500">Comisiones:</span>
            <span className="ml-2 text-gray-900">
              {asignacion.comisiones?.length ? asignacion.comisiones.join(', ') : 'Sin comisiones cargadas'}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Vigencia:</span>
            <span className="ml-2 text-gray-900">{formatDate(asignacion.desde)} - {formatDate(asignacion.hasta)}</span>
          </div>
          <div>
            <span className="text-gray-500">Estado:</span>
            <span className={`ml-2 inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
              asignacion.estado_vigencia === 'vigente'
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-600'
            }`}>
              {asignacion.estado_vigencia === 'vigente' ? 'Vigente' : 'Vencida'}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Asignación:</span>
            <span className="ml-2 text-gray-900">{asignacion.id.slice(0, 8)}...</span>
          </div>
        </div>
      </Card>

      <div className="flex gap-1 overflow-x-auto border-b border-gray-200">
        {visibleTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`whitespace-nowrap px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <Card className="p-6">
        {activeTab === 'calificaciones' && (
          <div>
            <h2 className="mb-4 text-lg font-semibold">Calificaciones</h2>
            {loadingCalif ? (
              <Spinner />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-gray-600">
                      <th className="pb-2">Actividad</th>
                      <th className="pb-2">Nota numérica</th>
                      <th className="pb-2">Nota textual</th>
                      <th className="pb-2">Estado</th>
                      <th className="pb-2">Origen</th>
                    </tr>
                  </thead>
                  <tbody>
                    {calificaciones?.items.map((c) => (
                      <tr key={c.id} className="border-b last:border-0">
                        <td className="py-2">{c.actividad}</td>
                        <td className="py-2">{c.nota_numerica ?? '-'}</td>
                        <td className="py-2">{c.nota_textual ?? '-'}</td>
                        <td className="py-2">{c.aprobado ? 'Aprobado' : 'No aprobado'}</td>
                        <td className="py-2">{c.origen}</td>
                      </tr>
                    ))}
                    {(!calificaciones || calificaciones.items.length === 0) && (
                      <tr>
                        <td colSpan={5} className="py-8 text-center text-gray-500">
                          No hay calificaciones importadas.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
        {activeTab === 'importar' && canImport && <ImportPreview materiaId={materiaId} cohorteId={cohorteId} />}
        {activeTab === 'umbral' && <UmbralForm materiaId={materiaId} asignacionId={asignacionId} />}
        {activeTab === 'atrasados' && (
          loadingAtrasados ? <Spinner /> : <AtrasadosTable data={atrasados} />
        )}
        {activeTab === 'ranking' && (
          loadingRanking ? <Spinner /> : <RankingTable data={ranking} />
        )}
        {activeTab === 'notas' && (
          loadingNotas ? <Spinner /> : <NotasFinalesTable data={notasFinales} hasActivities={actividades.length > 0} />
        )}
        {activeTab === 'reportes' && <ReportesRapidos materiaId={materiaId} />}
      </Card>
    </div>
  )
}
