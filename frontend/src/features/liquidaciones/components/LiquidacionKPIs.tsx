import { Card } from '@/shared/components/Card'

interface LiquidacionKPIsProps {
  totalPagable: string
  segmentoNexo: string
  segmentoFacturantes: string
  totalItems: number
}

export function LiquidacionKPIs({ totalPagable, segmentoNexo, segmentoFacturantes, totalItems }: LiquidacionKPIsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card className="p-4">
        <p className="text-xs font-medium text-gray-500">Total pagable</p>
        <p className="mt-1 text-2xl font-bold text-gray-900">${Number(totalPagable).toLocaleString()}</p>
      </Card>
      <Card className="p-4">
        <p className="text-xs font-medium text-gray-500">Segmento NEXO</p>
        <p className="mt-1 text-2xl font-bold text-primary-600">${Number(segmentoNexo).toLocaleString()}</p>
      </Card>
      <Card className="p-4">
        <p className="text-xs font-medium text-gray-500">Segmento facturantes</p>
        <p className="mt-1 text-2xl font-bold text-amber-600">${Number(segmentoFacturantes).toLocaleString()}</p>
      </Card>
      <Card className="p-4">
        <p className="text-xs font-medium text-gray-500">Docentes en preview</p>
        <p className="mt-1 text-2xl font-bold text-gray-900">{totalItems}</p>
      </Card>
    </div>
  )
}
