import { Card } from '@/shared/components/Card'
import { useSession } from '@/shared/hooks/useSession'
import { useCarreras, useCohortesList, useMaterias } from '@/features/admin/hooks/useAdmin'
import { useFechasList, usePeriodosList, useProgramasList } from '@/features/setup-cuatrimestre/hooks/usePeriodos'
import { FechasPanel } from '@/features/setup-cuatrimestre/components/FechasPanel'
import { PeriodosPanel } from '@/features/setup-cuatrimestre/components/PeriodosPanel'
import { ProgramasPanel } from '@/features/setup-cuatrimestre/components/ProgramasPanel'
import { SetupActionCard } from '@/features/setup-cuatrimestre/components/SetupActionCard'

export default function SetupCuatrimestrePage() {
  const { session } = useSession()
  const roles = session?.user.roles ?? []

  const periodosQuery = usePeriodosList()
  const programasQuery = useProgramasList()
  const fechasQuery = useFechasList()
  const carrerasQuery = useCarreras()
  const cohortesQuery = useCohortesList()
  const materiasQuery = useMaterias()

  const periodos = periodosQuery.data?.items ?? []
  const programas = programasQuery.data ?? []
  const fechas = fechasQuery.data ?? []
  const carreras = carrerasQuery.data?.items ?? []
  const cohortes = cohortesQuery.data?.items ?? []
  const materias = materiasQuery.data?.items ?? []

  const activePeriod = periodos.find((periodo) => periodo.activo)
  const activeCarreras = carreras.filter((carrera) => carrera.activo).length
  const activeCohortes = cohortes.filter((cohorte) => cohorte.activo).length
  const activeMaterias = materias.filter((materia) => materia.activo).length

  const estructuraStatus = activeCarreras && activeCohortes && activeMaterias
    ? 'completo'
    : activeCarreras || activeCohortes || activeMaterias
      ? 'en-curso'
      : 'pendiente'

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <Card className="overflow-hidden border-slate-200">
        <div className="bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.22),_transparent_28%),linear-gradient(135deg,#0f172a_0%,#111827_52%,#1e293b_100%)] px-6 py-8 text-white">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div className="max-w-3xl space-y-4">
              <div className="flex flex-wrap gap-2">
                <span className="rounded-full bg-white/12 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-100">Setup Operativo</span>
                <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-xs font-medium text-emerald-100">Visible para COORDINADOR y ADMIN</span>
                {roles.map((role) => <span key={role} className="rounded-full bg-white/8 px-3 py-1 text-xs font-medium text-slate-100">{role}</span>)}
              </div>
              <div className="space-y-2">
                <h1 className="max-w-2xl text-3xl font-semibold tracking-tight text-white">Setup de Cuatrimestre</h1>
                <p className="max-w-2xl text-sm leading-6 text-slate-200">
                  Centraliza el arranque del periodo lectivo: activa el periodo correcto, prepara estructura academica, registra programas y fechas oficiales, y deja a mano los accesos a equipos, avisos y padron.
                </p>
              </div>
            </div>
            <div className="grid min-w-[260px] gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-300">Periodo Activo</p>
                <p className="mt-2 text-lg font-semibold text-white">{activePeriod?.nombre ?? 'Sin definir'}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-300">Programas</p>
                <p className="mt-2 text-lg font-semibold text-white">{programas.length}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-300">Fechas</p>
                <p className="mt-2 text-lg font-semibold text-white">{fechas.length}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-300">Estructura Activa</p>
                <p className="mt-2 text-lg font-semibold text-white">{activeCarreras} carreras - {activeCohortes} cohortes - {activeMaterias} materias</p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 xl:grid-cols-3">
        <SetupActionCard
          step="1"
          title="Periodo Lectivo"
          description="Crea, ajusta y activa el periodo que ordena el trabajo del cuatrimestre."
          status={activePeriod ? 'completo' : periodos.length > 0 ? 'en-curso' : 'pendiente'}
          ctaLabel="Gestionar Periodos"
          href="#periodos"
          meta={activePeriod ? `Activo: ${activePeriod.nombre}` : 'Todavia no hay un periodo activo'}
        />
        <SetupActionCard
          step="2"
          title="Estructura Academica"
          description="Revisa carreras, cohortes y materias antes de cargar documentos o fechas oficiales."
          status={estructuraStatus}
          ctaLabel="Abrir Estructura"
          href="/admin/estructura/carreras"
          meta={`${activeCarreras} carreras activas - ${activeCohortes} cohortes activas - ${activeMaterias} materias activas`}
        />
        <SetupActionCard
          step="3"
          title="Equipos Docentes"
          description="Clona equipos, ajusta vigencias y completa asignaciones del nuevo periodo."
          status={activePeriod ? 'en-curso' : 'bloqueado'}
          ctaLabel="Abrir Equipos"
          href="/coordinacion/equipos-docentes"
          meta={activePeriod ? 'Listo para clonar y ajustar equipos' : 'Activa un periodo antes de seguir'}
        />
        <SetupActionCard
          step="4"
          title="Programas Oficiales"
          description="Registra el programa correcto por materia, carrera y cohorte usando referencia opaca de archivo."
          status={programas.length > 0 ? 'completo' : activePeriod ? 'pendiente' : 'bloqueado'}
          ctaLabel="Ir a Programas"
          href="#programas"
          meta={programas.length > 0 ? `${programas.length} programas cargados` : 'Todavia no hay programas registrados'}
        />
        <SetupActionCard
          step="5"
          title="Fechas de Evaluacion"
          description="Carga el calendario oficial de parciales, TPs, coloquios y recuperatorios."
          status={fechas.length > 0 ? 'completo' : activePeriod ? 'pendiente' : 'bloqueado'}
          ctaLabel="Ir a Fechas"
          href="#fechas"
          meta={fechas.length > 0 ? `${fechas.length} fechas registradas` : 'Todavia no hay fechas registradas'}
        />
        <SetupActionCard
          step="6"
          title="Aviso y Padron"
          description="Publica el aviso de inicio y luego importa el padron desde los modulos existentes."
          status={activePeriod ? 'pendiente' : 'bloqueado'}
          ctaLabel="Abrir Avisos"
          href="/coordinacion/avisos"
          meta={activePeriod ? 'Avisos y padron siguen en sus modulos operativos' : 'Activa un periodo antes de comunicar o importar'}
        />
      </div>

      <PeriodosPanel periodos={periodos} isLoading={periodosQuery.isLoading} />
      <ProgramasPanel programas={programas} carreras={carreras} cohortes={cohortes} materias={materias} isLoading={programasQuery.isLoading || carrerasQuery.isLoading || cohortesQuery.isLoading || materiasQuery.isLoading} />
      <FechasPanel fechas={fechas} periodos={periodos} carreras={carreras} cohortes={cohortes} materias={materias} isLoading={fechasQuery.isLoading || periodosQuery.isLoading || carrerasQuery.isLoading || cohortesQuery.isLoading || materiasQuery.isLoading} />
    </div>
  )
}
