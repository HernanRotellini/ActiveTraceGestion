import { Card } from '@/shared/components/Card'

interface LiquidacionKPIsProps {
  totalGeneral: number
  totalNexo: number
  totalFactura: number
  estado: string
}

export function LiquidacionKPIs({ totalGeneral, totalNexo, totalFactura, estado }: LiquidacionKPIsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card className="p-4">
        <p className="text-xs font-medium text-gray-500">Total General</p>
        <p className="mt-1 text-2xl font-bold text-gray-900">${totalGeneral.toLocaleString()}</p>
      </Card>
      <Card className="p-4">
        <p className="text-xs font-medium text-gray-500">Total NEXO</p>
        <p className="mt-1 text-2xl font-bold text-primary-600">${totalNexo.toLocaleString()}</p>
      </Card>
      <Card className="p-4">
        <p className="text-xs font-medium text-gray-500">Total Factura</p>
        <p className="mt-1 text-2xl font-bold text-amber-600">${totalFactura.toLocaleString()}</p>
      </Card>
      <Card className="p-4">
        <p className="text-xs font-medium text-gray-500">Estado</p>
        <span
          className={`mt-1 inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
            estado === 'cerrada' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
          }`}
        >
          {estado === 'cerrada' ? 'Cerrada' : 'Abierta'}
        </span>
      </Card>
    </div>
  )
}
