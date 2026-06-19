import { beforeEach, describe, expect, it, vi } from 'vitest'
import { crearUsuario, listarUsuarios, actualizarUsuario } from '@/features/admin/services/api'

const { apiMock } = vi.hoisted(() => ({
  apiMock: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

vi.mock('@/shared/services/api', () => ({
  default: apiMock,
}))

describe('admin services', () => {
  beforeEach(() => {
    apiMock.get.mockReset()
    apiMock.post.mockReset()
    apiMock.patch.mockReset()
  })

  it('uses the admin usuarios route without duplicating the api prefix when listing users', async () => {
    apiMock.get.mockResolvedValue({ data: [] })

    await listarUsuarios({ q: 'ana' })

    expect(apiMock.get).toHaveBeenCalledWith('/admin/usuarios', {
      params: { q: 'ana' },
    })
  })

  it('uses the admin usuarios route without duplicating the api prefix when creating a user', async () => {
    const payload = {
      nombre: 'Ana',
      apellidos: 'Perez',
      email: 'ana@test.com',
    }
    apiMock.post.mockResolvedValue({ data: { id: 'docente-1', ...payload } })

    await crearUsuario(payload)

    expect(apiMock.post).toHaveBeenCalledWith('/admin/usuarios', payload)
  })

  it('uses the admin usuarios route without duplicating the api prefix when updating a user', async () => {
    const payload = {
      nombre: 'Ana',
    }
    apiMock.patch.mockResolvedValue({ data: { id: 'docente-1', ...payload } })

    await actualizarUsuario('docente-1', payload)

    expect(apiMock.patch).toHaveBeenCalledWith('/admin/usuarios/docente-1', payload)
  })
})
