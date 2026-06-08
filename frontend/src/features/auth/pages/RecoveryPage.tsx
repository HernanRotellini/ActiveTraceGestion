import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { useRecovery } from '@/features/auth/hooks/useRecovery'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { Card } from '@/shared/components/Card'
import { Alert } from '@/shared/components/Alert'

const recoverySchema = z.object({
  tenant_code: z.string().min(1, 'El código de tenant es requerido'),
  email: z.string().min(1, 'El email es requerido').email('Email inválido'),
})

type RecoveryFormValues = z.infer<typeof recoverySchema>

export default function RecoveryPage() {
  const { submit, isLoading, isSuccess, error } = useRecovery()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RecoveryFormValues>({
    resolver: zodResolver(recoverySchema),
  })

  const onSubmit = (data: RecoveryFormValues) => {
    submit(data)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md p-8">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Recuperar contraseña</h1>
          <p className="mt-2 text-sm text-gray-600">
            Ingrese su email y le enviaremos instrucciones para restablecer su contraseña.
          </p>
        </div>

        {isSuccess && (
          <Alert variant="success" className="mb-4">
            Si la dirección de email existe en el sistema, recibirá instrucciones para restablecer su contraseña.
          </Alert>
        )}

        {error && (
          <Alert variant="error" className="mb-4">
            {error.message}
          </Alert>
        )}

        {!isSuccess && (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Código de institución"
              placeholder="ej: universidad-a"
              error={errors.tenant_code?.message}
              {...register('tenant_code')}
            />

            <Input
              label="Email"
              type="email"
              placeholder="email@institucion.edu"
              error={errors.email?.message}
              {...register('email')}
            />

            <Button type="submit" loading={isLoading} className="w-full">
              Enviar instrucciones
            </Button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-gray-600">
          <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
            Volver al inicio de sesión
          </Link>
        </p>
      </Card>
    </div>
  )
}
