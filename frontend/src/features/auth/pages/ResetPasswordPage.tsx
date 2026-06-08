import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useSearchParams, Link } from 'react-router-dom'
import { useResetPassword } from '@/features/auth/hooks/useResetPassword'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { Card } from '@/shared/components/Card'
import { Alert } from '@/shared/components/Alert'

const resetSchema = z
  .object({
    password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
    confirm: z.string().min(1, 'Debe confirmar la contraseña'),
  })
  .refine((data) => data.password === data.confirm, {
    message: 'Las contraseñas no coinciden',
    path: ['confirm'],
  })

type ResetFormValues = z.infer<typeof resetSchema>

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const { submit, isLoading, isSuccess, error } = useResetPassword()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetFormValues>({
    resolver: zodResolver(resetSchema),
  })

  const onSubmit = (data: ResetFormValues) => {
    if (!token) return
    submit({ token, new_password: data.password })
  }

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <Card className="w-full max-w-md p-8 text-center">
          <Alert variant="error" className="mb-4">
            Token de recuperación no proporcionado.
          </Alert>
          <Link
            to="/auth/recuperar"
            className="font-medium text-primary-600 hover:text-primary-500"
          >
            Solicitar nuevo token
          </Link>
        </Card>
      </div>
    )
  }

  if (isSuccess) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <Card className="w-full max-w-md p-8 text-center">
          <Alert variant="success" className="mb-4">
            Su contraseña ha sido restablecida exitosamente.
          </Alert>
          <Link
            to="/login"
            className="font-medium text-primary-600 hover:text-primary-500"
          >
            Iniciar sesión
          </Link>
        </Card>
      </div>
    )
  }

  if (error?.status === 401) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <Card className="w-full max-w-md p-8 text-center">
          <Alert variant="error" className="mb-4">
            El token de recuperación es inválido o ha expirado.
          </Alert>
          <Link
            to="/auth/recuperar"
            className="font-medium text-primary-600 hover:text-primary-500"
          >
            Solicitar nuevo token
          </Link>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md p-8">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Restablecer contraseña</h1>
          <p className="mt-2 text-sm text-gray-600">
            Ingrese su nueva contraseña.
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-4">
            {error.message}
          </Alert>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Nueva contraseña"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register('password')}
          />

          <Input
            label="Confirmar contraseña"
            type="password"
            placeholder="••••••••"
            error={errors.confirm?.message}
            {...register('confirm')}
          />

          <Button type="submit" loading={isLoading} className="w-full">
            Restablecer contraseña
          </Button>
        </form>
      </Card>
    </div>
  )
}
