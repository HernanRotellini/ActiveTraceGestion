import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import { useGrillaSalarial, useCrearSalarioBase, useActualizarSalarioBase, usePlus, useCrearPlus, useActualizarPlus } from '@/features/liquidaciones/hooks/useLiquidaciones'
import { SalarioBaseForm } from '@/features/liquidaciones/components/SalarioBaseForm'
import { PlusForm } from '@/features/liquidaciones/components/PlusForm'
import type { SalarioBase, SalarioBasePayload, Plus, PlusPayload } from '@/features/liquidaciones/types'

type Tab = 'salarios' | 'plus'

export default function GrillaSalarialPage() {
  const [tab, setTab] = useState<Tab>('salarios')
  const [salarioEdit, setSalarioEdit] = useState<SalarioBase | null>(null)
  const [plusEdit, setPlusEdit] = useState<Plus | null>(null)
  const [showForm, setShowForm] = useState(false)

  const { data: salarios, isLoading: loadingSalarios } = useGrillaSalarial()
  const { data: pluses, isLoading: loadingPluses } = usePlus()
  const crearSalario = useCrearSalarioBase()
  const actualizarSalario = useActualizarSalarioBase(salarioEdit?.id ?? '')
  const crearPlus = useCrearPlus()
  const actualizarPlus = useActualizarPlus(plusEdit?.id ?? '')

  const handleSaveSalario = async (payload: SalarioBasePayload) => {
    if (salarioEdit) {
      await actualizarSalario.mutateAsync(payload)
    } else {
      await crearSalario.mutateAsync(payload)
    }
    setShowForm(false)
    setSalarioEdit(null)
  }

  const handleSavePlus = async (payload: PlusPayload) => {
    if (plusEdit) {
      await actualizarPlus.mutateAsync(payload)
    } else {
      await crearPlus.mutateAsync(payload)
    }
    setShowForm(false)
    setPlusEdit(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Grilla Salarial</h1>
        <Button onClick={() => { setShowForm(true); setSalarioEdit(null); setPlusEdit(null) }}>
          Nuevo
        </Button>
      </div>

      <div className="flex gap-1 rounded-lg bg-gray-100 p-1 w-fit">
        <button
          onClick={() => { setTab('salarios'); setShowForm(false) }}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${tab === 'salarios' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
        >
          Salarios Base
        </button>
        <button
          onClick={() => { setTab('plus'); setShowForm(false) }}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${tab === 'plus' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
        >
          Plus
        </button>
      </div>

      {showForm && tab === 'salarios' && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{salarioEdit ? 'Editar Salario Base' : 'Nuevo Salario Base'}</h3>
          <SalarioBaseForm
            salario={salarioEdit ?? undefined}
            onSave={handleSaveSalario}
            onCancel={() => { setShowForm(false); setSalarioEdit(null) }}
          />
        </Card>
      )}

      {showForm && tab === 'plus' && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{plusEdit ? 'Editar Plus' : 'Nuevo Plus'}</h3>
          <PlusForm
            plus={plusEdit ?? undefined}
            onSave={handleSavePlus}
            onCancel={() => { setShowForm(false); setPlusEdit(null) }}
          />
        </Card>
      )}

      {tab === 'salarios' && (
        loadingSalarios ? <div className="flex justify-center py-12"><Spinner /></div>
        : (
          <Card className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Rol</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Importe</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Vigencia desde</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Vigencia hasta</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-600">Activo</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {salarios?.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{s.rol}</td>
                    <td className="px-4 py-3 text-right">${s.importe.toLocaleString()}</td>
                    <td className="px-4 py-3">{s.vigencia_desde}</td>
                    <td className="px-4 py-3">{s.vigencia_hasta ?? '-'}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs ${s.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                        {s.activo ? 'Sí' : 'No'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Button variant="ghost" onClick={() => { setSalarioEdit(s); setShowForm(true) }}>
                        Editar
                      </Button>
                    </td>
                  </tr>
                ))}
                {(!salarios || salarios.length === 0) && (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-500">No hay salarios base registrados.</td></tr>
                )}
              </tbody>
            </table>
          </Card>
        )
      )}

      {tab === 'plus' && (
        loadingPluses ? <div className="flex justify-center py-12"><Spinner /></div>
        : (
          <Card className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Clave</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Rol</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Descripción</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Importe</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Vigencia</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-600">Activo</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {pluses?.map((p) => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{p.clave}</td>
                    <td className="px-4 py-3">{p.rol}</td>
                    <td className="px-4 py-3">{p.descripcion}</td>
                    <td className="px-4 py-3 text-right">${p.importe.toLocaleString()}</td>
                    <td className="px-4 py-3">{p.vigencia_desde} - {p.vigencia_hasta ?? '∞'}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs ${p.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                        {p.activo ? 'Sí' : 'No'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Button variant="ghost" onClick={() => { setPlusEdit(p); setShowForm(true) }}>
                        Editar
                      </Button>
                    </td>
                  </tr>
                ))}
                {(!pluses || pluses.length === 0) && (
                  <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-500">No hay plus registrados.</td></tr>
                )}
              </tbody>
            </table>
          </Card>
        )
      )}
    </div>
  )
}
