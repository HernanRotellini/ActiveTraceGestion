import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md p-8 text-center">
        <h1 className="text-6xl font-bold text-gray-300">404</h1>
        <h2 className="mt-4 text-xl font-semibold text-gray-900">Página no encontrada</h2>
        <p className="mt-2 text-sm text-gray-600">
          La página que busca no existe o ha sido movida.
        </p>
        <div className="mt-6 space-y-2">
          <Link
            to="/"
            className="block rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            Volver al inicio
          </Link>
        </div>
      </Card>
    </div>
  )
}
