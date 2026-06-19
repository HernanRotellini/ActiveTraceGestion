import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { Combobox } from '@/shared/components/Combobox'
import { fetchMaterias } from '@/features/comunicaciones/services/comunicaciones'
import { VARIABLES_SOPORTADAS } from '@/features/comunicaciones/types/comunicaciones'
import type { MateriaOption } from '@/features/comunicaciones/types/comunicaciones'

const envioSchema = z.object({
  materiaId: z.string().min(1, 'La materia es requerida'),
  asunto: z.string().min(1, 'El asunto es requerido'),
  cuerpo: z.string().min(1, 'El cuerpo es requerido'),
})

export type EnvioFormValues = z.infer<typeof envioSchema>

interface EnvioFormProps {
  onPreview: (values: EnvioFormValues) => void
  onSend: (values: EnvioFormValues) => void
  isLoadingPreview: boolean
  isLoadingSend: boolean
  canSend: boolean
}

export function EnvioForm({ onPreview, onSend, isLoadingPreview, isLoadingSend, canSend }: EnvioFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<EnvioFormValues>({
    resolver: zodResolver(envioSchema),
  })

  const materiaId = watch('materiaId')

  const { data: materias = [], isLoading: loadingMaterias } = useQuery({
    queryKey: ['materias-comunicaciones'],
    queryFn: fetchMaterias,
    staleTime: 60_000,
  })

  const materiaItems = materias.map((m: MateriaOption) => ({
    value: m.id,
    label: `${m.codigo ? `[${m.codigo}] ` : ''}${m.nombre}`,
  }))

  return (
    <form className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Nueva comunicación</h2>
        <p className="text-sm text-gray-600">
          El mensaje se encola para los <span className="font-medium">alumnos atrasados</span> de la materia seleccionada.
        </p>
      </div>

      <Combobox
        label="Materia"
        items={materiaItems}
        value={materiaId ?? ''}
        onChange={(val) => setValue('materiaId', val, { shouldValidate: true })}
        placeholder="Buscar materia..."
        error={errors.materiaId?.message}
        isLoading={loadingMaterias}
      />

      <Input
        label="Asunto"
        placeholder="Asunto del mensaje"
        error={errors.asunto?.message}
        {...register('asunto')}
      />

      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">Cuerpo</label>
        <textarea
          rows={5}
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Contenido del mensaje"
          {...register('cuerpo')}
        />
        {errors.cuerpo && (
          <p className="text-sm text-red-600" role="alert">{errors.cuerpo.message}</p>
        )}
        <p className="text-xs text-gray-500">
          Variables disponibles:{' '}
          {VARIABLES_SOPORTADAS.map((v) => (
            <code key={v} className="mr-1 rounded bg-gray-100 px-1 py-0.5 text-gray-700">{`{{${v}}}`}</code>
          ))}
        </p>
      </div>

      <div className="space-y-2">
        <div className="flex gap-3">
          <Button type="button" variant="secondary" onClick={handleSubmit(onPreview)} loading={isLoadingPreview}>
            Previsualizar
          </Button>
          <Button type="button" onClick={handleSubmit(onSend)} loading={isLoadingSend} disabled={!canSend}>
            Encolar envío
          </Button>
        </div>
        {!canSend && (
          <p className="text-xs text-gray-500">Previsualizá el mensaje antes de encolar el envío (RN-16).</p>
        )}
      </div>
    </form>
  )
}
