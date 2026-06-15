import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { Combobox } from '@/shared/components/Combobox'
import { fetchMaterias } from '@/features/comunicaciones/services/comunicaciones'
import type { MateriaOption } from '@/features/comunicaciones/types/comunicaciones'

const envioSchema = z.object({
  materiaId: z.string().min(1, 'La materia es requerida'),
  tipo: z.string().min(1, 'El tipo es requerido'),
  asunto: z.string().min(1, 'El asunto es requerido'),
  cuerpo: z.string().min(1, 'El cuerpo es requerido'),
  destinatarios: z.string().min(1, 'Los destinatarios son requeridos'),
})

type EnvioFormValues = z.infer<typeof envioSchema>

interface EnvioFormProps {
  onPreview: (values: EnvioFormValues) => void
  onSend: (values: EnvioFormValues) => void
  isLoadingPreview: boolean
  isLoadingSend: boolean
}

export function EnvioForm({ onPreview, onSend, isLoadingPreview, isLoadingSend }: EnvioFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<EnvioFormValues>({
    resolver: zodResolver(envioSchema),
    defaultValues: {
      tipo: 'email',
    },
  })

  const materiaId = watch('materiaId')

  const { data: materias = [], isLoading: loadingMaterias } = useQuery({
    queryKey: ['materias-comunicaciones'],
    queryFn: fetchMaterias,
    staleTime: 60_000,
  })

  const materiaItems: { value: string; label: string }[] = materias.map((m: MateriaOption) => ({
    value: m.id,
    label: `${m.codigo ? `[${m.codigo}] ` : ''}${m.nombre}`,
  }))

  return (
    <form className="space-y-4">
      <h2 className="text-lg font-semibold">Nueva Comunicación</h2>

      <Combobox
        label="Materia"
        items={materiaItems}
        value={materiaId ?? ''}
        onChange={(val) => setValue('materiaId', val, { shouldValidate: true })}
        placeholder="Buscar materia..."
        error={errors.materiaId?.message}
        isLoading={loadingMaterias}
      />

      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">Tipo</label>
        <select
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          {...register('tipo')}
        >
          <option value="email">Email</option>
          <option value="sms">SMS</option>
          <option value="whatsapp">WhatsApp</option>
        </select>
        {errors.tipo && (
          <p className="text-sm text-red-600" role="alert">{errors.tipo.message}</p>
        )}
      </div>

      <Input
        label="Asunto"
        placeholder="Asunto del mensaje"
        error={errors.asunto?.message}
        {...register('asunto')}
      />

      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">Cuerpo</label>
        <textarea
          rows={4}
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Contenido del mensaje"
          {...register('cuerpo')}
        />
        {errors.cuerpo && (
          <p className="text-sm text-red-600" role="alert">{errors.cuerpo.message}</p>
        )}
      </div>

      <Input
        label="Destinatarios (separados por coma)"
        placeholder="email1@test.com, email2@test.com"
        error={errors.destinatarios?.message}
        {...register('destinatarios')}
      />

      <div className="flex gap-3">
        <Button type="button" variant="secondary" onClick={handleSubmit(onPreview)} loading={isLoadingPreview}>
          Previsualizar
        </Button>
        <Button type="button" onClick={handleSubmit(onSend)} loading={isLoadingSend}>
          Enviar
        </Button>
      </div>
    </form>
  )
}
