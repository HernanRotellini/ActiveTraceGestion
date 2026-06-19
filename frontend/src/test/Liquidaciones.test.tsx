import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { LiquidacionTable } from '@/features/liquidaciones/components/LiquidacionTable'
import { LiquidacionKPIs } from '@/features/liquidaciones/components/LiquidacionKPIs'
import { SalarioBaseForm } from '@/features/liquidaciones/components/SalarioBaseForm'
import { PlusForm } from '@/features/liquidaciones/components/PlusForm'
import { FacturaTable } from '@/features/liquidaciones/components/FacturaTable'
import type { LiquidacionResponse, FacturaResponse } from '@/features/liquidaciones/types'

describe('LiquidacionTable', () => {
  const items: LiquidacionResponse[] = [
    {
      id: '1', cohorte_id: 'c-1', usuario_id: 'd-1', periodo: '2026-06',
      rol: 'PROFESOR', estado: 'Cerrada', monto_base: '40000', monto_plus: '5000', monto_total: '45000',
      comisiones: ['COM-001'], es_nexo: false, excluido_por_factura: false, created_at: '2026-06-01T00:00:00Z',
    },
    {
      id: '2', cohorte_id: 'c-1', usuario_id: 'd-2', periodo: '2026-06',
      rol: 'TUTOR', estado: 'Cerrada', monto_base: '20000', monto_plus: '2000', monto_total: '22000',
      comisiones: ['COM-002'], es_nexo: true, excluido_por_factura: false, created_at: '2026-06-01T00:00:00Z',
    },
  ]

  it('renders liquidaciones table', () => {
    render(<LiquidacionTable items={items} />)
    expect(screen.getByText('2026-06')).toBeInTheDocument()
  })

  it('renders empty state', () => {
    render(<LiquidacionTable items={[]} />)
    expect(screen.getByText('No hay liquidaciones registradas.')).toBeInTheDocument()
  })
})

describe('LiquidacionKPIs', () => {
  it('renders all KPI cards', () => {
    render(<LiquidacionKPIs totalPagable="50000" segmentoNexo="15000" segmentoFacturantes="3000" totalItems={5} />)
    expect(screen.getByText('Total pagable')).toBeInTheDocument()
    expect(screen.getByText('Segmento NEXO')).toBeInTheDocument()
    expect(screen.getByText('Segmento facturantes')).toBeInTheDocument()
    expect(screen.getByText('Docentes en preview')).toBeInTheDocument()
  })
})

describe('SalarioBaseForm', () => {
  it('renders form fields', () => {
    render(<SalarioBaseForm onSave={async () => {}} onCancel={() => {}} />)
    expect(screen.getByText('Rol *')).toBeInTheDocument()
    expect(screen.getByText('Monto *')).toBeInTheDocument()
    expect(screen.getByText('Desde *')).toBeInTheDocument()
    expect(screen.getByText('Crear')).toBeInTheDocument()
  })

  it('renders edit mode with values', () => {
    render(
      <SalarioBaseForm
        salario={{ id: '1', rol: 'PROFESOR', monto: '50000', desde: '2026-01-01', hasta: null, created_at: '2026-01-01T00:00:00Z' }}
        onSave={async () => {}}
        onCancel={() => {}}
      />,
    )
    expect(screen.getByText('Actualizar')).toBeInTheDocument()
  })
})

describe('PlusForm', () => {
  it('renders plus form fields', () => {
    render(<PlusForm onSave={async () => {}} onCancel={() => {}} />)
    expect(screen.getByText('Grupo *')).toBeInTheDocument()
    expect(screen.getByText('Descripción *')).toBeInTheDocument()
  })
})

describe('FacturaTable', () => {
  const facturas: FacturaResponse[] = [
    {
      id: 'f-1', usuario_id: 'd-1', periodo: '2026-06',
      detalle: 'Honorarios junio', referencia_archivo: 'factura-001.pdf', archivo_size_bytes: 102400,
      estado: 'Pendiente', abonada_at: null, created_at: '2026-06-01T00:00:00Z',
    },
    {
      id: 'f-2', usuario_id: 'd-2', periodo: '2026-06',
      detalle: 'Honorarios junio', referencia_archivo: 'factura-002.pdf', archivo_size_bytes: 204800,
      estado: 'Abonada', abonada_at: '2026-06-05T00:00:00Z', created_at: '2026-06-01T00:00:00Z',
    },
  ]

  it('renders all facturas', () => {
    render(<FacturaTable facturas={facturas} onMarcarAbonada={() => {}} onEliminar={() => {}} />)
    expect(screen.getByText('Honorarios junio')).toBeInTheDocument()
  })

  it('shows boton abonar for pending', () => {
    render(<FacturaTable facturas={facturas} onMarcarAbonada={() => {}} onEliminar={() => {}} />)
    expect(screen.getByText('Abonar')).toBeInTheDocument()
  })

  it('renders empty state', () => {
    render(<FacturaTable facturas={[]} onMarcarAbonada={() => {}} onEliminar={() => {}} />)
    expect(screen.getByText('No hay facturas registradas.')).toBeInTheDocument()
  })
})
