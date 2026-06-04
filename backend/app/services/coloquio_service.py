"""Servicio de evaluaciones y coloquios: convocatorias, reservas, resultados."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coloquio import (
    ConvocatoriaAlumno,
    EstadoEvaluacion,
    EstadoReserva,
    Evaluacion,
    ResultadoEvaluacion,
    ReservaEvaluacion,
    TipoEvaluacion,
    TurnoEvaluacion,
)
from app.repositories.coloquio_repository import ColoquioRepository


class ColoquioError(ValueError):
    """Error de dominio en operaciones de coloquios."""


class ColoquioService:
    """Orquesta operaciones de coloquios vía repositorios."""

    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        usuario_id: UUID,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.usuario_id = usuario_id
        self.repo = ColoquioRepository(session, tenant_id)

    # ── Crear convocatoria ──────────────────────────────────────

    async def crear_convocatoria(
        self,
        materia_id: UUID,
        cohorte_id: UUID,
        tipo: str,
        instancia: str,
        turnos_data: list[dict],
    ) -> dict:
        try:
            tipo_enum = TipoEvaluacion(tipo)
        except ValueError:
            raise ColoquioError(f"Tipo de evaluación inválido: {tipo}")

        evaluacion = Evaluacion(
            tenant_id=self.tenant_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=tipo_enum,
            instancia=instancia,
            estado=EstadoEvaluacion.ACTIVA,
        )
        await self.repo.crear_evaluacion(evaluacion)

        turnos: list[TurnoEvaluacion] = []
        for t in turnos_data:
            turno = TurnoEvaluacion(
                tenant_id=self.tenant_id,
                evaluacion_id=evaluacion.id,
                fecha=t["fecha"],
                hora_inicio=t.get("hora_inicio"),
                hora_fin=t.get("hora_fin"),
                cupo_maximo=t["cupo_maximo"],
                cupo_restante=t.get("cupo_restante", t["cupo_maximo"]),
            )
            turnos.append(turno)

        await self.repo.crear_turnos(turnos)

        self._registrar_auditoria(
            "COLOQUIO_CREAR",
            recurso_id=str(evaluacion.id),
            detalle={
                "materia_id": str(materia_id),
                "instancia": instancia,
                "turnos": len(turnos),
            },
        )

        return {
            "id": evaluacion.id,
            "materia_id": evaluacion.materia_id,
            "cohorte_id": evaluacion.cohorte_id,
            "tipo": evaluacion.tipo.value,
            "instancia": evaluacion.instancia,
            "estado": evaluacion.estado.value,
            "turnos": [
                {
                    "id": t.id,
                    "fecha": str(t.fecha),
                    "hora_inicio": str(t.hora_inicio) if t.hora_inicio else None,
                    "hora_fin": str(t.hora_fin) if t.hora_fin else None,
                    "cupo_maximo": t.cupo_maximo,
                    "cupo_restante": t.cupo_restante,
                }
                for t in turnos
            ],
        }

    # ── Importar alumnos ────────────────────────────────────────

    async def importar_alumnos(
        self, evaluacion_id: UUID, alumno_ids: list[UUID],
    ) -> dict:
        evaluacion = await self.repo.get_evaluacion(evaluacion_id)
        if evaluacion is None:
            raise ColoquioError("Convocatoria no encontrada")
        if evaluacion.estado != EstadoEvaluacion.ACTIVA:
            raise ColoquioError("Convocatoria cerrada")

        importados = await self.repo.importar_alumnos(evaluacion_id, alumno_ids)

        self._registrar_auditoria(
            "COLOQUIO_IMPORTAR",
            recurso_id=str(evaluacion_id),
            detalle={"cantidad": importados, "solicitados": len(alumno_ids)},
        )

        return {"importados": importados}

    # ── Listar con métricas ─────────────────────────────────────

    async def listar_con_metricas(
        self, materia_id: UUID | None = None,
    ) -> list[dict]:
        evaluaciones = await self.repo.listar_evaluaciones(materia_id)
        result = []
        for ev in evaluaciones:
            turnos = await self.repo.listar_turnos(ev.id)
            cupos_libres = sum(t.cupo_restante for t in turnos)
            convocados = await self.repo.contar_convocados(ev.id)
            reservas_activas = len([
                r for r in await self.repo.listar_reservas(ev.id)
                if r.estado == EstadoReserva.ACTIVA
            ])
            result.append({
                "id": ev.id,
                "materia_id": ev.materia_id,
                "cohorte_id": ev.cohorte_id,
                "tipo": ev.tipo.value,
                "instancia": ev.instancia,
                "estado": ev.estado.value,
                "total_turnos": len(turnos),
                "alumnos_convocados": convocados,
                "reservas_activas": reservas_activas,
                "cupos_libres": cupos_libres,
                "created_at": ev.created_at,
            })
        return result

    # ── Detalle de convocatoria ─────────────────────────────────

    async def detalle_convocatoria(self, evaluacion_id: UUID) -> dict | None:
        evaluacion = await self.repo.get_evaluacion(evaluacion_id)
        if evaluacion is None:
            return None
        turnos = await self.repo.listar_turnos(evaluacion_id)
        return {
            "id": evaluacion.id,
            "materia_id": evaluacion.materia_id,
            "cohorte_id": evaluacion.cohorte_id,
            "tipo": evaluacion.tipo.value,
            "instancia": evaluacion.instancia,
            "estado": evaluacion.estado.value,
            "turnos": [
                {
                    "id": t.id,
                    "fecha": str(t.fecha),
                    "hora_inicio": str(t.hora_inicio) if t.hora_inicio else None,
                    "hora_fin": str(t.hora_fin) if t.hora_fin else None,
                    "cupo_maximo": t.cupo_maximo,
                    "cupo_restante": t.cupo_restante,
                }
                for t in turnos
            ],
            "created_at": evaluacion.created_at,
            "updated_at": evaluacion.updated_at,
        }

    # ── Turnos de una convocatoria ──────────────────────────────

    async def listar_turnos(self, evaluacion_id: UUID) -> list[dict]:
        turnos = await self.repo.listar_turnos(evaluacion_id)
        return [
            {
                "id": t.id,
                "evaluacion_id": t.evaluacion_id,
                "fecha": str(t.fecha),
                "hora_inicio": str(t.hora_inicio) if t.hora_inicio else None,
                "hora_fin": str(t.hora_fin) if t.hora_fin else None,
                "cupo_maximo": t.cupo_maximo,
                "cupo_restante": t.cupo_restante,
            }
            for t in turnos
        ]

    # ── Reservar turno ──────────────────────────────────────────

    async def reservar(self, evaluacion_id: UUID, turno_id: UUID) -> dict:
        evaluacion = await self.repo.get_evaluacion(evaluacion_id)
        if evaluacion is None:
            raise ColoquioError("Convocatoria no encontrada")
        if evaluacion.estado != EstadoEvaluacion.ACTIVA:
            raise ColoquioError("Convocatoria cerrada")

        if not await self.repo.es_convocado(evaluacion_id, self.usuario_id):
            raise ColoquioError("Alumno no habilitado para esta convocatoria")

        activa = await self.repo.get_reserva_activa(evaluacion_id, self.usuario_id)
        if activa is not None:
            raise ColoquioError("Ya tiene una reserva activa en esta convocatoria")

        turno = await self.repo.get_turno(turno_id)
        if turno is None:
            raise ColoquioError("Turno no encontrado")

        ok = await self.repo.decrementar_cupo(turno_id)
        if not ok:
            raise ColoquioError("Sin cupo disponible")

        reserva = ReservaEvaluacion(
            tenant_id=self.tenant_id,
            evaluacion_id=evaluacion_id,
            turno_id=turno_id,
            alumno_id=self.usuario_id,
            estado=EstadoReserva.ACTIVA,
        )
        await self.repo.crear_reserva(reserva)

        self._registrar_auditoria(
            "COLOQUIO_RESERVAR",
            recurso_id=str(reserva.id),
            detalle={
                "evaluacion_id": str(evaluacion_id),
                "turno_id": str(turno_id),
                "alumno_id": str(self.usuario_id),
            },
        )

        return {
            "id": reserva.id,
            "evaluacion_id": reserva.evaluacion_id,
            "turno_id": reserva.turno_id,
            "alumno_id": reserva.alumno_id,
            "estado": reserva.estado.value,
        }

    # ── Cancelar reserva ────────────────────────────────────────

    async def cancelar_reserva(self, evaluacion_id: UUID) -> dict:
        reserva = await self.repo.get_reserva_activa(evaluacion_id, self.usuario_id)
        if reserva is None:
            raise ColoquioError("Reserva no encontrada o ya cancelada")

        turno_id = reserva.turno_id
        cancelada = await self.repo.cancelar_reserva(reserva.id)
        if cancelada is None:
            raise ColoquioError("Reserva no encontrada o ya cancelada")

        await self.repo.incrementar_cupo(turno_id)

        self._registrar_auditoria(
            "COLOQUIO_CANCELAR",
            recurso_id=str(reserva.id),
            detalle={
                "evaluacion_id": str(evaluacion_id),
                "turno_id": str(turno_id),
                "alumno_id": str(self.usuario_id),
            },
        )

        return {
            "id": cancelada.id,
            "estado": cancelada.estado.value,
            "mensaje": "Reserva cancelada exitosamente",
        }

    # ── Reservas de una convocatoria ────────────────────────────

    async def listar_reservas(self, evaluacion_id: UUID) -> list[dict]:
        reservas = await self.repo.listar_reservas(evaluacion_id)
        return [
            {
                "id": r.id,
                "evaluacion_id": r.evaluacion_id,
                "turno_id": r.turno_id,
                "alumno_id": r.alumno_id,
                "estado": r.estado.value,
                "created_at": r.created_at,
            }
            for r in reservas
        ]

    # ── Registrar resultado ─────────────────────────────────────

    async def registrar_resultado(
        self, evaluacion_id: UUID, alumno_id: UUID, nota_final: str,
    ) -> dict:
        evaluacion = await self.repo.get_evaluacion(evaluacion_id)
        if evaluacion is None:
            raise ColoquioError("Convocatoria no encontrada")

        if not await self.repo.es_convocado(evaluacion_id, alumno_id):
            raise ColoquioError("Alumno no convocado a esta evaluación")

        resultado = ResultadoEvaluacion(
            tenant_id=self.tenant_id,
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
            nota_final=nota_final,
            registrado_por=self.usuario_id,
        )
        await self.repo.upsert_resultado(resultado)

        self._registrar_auditoria(
            "COLOQUIO_RESULTADO",
            recurso_id=str(evaluacion_id),
            detalle={
                "alumno_id": str(alumno_id),
                "nota_final": nota_final,
                "registrado_por": str(self.usuario_id),
            },
        )

        return {
            "id": resultado.id,
            "evaluacion_id": resultado.evaluacion_id,
            "alumno_id": resultado.alumno_id,
            "nota_final": resultado.nota_final,
            "registrado_por": resultado.registrado_por,
        }

    # ── Resultados consolidados ─────────────────────────────────

    async def listar_resultados(self, evaluacion_id: UUID) -> list[dict]:
        resultados = await self.repo.listar_resultados(evaluacion_id)
        return [
            {
                "id": r.id,
                "evaluacion_id": r.evaluacion_id,
                "alumno_id": r.alumno_id,
                "nota_final": r.nota_final,
                "registrado_por": r.registrado_por,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in resultados
        ]

    # ── Panel de métricas global ────────────────────────────────

    async def metricas_globales(self) -> dict:
        return await self.repo.metricas_globales()

    # ── Agenda de reservas ──────────────────────────────────────

    async def agenda_reservas(self) -> list[dict]:
        rows = await self.repo.agenda_reservas()
        return [
            {
                "id": r.id,
                "evaluacion_id": r.evaluacion_id,
                "turno_id": r.turno_id,
                "fecha": str(fecha) if fecha else None,
                "alumno_id": r.alumno_id,
                "created_at": r.created_at,
            }
            for r, fecha in rows
        ]

    # ── Cerrar convocatoria ─────────────────────────────────────

    async def cerrar_convocatoria(self, evaluacion_id: UUID) -> dict:
        evaluacion = await self.repo.cerrar_evaluacion(evaluacion_id)
        if evaluacion is None:
            raise ColoquioError("Convocatoria no encontrada")

        self._registrar_auditoria(
            "COLOQUIO_CERRAR",
            recurso_id=str(evaluacion_id),
            detalle={},
        )

        return {
            "id": evaluacion.id,
            "estado": evaluacion.estado.value,
            "mensaje": "Convocatoria cerrada exitosamente",
        }

    # ── Auditoría ───────────────────────────────────────────────

    def _registrar_auditoria(
        self,
        accion: str,
        recurso_id: str | None = None,
        recurso_tipo: str = "coloquio",
        detalle: dict | None = None,
    ) -> None:
        try:
            from app.models.audit import AuditLog  # noqa: PLC0415

            entry = AuditLog(
                tenant_id=self.tenant_id,
                actor_id=self.usuario_id,
                accion=accion,
                recurso_id=recurso_id,
                recurso_tipo=recurso_tipo,
                detalle=detalle or {},
            )
            self.session.add(entry)
        except (ImportError, Exception):
            pass
