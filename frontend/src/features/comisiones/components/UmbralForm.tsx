import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useUmbral } from '@/features/comisiones/hooks/useUmbral'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { Spinner } from '@/shared/components/Spinner'

const umbralSchema = z.object({
  nota_minima: z.coerce.number().min(0).max(100),
  nota_maxima: z.coerce.number().min(0).max(100),
  umbral_atraso: z.coerce.number().min(0).max(365),
  umbral_promocion: z.coerce.number().min(0).max(100),
})

type UmbralFormValues = z.infer<typeof umbralSchema>

interface UmbralFormProps {
  comisionId: string
}

export function UmbralForm({ comisionId }: UmbralFormProps) {
  const { query, mutation } = useUmbral(comisionId)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UmbralFormValues>({
    resolver: zodResolver(umbralSchema),
  })

  useEffect(() => {
    if (query.data) {
      reset({
        nota_minima: query.data.nota_minima,
        nota_maxima: query.data.nota_maxima,
        umbral_atraso: query.data.umbral_atraso,
        umbral_promocion: query.data.umbral_promocion,
      })
    }
  }, [query.data, reset])

  const onSubmit = (data: UmbralFormValues) => {
    mutation.mutate(data)
  }

  if (query.isLoading) return <Spinner />

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Configuración de Umbrales</h2>
      <p className="text-sm text-gray-600">
        Defina los valores mínimos y máximos para las calificaciones y umbrales de atraso.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="max-w-md space-y-4">
        <Input
          label="Nota mínima"
          type="number"
          error={errors.nota_minima?.message}
          {...register('nota_minima')}
        />
        <Input
          label="Nota máxima"
          type="number"
          error={errors.nota_maxima?.message}
          {...register('nota_maxima')}
        />
        <Input
          label="Umbral de atraso (días)"
          type="number"
          error={errors.umbral_atraso?.message}
          {...register('umbral_atraso')}
        />
        <Input
          label="Umbral de promoción"
          type="number"
          error={errors.umbral_promocion?.message}
          {...register('umbral_promocion')}
        />

        <Button type="submit" loading={mutation.isPending}>
          Guardar configuración
        </Button>
      </form>
    </div>
  )
}
