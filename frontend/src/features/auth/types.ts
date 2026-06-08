export interface LoginRequest {
  tenant_code: string
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Challenge2faRequest {
  challenge_id: string
  code: string
}

export interface Challenge2faResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RecoveryRequest {
  tenant_code: string
  email: string
}

export interface RecoveryResponse {
  message: string
}

export interface ResetRequest {
  token: string
  new_password: string
}

export interface MeResponse {
  user_id: string
  tenant_id: string
  roles: string[]
}
