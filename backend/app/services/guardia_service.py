"""Servicio de guardias tutoriales: registro, consulta, exportación CSV."""

import csv
import io
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardia import DiaSemana, EstadoGuardia, Guardia
from app.repositories.guardia_repository import GuardiaRepository


class GuardiaError(ValueError):
    """Error de dominio en operaciones de guardias."""


class GuardiaService:
    """Orquesta operaciones de guardias vía repositorios."""

    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        usuario_id: UUID,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.usuario_id = usuario_id
        self.repo = GuardiaRepository(session, tenant_id)

    # ── Registrar guardia ───────────────────────────────────────

    async def registrar(
        self,
        asignacion_id: UUID,
        materia_id: UUID,
        carrera_id: UUID,
        cohorte_id: UUID,
        dia: str,
        horario: str,
        estado: str | None = None,
        comentarios: str | None = None,
    ) -> dict:
        try:
            dia_enum = DiaSemana(dia)
        except ValueError:
            raise GuardiaError(f"Día de semana inválido: {dia}")

        if estado:
            try:
                estado_enum = EstadoGuardia(estado)
            except ValueError:
                raise GuardiaError(f"Estado inválido: {estado}")
        else:
            estado_enum = EstadoGuardia.PENDIENTE

        guardia = Guardia(
            tenant_id=self.tenant_id,
            asignacion_id=asignacion_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            dia=dia_enum,
            horario=horario,
            estado=estado_enum,
            comentarios=comentarios,
        )
        await self.repo.crear(guardia)

        self._registrar_auditoria(
            "GUARDIA_REGISTRAR",
            recurso_id=str(guardia.id),
            detalle={
                "asignacion_id": str(asignacion_id),
                "materia_id": str(materia_id),
            },
        )

        return {
            "id": guardia.id,
            "asignacion_id": guardia.asignacion_id,
            "materia_id": guardia.materia_id,
            "carrera_id": guardia.carrera_id,
            "cohorte_id": guardia.cohorte_id,
            "dia": guardia.dia.value,
            "horario": guardia.horario,
            "estado": guardia.estado.value,
            "comentarios": guardia.comentarios,
            "created_at": guardia.created_at,
        }

    # ── Listar guardias ─────────────────────────────────────────

    async def listar(
        self,
        materia_id: UUID | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        estado: str | None = None,
    ) -> list[dict]:
        guardias = await self.repo.listar_con_filtros(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            estado=estado,
        )
        return [
            {
                "id": g.id,
                "asignacion_id": g.asignacion_id,
                "materia_id": g.materia_id,
                "carrera_id": g.carrera_id,
                "cohorte_id": g.cohorte_id,
                "dia": g.dia.value,
                "horario": g.horario,
                "estado": g.estado.value,
                "comentarios": g.comentarios,
                "created_at": g.created_at,
                "updated_at": g.updated_at,
            }
            for g in guardias
        ]

    # ── Actualizar estado ────────────────────────────────────────

    async def actualizar_estado(
        self, guardia_id: UUID, estado: str, comentarios: str | None = None,
    ) -> dict:
        guardia = await self.repo.actualizar_estado(guardia_id, estado, comentarios)
        if guardia is None:
            raise GuardiaError("Guardia no encontrada")

        self._registrar_auditoria(
            "GUARDIA_ACTUALIZAR",
            recurso_id=str(guardia_id),
            detalle={"estado": estado},
        )

        return {
            "id": guardia.id,
            "asignacion_id": guardia.asignacion_id,
            "materia_id": guardia.materia_id,
            "carrera_id": guardia.carrera_id,
            "cohorte_id": guardia.cohorte_id,
            "dia": guardia.dia.value,
            "horario": guardia.horario,
            "estado": guardia.estado.value,
            "comentarios": guardia.comentarios,
            "updated_at": guardia.updated_at,
        }

    # ── Exportar CSV ─────────────────────────────────────────────

    async def exportar_csv(
        self,
        materia_id: UUID | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        estado: str | None = None,
    ) -> str:
        guardias = await self.repo.listar_con_filtros(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            estado=estado,
        )

        output = io.StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(["id", "asignacion_id", "materia_id", "carrera_id", "cohorte_id",
                         "dia", "horario", "estado", "comentarios", "creada_at"])
        for g in guardias:
            writer.writerow([
                str(g.id),
                str(g.asignacion_id),
                str(g.materia_id),
                str(g.carrera_id),
                str(g.cohorte_id),
                g.dia.value,
                g.horario,
                g.estado.value,
                g.comentarios or "",
                str(g.created_at),
            ])

        self._registrar_auditoria(
            "GUARDIA_EXPORTAR",
            detalle={"cantidad": len(guardias)},
        )

        return output.getvalue()

    # ── Auditoría ───────────────────────────────────────────────

    def _registrar_auditoria(
        self,
        accion: str,
        recurso_id: str | None = None,
        recurso_tipo: str = "guardia",
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
