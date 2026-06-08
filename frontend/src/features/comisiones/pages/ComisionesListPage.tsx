import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'

interface ComisionResumen {
  id: string
  nombre: string
  materia: string
  cantidad_alumnos: number
}

const comisionesMock: ComisionResumen[] = []

export default function ComisionesListPage() {
  if (comisionesMock.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Mis Comisiones</h1>
        <Card className="p-12 text-center">
          <p className="text-gray-500">No hay comisiones asignadas.</p>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Mis Comisiones</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {comisionesMock.map((c) => (
          <Link key={c.id} to={`/docente/comisiones/${c.id}`}>
            <Card className="p-4 transition-shadow hover:shadow-md">
              <h3 className="font-semibold text-gray-900">{c.nombre}</h3>
              <p className="text-sm text-gray-500">{c.materia}</p>
              <p className="mt-2 text-sm text-gray-600">{c.cantidad_alumnos} alumnos</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
