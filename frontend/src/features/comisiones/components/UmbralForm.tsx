import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useUmbral } from '@/features/comisiones/hooks/useUmbral'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'

const umbralSchema = z.object({
  umbral_pct: z.coerce.number().min(0).max(100),
  valores_aprobatorios: z.string().min(1, 'Ingresá al menos un valor aprobatorio.'),
})

type UmbralFormValues = z.infer<typeof umbralSchema>

interface UmbralFormProps {
  materiaId: string
  asignacionId: string
}

function splitValores(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

export function UmbralForm({ materiaId, asignacionId }: UmbralFormProps) {
  const { query, mutation } = useUmbral(materiaId, asignacionId)
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UmbralFormValues>({
    resolver: zodResolver(umbralSchema),
    defaultValues: {
      umbral_pct: 60,
      valores_aprobatorios: 'Satisfactorio, Supera lo esperado',
    },
  })

  useEffect(() => {
    if (query.data) {
      reset({
        umbral_pct: query.data.umbral_pct,
        valores_aprobatorios: query.data.valores_aprobatorios?.join(', ') ?? '',
      })
    }
  }, [query.data, reset])

  const onSubmit = async (data: UmbralFormValues) => {
    try {
      await mutation.mutateAsync({
        umbral_pct: data.umbral_pct,
        valores_aprobatorios: splitValores(data.valores_aprobatorios),
      })
      setToast({ message: 'Umbral actualizado correctamente.', variant: 'success' })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'No se pudo guardar el umbral.'
      setToast({ message, variant: 'error' })
    }
  }

  if (query.isLoading) return <Spinner />

  return (
    <div className="space-y-4">
      {toast && (
        <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />
      )}

      <h2 className="text-lg font-semibold">Configuración de Umbral</h2>
      <p className="text-sm text-gray-600">
        Definí el porcentaje mínimo de aprobación y los valores textuales que cuentan como aprobatorios.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="max-w-md space-y-4">
        <Input
          label="Umbral de aprobación (%)"
          type="number"
          min={0}
          max={100}
          error={errors.umbral_pct?.message}
          {...register('umbral_pct')}
        />
        <Input
          label="Valores aprobatorios"
          type="text"
          error={errors.valores_aprobatorios?.message}
          {...register('valores_aprobatorios')}
        />

        <Button type="submit" loading={mutation.isPending}>
          Guardar configuración
        </Button>
      </form>
    </div>
  )
}
