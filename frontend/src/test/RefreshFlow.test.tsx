import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { writeSession } from '@/shared/services/session'
import api from '@/shared/services/api'

const server = setupServer()

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => {
  server.resetHandlers()
  sessionStorage.clear()
})

describe('Transparent refresh flow', () => {
  it('retries original request after successful token refresh', async () => {
    writeSession({
      access_token: 'expired-token',
      refresh_token: 'valid-refresh-token',
      user: {
        user_id: 'user-1',
        tenant_id: 'tenant-1',
        roles: ['admin'],
      },
    })

    let refreshCalled = false

    server.use(
      http.get('/api/auth/me', () => {
        if (!refreshCalled) {
          return HttpResponse.json(
            { detail: 'Token expired' },
            { status: 401 },
          )
        }
        return HttpResponse.json({
          user_id: 'user-1',
          tenant_id: 'tenant-1',
          roles: ['admin'],
        })
      }),
      http.post('/api/auth/refresh', () => {
        refreshCalled = true
        return HttpResponse.json({
          access_token: 'new-access-token',
          refresh_token: 'new-refresh-token',
          token_type: 'bearer',
        })
      }),
    )

    const response = await api.get('/auth/me')

    expect(response.status).toBe(200)
    expect(refreshCalled).toBe(true)

    const session = JSON.parse(sessionStorage.getItem('trace_session')!)
    expect(session.access_token).toBe('new-access-token')
    expect(session.refresh_token).toBe('new-refresh-token')
  })
})
