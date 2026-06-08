import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useChallenge2fa } from '@/features/auth/hooks/useChallenge2fa'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { Card } from '@/shared/components/Card'
import { Alert } from '@/shared/components/Alert'

export default function Challenge2faPage() {
  const navigate = useNavigate()
  const { submit, isLoading, error } = useChallenge2fa()
  const [code, setCode] = useState('')

  useEffect(() => {
    const challengeId = sessionStorage.getItem('challenge_id')
    if (!challengeId) {
      navigate('/login', { replace: true })
    }
  }, [navigate])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (code.length !== 6 || !/^\d{6}$/.test(code)) return
    submit(code)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md p-8">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Verificación en dos pasos</h1>
          <p className="mt-2 text-sm text-gray-600">
            Ingrese el código de 6 dígitos generado por su aplicación de autenticación.
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-4">
            {error.status === 401
              ? 'Código inválido o expirado. Intente nuevamente.'
              : error.message}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Código TOTP"
            placeholder="000000"
            value={code}
            onChange={(e) => {
              const val = e.target.value.replace(/\D/g, '').slice(0, 6)
              setCode(val)
            }}
            maxLength={6}
            inputMode="numeric"
            autoComplete="one-time-code"
          />

          <Button type="submit" loading={isLoading} className="w-full" disabled={code.length !== 6}>
            Verificar
          </Button>
        </form>
      </Card>
    </div>
  )
}
