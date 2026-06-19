import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/coloquios/services/api'
import type { EvaluacionCreate, ResultadoCreate, ColoquiosFilters } from '@/features/coloquios/types'

export function useMetricasColoquios() {
  return useQuery({
    queryKey: ['coloquios-metricas'],
    queryFn: () => api.panelMetricas(),
    staleTime: 60_000,
  })
}

export function useColoquiosList(filters?: ColoquiosFilters) {
  return useQuery({
    queryKey: ['coloquios', filters],
    queryFn: () => api.listarConvocatorias(filters),
    staleTime: 30_000,
  })
}

export function useColoquio(id: string) {
  return useQuery({
    queryKey: ['coloquio', id],
    queryFn: () => api.obtenerConvocatoria(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useReservas(evaluacionId: string) {
  return useQuery({
    queryKey: ['coloquio-reservas', evaluacionId],
    queryFn: () => api.listarReservas(evaluacionId),
    enabled: !!evaluacionId,
    staleTime: 30_000,
  })
}

export function useResultados(evaluacionId: string) {
  return useQuery({
    queryKey: ['coloquio-resultados', evaluacionId],
    queryFn: () => api.listarResultados(evaluacionId),
    enabled: !!evaluacionId,
    staleTime: 30_000,
  })
}

export function useCrearConvocatoria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: EvaluacionCreate) => api.crearConvocatoria(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['coloquios'] })
      qc.invalidateQueries({ queryKey: ['coloquios-metricas'] })
    },
  })
}

export function useCerrarConvocatoria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.cerrarConvocatoria(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['coloquios'] })
      qc.invalidateQueries({ queryKey: ['coloquios-metricas'] })
    },
  })
}

export function useImportarAlumnos(evaluacionId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (alumno_ids: string[]) => api.importarAlumnos(evaluacionId, alumno_ids),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['coloquio', evaluacionId] }),
  })
}

export function useRegistrarResultado(evaluacionId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ResultadoCreate) => api.registrarResultado(evaluacionId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['coloquio-resultados', evaluacionId] })
      qc.invalidateQueries({ queryKey: ['coloquios-metricas'] })
    },
  })
}
