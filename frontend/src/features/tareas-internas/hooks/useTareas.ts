import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/tareas-internas/services/api'
import type { TareaPayload, TareaEstado, ComentarioPayload, TareasFilters } from '@/features/tareas-internas/types'

export function useTareasList(filters?: TareasFilters) {
  return useQuery({
    queryKey: ['tareas-internas', filters],
    queryFn: () => api.listarTareas(filters),
    staleTime: 30_000,
  })
}

export function useTarea(id: string) {
  return useQuery({
    queryKey: ['tarea', id],
    queryFn: () => api.obtenerTarea(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useCrearTarea() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: TareaPayload) => api.crearTarea(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tareas-internas'] }),
  })
}

export function useActualizarTarea(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Partial<TareaPayload>) => api.actualizarTarea(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['tareas-internas'] }); qc.invalidateQueries({ queryKey: ['tarea', id] }) },
  })
}

export function useCambiarEstadoTarea() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, estado }: { id: string; estado: TareaEstado }) => api.cambiarEstadoTarea(id, estado),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tareas-internas'] }),
  })
}

export function useComentarios(tareaId: string) {
  return useQuery({
    queryKey: ['comentarios', tareaId],
    queryFn: () => api.listarComentarios(tareaId),
    enabled: !!tareaId,
  })
}

export function useCrearComentario(tareaId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ComentarioPayload) => api.crearComentario(tareaId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['comentarios', tareaId] }),
  })
}
