import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { useLogin } from '@/features/auth/hooks/useLogin'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { Card } from '@/shared/components/Card'
import { Alert } from '@/shared/components/Alert'

const loginSchema = z.object({
  tenant_code: z.string().min(1, 'El código de tenant es requerido'),
  email: z.string().min(1, 'El email es requerido').email('Email inválido'),
  password: z.string().min(1, 'La contraseña es requerida'),
})

type LoginFormValues = z.infer<typeof loginSchema>

export default function LoginPage() {
  const { login, isLoading, error } = useLogin()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data: LoginFormValues) => {
    login(data)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md p-8">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Trace</h1>
          <p className="mt-2 text-sm text-gray-600">Iniciar sesión</p>
        </div>

        {error?.status === 401 && (
          <Alert variant="error" className="mb-4">
            Credenciales inválidas. Verifique su email y contraseña.
          </Alert>
        )}

        {error?.status === 429 && (
          <Alert variant="error" className="mb-4">
            Demasiados intentos. Espere unos minutos e intente nuevamente.
          </Alert>
        )}

        {error && error.status !== 401 && error.status !== 429 && (
          <Alert variant="error" className="mb-4">
            {error.message}
          </Alert>
        )}

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

          <Input
            label="Contraseña"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register('password')}
          />

          <Button type="submit" loading={isLoading} className="w-full">
            Iniciar sesión
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-600">
          ¿Olvidó su contraseña?{' '}
          <Link to="/auth/recuperar" className="font-medium text-primary-600 hover:text-primary-500">
            Recuperar acceso
          </Link>
        </p>
      </Card>
    </div>
  )
}
