import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { useCalificaciones } from '@/features/comisiones/hooks/useCalificaciones'
import { useAtrasados } from '@/features/comisiones/hooks/useAtrasados'
import { useRanking } from '@/features/comisiones/hooks/useRanking'
import { useNotasFinales } from '@/features/comisiones/hooks/useNotasFinales'
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

export default function ComisionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [activeTab, setActiveTab] = useState<Tab>('calificaciones')

  const { data: calificaciones, isLoading: loadingCalif } = useCalificaciones(id!)
  const { data: atrasados, isLoading: loadingAtrasados } = useAtrasados(id!)
  const { data: ranking, isLoading: loadingRanking } = useRanking(id!)
  const { data: notasFinales, isLoading: loadingNotas } = useNotasFinales(id!)

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/docente/comisiones" className="text-sm text-primary-600 hover:text-primary-500">
          &larr; Volver a comisiones
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Comisión {id}</h1>
      </div>

      <div className="flex gap-1 overflow-x-auto border-b border-gray-200">
        {tabs.map((tab) => (
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
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-gray-600">
                    <th className="pb-2">Alumno</th>
                    <th className="pb-2">Materia</th>
                    <th className="pb-2">Nota</th>
                    <th className="pb-2">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {calificaciones?.map((c) => (
                    <tr key={c.id} className="border-b last:border-0">
                      <td className="py-2">{c.alumno_nombre}</td>
                      <td className="py-2">{c.materia}</td>
                      <td className="py-2">{c.nota ?? '-'}</td>
                      <td className="py-2">{c.estado}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
        {activeTab === 'importar' && <ImportPreview comisionId={id!} />}
        {activeTab === 'umbral' && <UmbralForm comisionId={id!} />}
        {activeTab === 'atrasados' && (
          loadingAtrasados ? <Spinner /> : <AtrasadosTable data={atrasados} />
        )}
        {activeTab === 'ranking' && (
          loadingRanking ? <Spinner /> : <RankingTable data={ranking} />
        )}
        {activeTab === 'notas' && (
          loadingNotas ? <Spinner /> : <NotasFinalesTable data={notasFinales} />
        )}
        {activeTab === 'reportes' && <ReportesRapidos comisionId={id!} />}
      </Card>
    </div>
  )
}
