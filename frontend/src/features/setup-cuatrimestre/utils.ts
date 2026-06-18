import type { Carrera, Cohorte, Materia } from '@/features/admin/types'

const dateFormatter = new Intl.DateTimeFormat('es-AR', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
})

const dateTimeFormatter = new Intl.DateTimeFormat('es-AR', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'UTC',
})

export function formatDate(value: string) {
  return dateFormatter.format(new Date(value))
}

export function formatDateTime(value: string) {
  return dateTimeFormatter.format(new Date(value))
}

export function toInputDate(value: string) {
  return value.slice(0, 10)
}

export function getCarreraName(carreras: Carrera[] | undefined, carreraId: string | null | undefined) {
  return carreras?.find((carrera) => carrera.id === carreraId)?.nombre ?? 'Sin carrera'
}

export function getCohorteName(cohortes: Cohorte[] | undefined, cohorteId: string | null | undefined) {
  return cohortes?.find((cohorte) => cohorte.id === cohorteId)?.nombre ?? 'Sin cohorte'
}

export function getMateriaName(materias: Materia[] | undefined, materiaId: string | null | undefined) {
  return materias?.find((materia) => materia.id === materiaId)?.nombre ?? 'Sin materia'
}
