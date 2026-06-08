import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { LiquidacionTable } from '@/features/liquidaciones/components/LiquidacionTable'
import { LiquidacionKPIs } from '@/features/liquidaciones/components/LiquidacionKPIs'
import { SalarioBaseForm } from '@/features/liquidaciones/components/SalarioBaseForm'
import { PlusForm } from '@/features/liquidaciones/components/PlusForm'
import { FacturaTable } from '@/features/liquidaciones/components/FacturaTable'
import type { LiquidacionItem, Factura } from '@/features/liquidaciones/types'

describe('LiquidacionTable', () => {
  const items: LiquidacionItem[] = [
    {
      id: '1', liquidacion_id: 'l-1', docente_id: 'd-1', docente_nombre: 'Juan Perez',
      materia: 'Matemática', comision: 'COM-001', rol: 'PROFESOR', horas: 40, valor_hora: 500, subtotal: 20000, segmento: 'general',
    },
    {
      id: '2', liquidacion_id: 'l-1', docente_id: 'd-2', docente_nombre: 'Maria Gomez',
      materia: 'Lengua', comision: 'COM-002', rol: 'TUTOR', horas: 20, valor_hora: 300, subtotal: 6000, segmento: 'nexo',
    },
  ]

  it('renders segment title and subtotal', () => {
    render(<LiquidacionTable items={items} segmento="general" titulo="General" subtotal={20000} />)
    expect(screen.getByText('General')).toBeInTheDocument()
    expect(screen.getByText('Subtotal General')).toBeInTheDocument()
  })

  it('renders docentes in segment', () => {
    render(<LiquidacionTable items={items} segmento="general" titulo="General" subtotal={20000} />)
    expect(screen.getByText('Juan Perez')).toBeInTheDocument()
    expect(screen.queryByText('Maria Gomez')).not.toBeInTheDocument()
  })

  it('returns null when no items match segment', () => {
    const { container } = render(<LiquidacionTable items={items} segmento="factura" titulo="Factura" subtotal={0} />)
    expect(container.firstChild).toBeNull()
  })
})

describe('LiquidacionKPIs', () => {
  it('renders all KPI cards', () => {
    render(<LiquidacionKPIs totalGeneral={50000} totalNexo={15000} totalFactura={3000} estado="abierta" />)
    expect(screen.getByText('Total General')).toBeInTheDocument()
    expect(screen.getByText('Total NEXO')).toBeInTheDocument()
    expect(screen.getByText('Total Factura')).toBeInTheDocument()
    expect(screen.getByText('Abierta')).toBeInTheDocument()
  })

  it('shows cerrada state', () => {
    render(<LiquidacionKPIs totalGeneral={0} totalNexo={0} totalFactura={0} estado="cerrada" />)
    expect(screen.getByText('Cerrada')).toBeInTheDocument()
  })
})

describe('SalarioBaseForm', () => {
  it('renders form fields', () => {
    render(<SalarioBaseForm onSave={async () => {}} onCancel={() => {}} />)
    expect(screen.getByText('Rol *')).toBeInTheDocument()
    expect(screen.getByText('Importe *')).toBeInTheDocument()
    expect(screen.getByText('Vigencia desde *')).toBeInTheDocument()
    expect(screen.getByText('Crear')).toBeInTheDocument()
  })

  it('renders edit mode with values', () => {
    render(
      <SalarioBaseForm
        salario={{ id: '1', rol: 'PROFESOR', importe: 50000, vigencia_desde: '2026-01-01', vigencia_hasta: '', activo: true }}
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
    expect(screen.getByText('Clave *')).toBeInTheDocument()
    expect(screen.getByText('Descripción *')).toBeInTheDocument()
  })
})

describe('FacturaTable', () => {
  const facturas: Factura[] = [
    {
      id: 'f-1', docente_id: 'd-1', docente_nombre: 'Juan Perez', periodo: '2026-06',
      importe: 25000, estado: 'pendiente', creada_en: '2026-06-01T00:00:00Z',
    },
    {
      id: 'f-2', docente_id: 'd-2', docente_nombre: 'Maria Gomez', periodo: '2026-06',
      importe: 18000, estado: 'abonada', creada_en: '2026-06-01T00:00:00Z', abonada_en: '2026-06-05T00:00:00Z',
    },
  ]

  it('renders all facturas', () => {
    render(<FacturaTable facturas={facturas} onCambiarEstado={() => {}} />)
    expect(screen.getByText('Juan Perez')).toBeInTheDocument()
    expect(screen.getByText('Maria Gomez')).toBeInTheDocument()
  })

  it('shows boton marcar abonada for pending', () => {
    render(<FacturaTable facturas={facturas} onCambiarEstado={() => {}} />)
    expect(screen.getByText('Marcar abonada')).toBeInTheDocument()
  })

  it('renders empty state', () => {
    render(<FacturaTable facturas={[]} onCambiarEstado={() => {}} />)
    expect(screen.getByText('No hay facturas registradas.')).toBeInTheDocument()
  })
})
