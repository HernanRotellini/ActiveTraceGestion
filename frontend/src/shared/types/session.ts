export interface SessionUser {
  user_id: string
  tenant_id: string
  roles: string[]
  permissions?: string[]
  email?: string | null
}

export interface Session {
  access_token: string
  refresh_token: string
  user: SessionUser
}

export interface LoginPayload {
  tenant_code: string
  email: string
  password: string
}

export interface ChallengePayload {
  challenge_id: string
  code: string
}

export interface RecoveryPayload {
  tenant_code: string
  email: string
}

export interface ResetPayload {
  token: string
  password: string
}
