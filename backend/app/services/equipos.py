"""Servicio de orquestación para operaciones de equipo docente."""

import csv
import io
import logging
from datetime import date as date_type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.asignaciones import AsignacionRepository
from app.repositories.usuarios import UsuarioRepository
from app.schemas.asignaciones import AsignacionResponse

logger = logging.getLogger(__name__)


class NotFoundError(ValueError):
    """Raised when a referenced entity is not found."""


class EquipoService:
    def __init__(self, session: AsyncSession, tenant_id: UUID, encryption_key: str) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._asignacion_repo = AsignacionRepository(session, tenant_id)
        self._usuario_repo = UsuarioRepository(session, tenant_id, encryption_key)

    async def list_mis_equipos(
        self,
        usuario_id: UUID,
        estado: str | None = None,
        materia_id: UUID | None = None,
        rol: str | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
    ) -> list[AsignacionResponse]:
        asignaciones = await self._asignacion_repo.list_by_filters(
            usuario_id=usuario_id,
            estado=estado,
            materia_id=materia_id,
            rol=rol,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
        )
        return [AsignacionResponse.model_validate(a) for a in asignaciones]

    async def asignacion_masiva(
        self,
        usuario_ids: list[UUID],
        materia_id: UUID,
        carrera_id: UUID,
        cohorte_id: UUID,
        rol: str,
        desde: date_type,
        hasta: date_type | None = None,
    ) -> list[AsignacionResponse]:
        usuarios = {}
        for uid in usuario_ids:
            user = await self._usuario_repo.get(uid)
            if user is None:
                raise NotFoundError(f"Usuario with id '{uid}' not found")
            usuarios[uid] = user

        existing = await self._asignacion_repo.list_by_filters(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            rol=rol,
        )
        existing_users = {a.usuario_id for a in existing}

        created = []
        for uid in usuario_ids:
            if uid in existing_users:
                continue
            asignacion = await self._asignacion_repo.create(
                usuario_id=uid,
                materia_id=materia_id,
                carrera_id=carrera_id,
                cohorte_id=cohorte_id,
                rol=rol,
                desde=desde,
                hasta=hasta,
            )
            created.append(asignacion)

        self._audit_action(
            "ASIGNACION_MODIFICAR",
            {
                "accion": "asignacion_masiva",
                "usuarios_asignados": len(created),
                "materia_id": str(materia_id),
                "carrera_id": str(carrera_id),
                "cohorte_id": str(cohorte_id),
                "rol": rol,
            },
        )
        return [AsignacionResponse.model_validate(a) for a in created]

    async def clone_equipo(
        self,
        origen_materia_id: UUID,
        origen_carrera_id: UUID,
        origen_cohorte_id: UUID,
        destino_carrera_id: UUID,
        destino_cohorte_id: UUID,
        destino_desde: date_type,
        destino_hasta: date_type | None = None,
    ) -> list[AsignacionResponse]:
        origen_asignaciones = await self._asignacion_repo.list_by_filters(
            materia_id=origen_materia_id,
            carrera_id=origen_carrera_id,
            cohorte_id=origen_cohorte_id,
            estado="vigente",
        )

        if not origen_asignaciones:
            return []

        created = []
        for a in origen_asignaciones:
            nueva = await self._asignacion_repo.create(
                usuario_id=a.usuario_id,
                rol=a.rol,
                materia_id=a.materia_id,
                carrera_id=destino_carrera_id,
                cohorte_id=destino_cohorte_id,
                comisiones=a.comisiones,
                responsable_id=a.responsable_id,
                desde=destino_desde,
                hasta=destino_hasta,
            )
            created.append(nueva)

        self._audit_action(
            "ASIGNACION_MODIFICAR",
            {
                "accion": "clone_equipo",
                "asignaciones_clonadas": len(created),
                "origen": {
                    "materia_id": str(origen_materia_id),
                    "carrera_id": str(origen_carrera_id),
                    "cohorte_id": str(origen_cohorte_id),
                },
                "destino": {
                    "carrera_id": str(destino_carrera_id),
                    "cohorte_id": str(destino_cohorte_id),
                },
            },
        )
        return [AsignacionResponse.model_validate(a) for a in created]

    async def update_vigencia_equipo(
        self,
        materia_id: UUID,
        carrera_id: UUID,
        cohorte_id: UUID,
        desde: date_type | None = None,
        hasta: date_type | None = None,
    ) -> int:
        asignaciones = await self._asignacion_repo.list_by_filters(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
        )

        affected = 0
        for a in asignaciones:
            update_kwargs: dict[str, object] = {}
            if desde is not None:
                update_kwargs["desde"] = desde
            if hasta is not None:
                update_kwargs["hasta"] = hasta
            if update_kwargs:
                await self._asignacion_repo.update(a.id, **update_kwargs)
                affected += 1

        self._audit_action(
            "ASIGNACION_MODIFICAR",
            {
                "accion": "update_vigencia",
                "asignaciones_afectadas": affected,
                "materia_id": str(materia_id),
                "carrera_id": str(carrera_id),
                "cohorte_id": str(cohorte_id),
            },
        )
        return affected

    async def export_equipo_csv(
        self,
        materia_id: UUID,
        carrera_id: UUID,
        cohorte_id: UUID,
    ) -> str:
        asignaciones = await self._asignacion_repo.list_by_filters(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
        )

        user_ids = {a.usuario_id for a in asignaciones}
        nombres: dict[UUID, str] = {}
        for uid in user_ids:
            user = await self._usuario_repo.get(uid)
            if user is not None:
                nombres[uid] = f"{user.nombre} {user.apellidos}"

        output = io.StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow([
            "docente", "rol", "materia", "carrera", "cohorte",
            "comisiones", "desde", "hasta", "estado_vigencia",
        ])

        for a in asignaciones:
            row = AsignacionResponse.model_validate(a)
            writer.writerow([
                nombres.get(a.usuario_id, str(a.usuario_id)),
                a.rol,
                str(a.materia_id or ""),
                str(a.carrera_id or ""),
                str(a.cohorte_id or ""),
                ",".join(a.comisiones) if a.comisiones else "",
                a.desde.isoformat(),
                a.hasta.isoformat() if a.hasta else "",
                row.estado_vigencia,
            ])

        return output.getvalue()

    def _audit_action(self, accion: str, detalle: dict[str, object]) -> None:
        logger.info("AUDIT: %s | %s", accion, detalle)
