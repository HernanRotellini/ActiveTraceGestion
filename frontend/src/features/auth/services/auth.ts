import api from '@/shared/services/api'
import type {
  LoginRequest,
  LoginResponse,
  Challenge2faRequest,
  Challenge2faResponse,
  RecoveryRequest,
  RecoveryResponse,
  ResetRequest,
  MeResponse,
} from '@/features/auth/types'

export async function login(data: LoginRequest): Promise<LoginResponse & { requires_2fa?: boolean; challenge_id?: string }> {
  const response = await api.post('/auth/login', data)
  return response.data
}

export async function challenge2fa(data: Challenge2faRequest): Promise<Challenge2faResponse> {
  const response = await api.post('/auth/2fa/challenge', data)
  return response.data
}

export async function refresh(refreshToken: string): Promise<LoginResponse> {
  const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
  return response.data
}

export async function logout(refreshToken: string): Promise<void> {
  await api.post('/auth/logout', { refresh_token: refreshToken })
}

export async function requestRecovery(data: RecoveryRequest): Promise<RecoveryResponse> {
  const response = await api.post('/auth/forgot', data)
  return response.data
}

export async function resetPassword(data: ResetRequest): Promise<void> {
  await api.post('/auth/reset', data)
}

export async function getMe(): Promise<MeResponse> {
  const response = await api.get('/auth/me')
  return response.data
}
