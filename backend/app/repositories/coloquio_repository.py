"""Repositorio tenant-scoped para evaluaciones y coloquios."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coloquio import (
    ConvocatoriaAlumno,
    EstadoEvaluacion,
    EstadoReserva,
    Evaluacion,
    ResultadoEvaluacion,
    ReservaEvaluacion,
    TurnoEvaluacion,
)
from app.repositories.base import TenantScopedRepository


class ColoquioRepository(TenantScopedRepository[Evaluacion]):
    """Acceso a datos de evaluaciones y coloquios, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Evaluacion, tenant_id)

    # ── Evaluacion ──────────────────────────────────────────────

    async def crear_evaluacion(self, evaluacion: Evaluacion) -> Evaluacion:
        self.session.add(evaluacion)
        await self.session.flush()
        return evaluacion

    async def get_evaluacion(self, evaluacion_id: UUID) -> Evaluacion | None:
        return await self.get(evaluacion_id)

    async def listar_evaluaciones(
        self, materia_id: UUID | None = None,
    ) -> list[Evaluacion]:
        stmt = (
            select(Evaluacion)
            .where(
                Evaluacion.tenant_id == self.tenant_id,
                Evaluacion.deleted_at.is_(None),
            )
        )
        if materia_id is not None:
            stmt = stmt.where(Evaluacion.materia_id == materia_id)
        stmt = stmt.order_by(Evaluacion.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def cerrar_evaluacion(self, evaluacion_id: UUID) -> Evaluacion | None:
        evaluacion = await self.get(evaluacion_id)
        if evaluacion is None:
            return None
        evaluacion.estado = EstadoEvaluacion.CERRADA
        return evaluacion

    # ── TurnoEvaluacion ─────────────────────────────────────────

    async def crear_turnos(
        self, turnos: list[TurnoEvaluacion],
    ) -> list[TurnoEvaluacion]:
        self.session.add_all(turnos)
        await self.session.flush()
        return turnos

    async def listar_turnos(self, evaluacion_id: UUID) -> list[TurnoEvaluacion]:
        result = await self.session.execute(
            select(TurnoEvaluacion).where(
                TurnoEvaluacion.tenant_id == self.tenant_id,
                TurnoEvaluacion.evaluacion_id == evaluacion_id,
                TurnoEvaluacion.deleted_at.is_(None),
            ).order_by(TurnoEvaluacion.fecha)
        )
        return list(result.scalars().all())

    async def get_turno(self, turno_id: UUID) -> TurnoEvaluacion | None:
        result = await self.session.execute(
            select(TurnoEvaluacion).where(
                TurnoEvaluacion.id == turno_id,
                TurnoEvaluacion.tenant_id == self.tenant_id,
                TurnoEvaluacion.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def decrementar_cupo(self, turno_id: UUID) -> bool:
        """UPDATE atómico: cupo_restante -= 1 WHERE cupo_restante > 0.
        
        Returns:
            True si se afectó una fila (cupo disponible), False si no.
        """
        result = await self.session.execute(
            update(TurnoEvaluacion)
            .where(
                TurnoEvaluacion.id == turno_id,
                TurnoEvaluacion.tenant_id == self.tenant_id,
                TurnoEvaluacion.deleted_at.is_(None),
                TurnoEvaluacion.cupo_restante > 0,
            )
            .values(cupo_restante=TurnoEvaluacion.cupo_restante - 1)
        )
        return result.rowcount > 0  # type: ignore[return-value]

    async def incrementar_cupo(self, turno_id: UUID) -> None:
        """Restituye cupo: cupo_restante += 1."""
        await self.session.execute(
            update(TurnoEvaluacion)
            .where(
                TurnoEvaluacion.id == turno_id,
                TurnoEvaluacion.tenant_id == self.tenant_id,
                TurnoEvaluacion.deleted_at.is_(None),
            )
            .values(cupo_restante=TurnoEvaluacion.cupo_restante + 1)
        )

    # ── ReservaEvaluacion ───────────────────────────────────────

    async def crear_reserva(self, reserva: ReservaEvaluacion) -> ReservaEvaluacion:
        self.session.add(reserva)
        await self.session.flush()
        return reserva

    async def get_reserva_activa(
        self, evaluacion_id: UUID, alumno_id: UUID,
    ) -> ReservaEvaluacion | None:
        result = await self.session.execute(
            select(ReservaEvaluacion).where(
                ReservaEvaluacion.tenant_id == self.tenant_id,
                ReservaEvaluacion.evaluacion_id == evaluacion_id,
                ReservaEvaluacion.alumno_id == alumno_id,
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
                ReservaEvaluacion.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_reserva(self, reserva_id: UUID) -> ReservaEvaluacion | None:
        result = await self.session.execute(
            select(ReservaEvaluacion).where(
                ReservaEvaluacion.id == reserva_id,
                ReservaEvaluacion.tenant_id == self.tenant_id,
                ReservaEvaluacion.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def cancelar_reserva(self, reserva_id: UUID) -> ReservaEvaluacion | None:
        reserva = await self.get_reserva(reserva_id)
        if reserva is None or reserva.estado != EstadoReserva.ACTIVA:
            return None
        reserva.estado = EstadoReserva.CANCELADA
        return reserva

    async def listar_reservas(self, evaluacion_id: UUID) -> list[ReservaEvaluacion]:
        result = await self.session.execute(
            select(ReservaEvaluacion).where(
                ReservaEvaluacion.tenant_id == self.tenant_id,
                ReservaEvaluacion.evaluacion_id == evaluacion_id,
                ReservaEvaluacion.deleted_at.is_(None),
            ).order_by(ReservaEvaluacion.created_at)
        )
        return list(result.scalars().all())

    async def agenda_reservas(self) -> list[tuple[ReservaEvaluacion, date | None]]:
        """Retorna reservas Activas con fecha del turno para agenda global."""
        result = await self.session.execute(
            select(
                ReservaEvaluacion,
                TurnoEvaluacion.fecha,
            )
            .join(
                TurnoEvaluacion,
                ReservaEvaluacion.turno_id == TurnoEvaluacion.id,
            )
            .where(
                ReservaEvaluacion.tenant_id == self.tenant_id,
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
                ReservaEvaluacion.deleted_at.is_(None),
                TurnoEvaluacion.deleted_at.is_(None),
            )
            .order_by(TurnoEvaluacion.fecha)
        )
        rows = result.all()
        return [(row[0], row[1]) for row in rows]

    # ── ConvocatoriaAlumno ──────────────────────────────────────

    async def importar_alumnos(
        self, evaluacion_id: UUID, alumno_ids: list[UUID],
    ) -> int:
        """Importa alumnos no duplicados. Retorna cantidad de nuevos."""
        importados = 0
        for alumno_id in alumno_ids:
            existe = await self.session.execute(
                select(ConvocatoriaAlumno).where(
                    ConvocatoriaAlumno.tenant_id == self.tenant_id,
                    ConvocatoriaAlumno.evaluacion_id == evaluacion_id,
                    ConvocatoriaAlumno.alumno_id == alumno_id,
                    ConvocatoriaAlumno.deleted_at.is_(None),
                )
            )
            if existe.scalar_one_or_none() is not None:
                continue
            entry = ConvocatoriaAlumno(
                tenant_id=self.tenant_id,
                evaluacion_id=evaluacion_id,
                alumno_id=alumno_id,
            )
            self.session.add(entry)
            importados += 1
        await self.session.flush()
        return importados

    async def es_convocado(self, evaluacion_id: UUID, alumno_id: UUID) -> bool:
        result = await self.session.execute(
            select(ConvocatoriaAlumno).where(
                ConvocatoriaAlumno.tenant_id == self.tenant_id,
                ConvocatoriaAlumno.evaluacion_id == evaluacion_id,
                ConvocatoriaAlumno.alumno_id == alumno_id,
                ConvocatoriaAlumno.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none() is not None

    async def contar_convocados(self, evaluacion_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(ConvocatoriaAlumno)
            .where(
                ConvocatoriaAlumno.tenant_id == self.tenant_id,
                ConvocatoriaAlumno.evaluacion_id == evaluacion_id,
                ConvocatoriaAlumno.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    # ── ResultadoEvaluacion ─────────────────────────────────────

    async def upsert_resultado(
        self, resultado: ResultadoEvaluacion,
    ) -> ResultadoEvaluacion:
        existing = await self.obtener_resultado(
            resultado.evaluacion_id, resultado.alumno_id,
        )
        if existing is not None:
            existing.nota_final = resultado.nota_final
            existing.registrado_por = resultado.registrado_por
            return existing
        self.session.add(resultado)
        await self.session.flush()
        return resultado

    async def obtener_resultado(
        self, evaluacion_id: UUID, alumno_id: UUID,
    ) -> ResultadoEvaluacion | None:
        result = await self.session.execute(
            select(ResultadoEvaluacion).where(
                ResultadoEvaluacion.tenant_id == self.tenant_id,
                ResultadoEvaluacion.evaluacion_id == evaluacion_id,
                ResultadoEvaluacion.alumno_id == alumno_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def listar_resultados(
        self, evaluacion_id: UUID,
    ) -> list[ResultadoEvaluacion]:
        result = await self.session.execute(
            select(ResultadoEvaluacion).where(
                ResultadoEvaluacion.tenant_id == self.tenant_id,
                ResultadoEvaluacion.evaluacion_id == evaluacion_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            ).order_by(ResultadoEvaluacion.created_at)
        )
        return list(result.scalars().all())

    async def contar_resultados(self, evaluacion_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(ResultadoEvaluacion)
            .where(
                ResultadoEvaluacion.tenant_id == self.tenant_id,
                ResultadoEvaluacion.evaluacion_id == evaluacion_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    # ── Métricas globales ───────────────────────────────────────

    async def metricas_globales(self) -> dict:
        """Retorta métricas globales del tenant."""
        convocados = await self.session.execute(
            select(func.count())
            .select_from(ConvocatoriaAlumno)
            .where(
                ConvocatoriaAlumno.tenant_id == self.tenant_id,
                ConvocatoriaAlumno.deleted_at.is_(None),
            )
        )
        activas = await self.session.execute(
            select(func.count())
            .select_from(Evaluacion)
            .where(
                Evaluacion.tenant_id == self.tenant_id,
                Evaluacion.estado == EstadoEvaluacion.ACTIVA,
                Evaluacion.deleted_at.is_(None),
            )
        )
        reservas_activas = await self.session.execute(
            select(func.count())
            .select_from(ReservaEvaluacion)
            .where(
                ReservaEvaluacion.tenant_id == self.tenant_id,
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
                ReservaEvaluacion.deleted_at.is_(None),
            )
        )
        notas = await self.session.execute(
            select(func.count())
            .select_from(ResultadoEvaluacion)
            .where(
                ResultadoEvaluacion.tenant_id == self.tenant_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
        )
        return {
            "alumnos_convocados": convocados.scalar() or 0,
            "convocatorias_activas": activas.scalar() or 0,
            "reservas_activas": reservas_activas.scalar() or 0,
            "notas_registradas": notas.scalar() or 0,
        }
