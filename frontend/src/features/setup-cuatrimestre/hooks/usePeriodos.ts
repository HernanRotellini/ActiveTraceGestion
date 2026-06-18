import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/setup-cuatrimestre/services/api'
import type {
  FechaAcademicaOficialPayload,
  FechaAcademicaOficialUpdatePayload,
  FechaPayload,
  PeriodoPayload,
  ProgramaOficialPayload,
  ProgramaOficialUpdatePayload,
  ProgramaPayload,
} from '@/features/setup-cuatrimestre/types'

export function usePeriodosList() {
  return useQuery({
    queryKey: ['periodos-academicos'],
    queryFn: () => api.listarPeriodos(),
    staleTime: 30_000,
  })
}

export function usePeriodo(id: string) {
  return useQuery({
    queryKey: ['periodo', id],
    queryFn: () => api.obtenerPeriodo(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useCrearPeriodo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: PeriodoPayload) => api.crearPeriodo(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['periodos-academicos'] }),
  })
}

export function useActualizarPeriodoMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & Partial<PeriodoPayload>) =>
      api.actualizarPeriodo(id, payload),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', variables.id] })
    },
  })
}

export function useActivarPeriodo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.activarPeriodo(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['periodos-academicos'] }),
  })
}

export function useDesactivarPeriodo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.desactivarPeriodo(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['periodos-academicos'] }),
  })
}

export function useEliminarPeriodo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarPeriodo(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['periodos-academicos'] }),
  })
}

export function useAgregarFechaMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ periodoId, ...payload }: { periodoId: string } & FechaPayload) =>
      api.agregarFecha(periodoId, payload),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', variables.periodoId] })
    },
  })
}

export function useQuitarFechaMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ periodoId, fechaId }: { periodoId: string; fechaId: string }) =>
      api.quitarFecha(periodoId, fechaId),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', variables.periodoId] })
    },
  })
}

export function useAgregarProgramaMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ periodoId, ...payload }: { periodoId: string } & ProgramaPayload) =>
      api.agregarPrograma(periodoId, payload),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', variables.periodoId] })
    },
  })
}

export function useQuitarProgramaMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ periodoId, programaId }: { periodoId: string; programaId: string }) =>
      api.quitarPrograma(periodoId, programaId),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', variables.periodoId] })
    },
  })
}

export function useProgramasList(filters?: api.ProgramasFilters) {
  return useQuery({
    queryKey: ['setup-programas', filters],
    queryFn: () => api.listarProgramas(filters),
    staleTime: 30_000,
  })
}

export function useCrearProgramaOficial() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ProgramaOficialPayload) => api.crearPrograma(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['setup-programas'] }),
  })
}

export function useActualizarProgramaOficial() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & ProgramaOficialUpdatePayload) =>
      api.actualizarPrograma(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['setup-programas'] }),
  })
}

export function useEliminarProgramaOficial() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarPrograma(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['setup-programas'] }),
  })
}

export function useFechasList(filters?: api.FechasFilters) {
  return useQuery({
    queryKey: ['setup-fechas', filters],
    queryFn: () => api.listarFechas(filters),
    staleTime: 30_000,
  })
}

export function useCrearFechaOficial() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: FechaAcademicaOficialPayload) => api.crearFecha(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['setup-fechas'] }),
  })
}

export function useActualizarFechaOficial() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & FechaAcademicaOficialUpdatePayload) =>
      api.actualizarFecha(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['setup-fechas'] }),
  })
}

export function useEliminarFechaOficial() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarFecha(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['setup-fechas'] }),
  })
}
