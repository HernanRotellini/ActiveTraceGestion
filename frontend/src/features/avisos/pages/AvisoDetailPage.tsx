import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { useAviso, usePublicarAviso, useArchivarAviso } from '@/features/avisos/hooks/useAvisos'
import { AckProgressBar } from '@/features/avisos/components/AckProgressBar'

export default function AvisoDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: aviso, isLoading } = useAviso(id!)
  const publicar = usePublicarAviso()
  const archivar = useArchivarAviso()

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!aviso) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Aviso no encontrado</h1>
        <Link to="/coordinacion/avisos" className="text-primary-600 hover:text-primary-800">Volver</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link to="/coordinacion/avisos" className="text-sm text-primary-600 hover:text-primary-800">
            &larr; Volver
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">{aviso.titulo}</h1>
        </div>
        <div className="flex items-center gap-3">
          <Link to={`/coordinacion/avisos/${id}/editar`}>
            <Button variant="secondary">Editar</Button>
          </Link>
          {aviso.estado === 'borrador' && (
            <Button onClick={() => publicar.mutate(aviso.id)} loading={publicar.isPending}>
              Publicar
            </Button>
          )}
          {aviso.estado === 'publicado' && (
            <Button variant="secondary" onClick={() => archivar.mutate(aviso.id)} loading={archivar.isPending}>
              Archivar
            </Button>
          )}
        </div>
      </div>

      <Card className="p-6">
        <div className="mb-4 flex items-center gap-3">
          <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
            aviso.estado === 'publicado' ? 'bg-green-100 text-green-700'
            : aviso.estado === 'borrador' ? 'bg-yellow-100 text-yellow-700'
            : 'bg-gray-100 text-gray-600'
          }`}>{aviso.estado}</span>
          <span className="text-sm text-gray-500">Alcance: {aviso.scope}{aviso.scope_valor ? ` (${aviso.scope_valor})` : ''}</span>
          <span className="text-sm text-gray-500">Autor: {aviso.autor_nombre}</span>
          {aviso.publicado_en && <span className="text-sm text-gray-500">Publicado: {new Date(aviso.publicado_en).toLocaleDateString()}</span>}
        </div>

        <div className="whitespace-pre-wrap text-gray-800">{aviso.contenido}</div>
      </Card>

      {aviso.estado === 'publicado' && (
        <>
          <h2 className="text-lg font-semibold text-gray-900">Seguimiento de lectura</h2>
          <Card className="p-4">
            <AckProgressBar acks={aviso.acks ?? []} />

            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
                  <tr>
                    <th className="px-4 py-3">Usuario</th>
                    <th className="px-4 py-3">Estado</th>
                    <th className="px-4 py-3">Leído</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {(aviso.acks ?? []).map((ack) => (
                    <tr key={ack.usuario_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-900">{ack.usuario_nombre}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                          ack.leido ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                        }`}>{ack.leido ? 'Leído' : 'Pendiente'}</span>
                      </td>
                      <td className="px-4 py-3 text-gray-500">{ack.leido_en ? new Date(ack.leido_en).toLocaleString() : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}

      {aviso.estado === 'publicado' && publicar.isError && (
        <Alert variant="error">Error al publicar el aviso.</Alert>
      )}
    </div>
  )
}
