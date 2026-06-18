import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/setup-cuatrimestre/services/api'
import type { PeriodoPayload, FechaPayload, ProgramaPayload } from '@/features/setup-cuatrimestre/types'

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

export function useActualizarPeriodo(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Partial<PeriodoPayload>) => api.actualizarPeriodo(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['periodos-academicos'] }); qc.invalidateQueries({ queryKey: ['periodo', id] }) },
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

export function useAgregarFecha(periodoId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: FechaPayload) => api.agregarFecha(periodoId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', periodoId] })
    },
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

export function useQuitarFecha(periodoId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (fechaId: string) => api.quitarFecha(periodoId, fechaId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', periodoId] })
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

export function useAgregarPrograma(periodoId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ProgramaPayload) => api.agregarPrograma(periodoId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', periodoId] })
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

export function useQuitarPrograma(periodoId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (programaId: string) => api.quitarPrograma(periodoId, programaId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['periodos-academicos'] })
      qc.invalidateQueries({ queryKey: ['periodo', periodoId] })
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
