"""Servicio de Asignacion con reglas de vigencia y contexto."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.asignaciones import AsignacionRepository
from app.repositories.usuarios import UsuarioRepository


class NotFoundError(ValueError):
    """Raised when a referenced entity is not found."""


class ResponsableNotFoundError(ValueError):
    """Raised when the referenced responsable does not exist."""


class AsignacionService:
    def __init__(self, session: AsyncSession, tenant_id: UUID, encryption_key: str) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._repo = AsignacionRepository(session, tenant_id)
        self._usuario_repo = UsuarioRepository(session, tenant_id, encryption_key)

    async def create_asignacion(self, **kwargs):
        usuario_id = kwargs.get("usuario_id")
        usuario = await self._usuario_repo.get(usuario_id)
        if usuario is None:
            raise NotFoundError(f"Usuario with id '{usuario_id}' not found")
        responsable_id = kwargs.get("responsable_id")
        if responsable_id is not None:
            responsable = await self._usuario_repo.get(responsable_id)
            if responsable is None:
                raise ResponsableNotFoundError(f"Responsable with id '{responsable_id}' not found")
        return await self._repo.create(**kwargs)

    async def get_asignacion(self, asignacion_id: UUID):
        return await self._repo.get(asignacion_id)

    async def get_mi_comision(self, asignacion_id: UUID, usuario_id: UUID):
        record = await self._repo.get(asignacion_id)
        if record is None or record.usuario_id != usuario_id:
            return None
        return record

    async def get_usuario_id_by_email(self, email: str | None) -> UUID | None:
        if not email:
            return None
        usuario = await self._usuario_repo.get_by_email(email)
        if usuario is None:
            return None
        return usuario.id

    async def list_asignaciones(self, materia_id: UUID | None = None, usuario_id: UUID | None = None, rol: str | None = None):
        if materia_id is not None:
            return await self._repo.list_by_materia(materia_id)
        if usuario_id is not None:
            return await self._repo.list_by_usuario(usuario_id)
        if rol is not None:
            return await self._repo.list_by_rol(rol)
        return await self._repo.list()

    async def list_mis_comisiones(
        self,
        usuario_id: UUID,
        materia_id: UUID | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        rol: str | None = None,
        estado: str | None = None,
    ):
        return await self._repo.list_by_filters(
            usuario_id=usuario_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            rol=rol,
            estado=estado,
        )

    async def list_mis_comisiones_enriched(
        self,
        usuario_id: UUID,
        materia_id: UUID | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        rol: str | None = None,
        estado: str | None = None,
    ):
        return await self._repo.list_mis_comisiones_enriched(
            usuario_id=usuario_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            rol=rol,
            estado=estado,
        )

    async def get_mi_comision_enriched(self, asignacion_id: UUID, usuario_id: UUID):
        return await self._repo.get_mi_comision_enriched(asignacion_id, usuario_id)

    async def update_asignacion(self, asignacion_id: UUID, **kwargs):
        record = await self._repo.get(asignacion_id)
        if record is None:
            raise NotFoundError(f"Asignacion with id '{asignacion_id}' not found")
        if "responsable_id" in kwargs and kwargs["responsable_id"] is not None:
            responsable = await self._usuario_repo.get(kwargs["responsable_id"])
            if responsable is None:
                raise ResponsableNotFoundError(f"Responsable with id '{kwargs['responsable_id']}' not found")
        return await self._repo.update(asignacion_id, **kwargs)

    async def delete_asignacion(self, asignacion_id: UUID) -> bool:
        return await self._repo.soft_delete(asignacion_id)
