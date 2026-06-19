import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  actualizarVigencia,
  clonarEquipo,
  crearAsignacionesEquipo,
  exportarEquiposCSV,
  listarAsignaciones,
} from '@/features/equipos-docentes/services/api'

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

describe('equipos docentes services', () => {
  beforeEach(() => {
    apiMock.get.mockReset()
    apiMock.post.mockReset()
    apiMock.patch.mockReset()
  })

  it('lists asignaciones without duplicating the api prefix', async () => {
    apiMock.get.mockResolvedValue({ data: [] })

    await listarAsignaciones({ docente_id: 'doc-1' })

    expect(apiMock.get).toHaveBeenCalledWith('/asignaciones', {
      params: { docente_id: 'doc-1' },
    })
  })

  it('creates asignaciones without duplicating the api prefix', async () => {
    const payload = {
      materia_id: 'mat-1',
      cohorte_id: 'coh-1',
      docente_ids: ['doc-1'],
      rol_en_materia: 'titular',
    }
    apiMock.post.mockResolvedValue({ data: [] })

    await crearAsignacionesEquipo(payload)

    expect(apiMock.post).toHaveBeenCalledWith('/equipos/asignacion-masiva', payload)
  })

  it('clones equipos without duplicating the api prefix', async () => {
    const payload = {
      source_materia_id: 'mat-1',
      target_materia_id: 'mat-2',
    }
    apiMock.post.mockResolvedValue({ data: {} })

    await clonarEquipo(payload)

    expect(apiMock.post).toHaveBeenCalledWith('/equipos/clonar', payload)
  })

  it('updates vigencia without duplicating the api prefix', async () => {
    const payload = {
      asignacion_id: 'asg-1',
      activa: true,
    }
    apiMock.patch.mockResolvedValue({ data: {} })

    await actualizarVigencia(payload)

    expect(apiMock.patch).toHaveBeenCalledWith('/equipos/vigencia', payload)
  })

  it('exports equipos without duplicating the api prefix', async () => {
    const params = {
      materia_id: 'mat-1',
      cohorte_id: 'coh-1',
    }
    apiMock.get.mockResolvedValue({ data: new Blob() })

    await exportarEquiposCSV(params)

    expect(apiMock.get).toHaveBeenCalledWith('/equipos/exportar', {
      params,
      responseType: 'blob',
    })
  })
})
