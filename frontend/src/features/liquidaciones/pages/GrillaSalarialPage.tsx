import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import {
  useSalariosBase,
  useCrearSalarioBase,
  useActualizarSalarioBase,
  useEliminarSalarioBase,
  usePlus,
  useCrearPlus,
} from '@/features/liquidaciones/hooks/useLiquidaciones'
import { SalarioBaseForm } from '@/features/liquidaciones/components/SalarioBaseForm'
import { PlusForm } from '@/features/liquidaciones/components/PlusForm'
import type { SalarioBaseResponse, SalarioBaseCreate, SalarioBaseUpdate } from '@/features/liquidaciones/types'

type Tab = 'salarios' | 'plus'

export default function GrillaSalarialPage() {
  const [tab, setTab] = useState<Tab>('salarios')
  const [salarioEdit, setSalarioEdit] = useState<SalarioBaseResponse | null>(null)
  const [showForm, setShowForm] = useState(false)

  const { data: salarios, isLoading: loadingSalarios } = useSalariosBase()
  const { data: pluses, isLoading: loadingPluses } = usePlus()
  const crearSalario = useCrearSalarioBase()
  const actualizarSalario = useActualizarSalarioBase()
  const eliminarSalario = useEliminarSalarioBase()
  const crearPlus = useCrearPlus()

  const handleSaveSalario = async (payload: SalarioBaseCreate) => {
    if (salarioEdit) {
      const updatePayload: SalarioBaseUpdate = {
        rol: payload.rol,
        monto: payload.monto,
        desde: payload.desde,
        hasta: payload.hasta ?? null,
      }
      await actualizarSalario.mutateAsync({ id: salarioEdit.id, ...updatePayload })
    } else {
      await crearSalario.mutateAsync(payload)
    }
    setShowForm(false)
    setSalarioEdit(null)
  }

  const handleSavePlus = async (payload: Parameters<typeof crearPlus.mutateAsync>[0]) => {
    await crearPlus.mutateAsync(payload)
    setShowForm(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Grilla Salarial</h1>
        <Button onClick={() => { setShowForm(true); setSalarioEdit(null) }}>
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
          <h3 className="mb-4 text-lg font-semibold">Nuevo Plus</h3>
          <PlusForm
            onSave={handleSavePlus}
            onCancel={() => setShowForm(false)}
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
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Monto</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Desde</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Hasta</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {salarios?.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{s.rol}</td>
                    <td className="px-4 py-3 text-right">${Number(s.monto).toLocaleString()}</td>
                    <td className="px-4 py-3">{s.desde}</td>
                    <td className="px-4 py-3">{s.hasta ?? '-'}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => { setSalarioEdit(s); setShowForm(true) }}>
                          Editar
                        </Button>
                        <Button variant="danger" onClick={() => eliminarSalario.mutate(s.id)}>
                          Eliminar
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {(!salarios || salarios.length === 0) && (
                  <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No hay salarios base registrados.</td></tr>
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
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Rol</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Grupo</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Descripción</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Monto</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Vigencia</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {pluses?.map((p) => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{p.rol}</td>
                    <td className="px-4 py-3">{p.grupo}</td>
                    <td className="px-4 py-3">{p.descripcion}</td>
                    <td className="px-4 py-3 text-right">${Number(p.monto).toLocaleString()}</td>
                    <td className="px-4 py-3">{p.desde} — {p.hasta ?? '∞'}</td>
                  </tr>
                ))}
                {(!pluses || pluses.length === 0) && (
                  <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No hay plus registrados.</td></tr>
                )}
              </tbody>
            </table>
          </Card>
        )
      )}
    </div>
  )
}
