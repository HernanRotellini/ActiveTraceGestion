"""Repository tenant-scoped para Asignacion."""

from datetime import date as date_type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estructura_academica import Carrera, Cohorte, Materia
from app.models.usuarios_asignaciones import Asignacion
from app.repositories.base import TenantScopedRepository


def _asignacion_to_dict(
    asignacion: Asignacion,
    materia_nombre: str | None,
    carrera_nombre: str | None,
    cohorte_nombre: str | None,
) -> dict:
    return {
        "id": asignacion.id,
        "usuario_id": asignacion.usuario_id,
        "rol": asignacion.rol,
        "materia_id": asignacion.materia_id,
        "carrera_id": asignacion.carrera_id,
        "cohorte_id": asignacion.cohorte_id,
        "comisiones": asignacion.comisiones,
        "responsable_id": asignacion.responsable_id,
        "desde": asignacion.desde,
        "hasta": asignacion.hasta,
        "created_at": asignacion.created_at,
        "updated_at": asignacion.updated_at,
        "materia_nombre": materia_nombre,
        "carrera_nombre": carrera_nombre,
        "cohorte_nombre": cohorte_nombre,
    }


class AsignacionRepository(TenantScopedRepository[Asignacion]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Asignacion, tenant_id)

    async def list_by_materia(self, materia_id: UUID) -> list[Asignacion]:
        result = await self.session.execute(
            select(Asignacion).where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.materia_id == materia_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_usuario(self, usuario_id: UUID) -> list[Asignacion]:
        result = await self.session.execute(
            select(Asignacion).where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.usuario_id == usuario_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_rol(self, rol: str) -> list[Asignacion]:
        result = await self.session.execute(
            select(Asignacion).where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.rol == rol,
            )
        )
        return list(result.scalars().all())

    async def list_by_filters(
        self,
        usuario_id: UUID | None = None,
        materia_id: UUID | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        rol: str | None = None,
        estado: str | None = None,
    ) -> list[Asignacion]:
        query = select(Asignacion).where(
            Asignacion.tenant_id == self.tenant_id,
            Asignacion.deleted_at.is_(None),
        )
        if usuario_id is not None:
            query = query.where(Asignacion.usuario_id == usuario_id)
        if materia_id is not None:
            query = query.where(Asignacion.materia_id == materia_id)
        if carrera_id is not None:
            query = query.where(Asignacion.carrera_id == carrera_id)
        if cohorte_id is not None:
            query = query.where(Asignacion.cohorte_id == cohorte_id)
        if rol is not None:
            query = query.where(Asignacion.rol == rol)
        if estado == "vigente":
            today = date_type.today()
            query = query.where(
                (Asignacion.hasta.is_(None)) | (Asignacion.hasta >= today)
            )
        elif estado == "vencida":
            today = date_type.today()
            query = query.where(
                (Asignacion.hasta.isnot(None)) & (Asignacion.hasta < today)
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_mis_comisiones_enriched(
        self,
        usuario_id: UUID,
        materia_id: UUID | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        rol: str | None = None,
        estado: str | None = None,
    ) -> list[dict]:
        query = (
            select(Asignacion, Materia.nombre, Carrera.nombre, Cohorte.nombre)
            .outerjoin(
                Materia,
                (Materia.id == Asignacion.materia_id)
                & (Materia.tenant_id == self.tenant_id)
                & (Materia.deleted_at.is_(None)),
            )
            .outerjoin(
                Carrera,
                (Carrera.id == Asignacion.carrera_id)
                & (Carrera.tenant_id == self.tenant_id)
                & (Carrera.deleted_at.is_(None)),
            )
            .outerjoin(
                Cohorte,
                (Cohorte.id == Asignacion.cohorte_id)
                & (Cohorte.tenant_id == self.tenant_id)
                & (Cohorte.deleted_at.is_(None)),
            )
            .where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.usuario_id == usuario_id,
            )
        )
        if materia_id is not None:
            query = query.where(Asignacion.materia_id == materia_id)
        if carrera_id is not None:
            query = query.where(Asignacion.carrera_id == carrera_id)
        if cohorte_id is not None:
            query = query.where(Asignacion.cohorte_id == cohorte_id)
        if rol is not None:
            query = query.where(Asignacion.rol == rol)
        if estado == "vigente":
            today = date_type.today()
            query = query.where((Asignacion.hasta.is_(None)) | (Asignacion.hasta >= today))
        elif estado == "vencida":
            today = date_type.today()
            query = query.where((Asignacion.hasta.isnot(None)) & (Asignacion.hasta < today))

        result = await self.session.execute(query)
        return [
            _asignacion_to_dict(asignacion, materia_nombre, carrera_nombre, cohorte_nombre)
            for asignacion, materia_nombre, carrera_nombre, cohorte_nombre in result.all()
        ]

    async def get_mi_comision_enriched(
        self,
        asignacion_id: UUID,
        usuario_id: UUID,
    ) -> dict | None:
        query = (
            select(Asignacion, Materia.nombre, Carrera.nombre, Cohorte.nombre)
            .outerjoin(
                Materia,
                (Materia.id == Asignacion.materia_id)
                & (Materia.tenant_id == self.tenant_id)
                & (Materia.deleted_at.is_(None)),
            )
            .outerjoin(
                Carrera,
                (Carrera.id == Asignacion.carrera_id)
                & (Carrera.tenant_id == self.tenant_id)
                & (Carrera.deleted_at.is_(None)),
            )
            .outerjoin(
                Cohorte,
                (Cohorte.id == Asignacion.cohorte_id)
                & (Cohorte.tenant_id == self.tenant_id)
                & (Cohorte.deleted_at.is_(None)),
            )
            .where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.id == asignacion_id,
                Asignacion.usuario_id == usuario_id,
            )
        )
        result = await self.session.execute(query)
        row = result.one_or_none()
        if row is None:
            return None
        asignacion, materia_nombre, carrera_nombre, cohorte_nombre = row
        return _asignacion_to_dict(asignacion, materia_nombre, carrera_nombre, cohorte_nombre)

    async def create(self, **kwargs) -> Asignacion:
        record = Asignacion(tenant_id=self.tenant_id, **kwargs)
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(self, asignacion_id: UUID, **kwargs) -> Asignacion | None:
        record = await self.get(asignacion_id)
        if record is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(record, key, value)
        await self.session.flush()
        return record
