"""Servicio de grilla salarial para liquidaciones."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.liquidaciones import MateriaPlus, RolLiquidacion, SalarioBase, SalarioPlus
from app.repositories.liquidacion_repository import (
    LiquidacionContextRepository,
    MateriaPlusRepository,
    SalarioBaseRepository,
    SalarioPlusRepository,
)


class GrillaSalarialError(ValueError):
    """Error base de grilla salarial."""


class GrillaSalarialValidationError(GrillaSalarialError):
    """Datos inválidos para grilla salarial."""


class GrillaSalarialOverlapError(GrillaSalarialError):
    """Vigencia solapada con una configuración activa."""


class GrillaSalarialContextError(GrillaSalarialError):
    """Contexto académico inválido para el tenant."""


class GrillaSalarialNotFoundError(GrillaSalarialError):
    """Registro de grilla no encontrado en el tenant."""


class GrillaSalarialService:
    """Orquesta grilla salarial sin consultas directas desde el servicio."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.tenant_id = tenant_id
        self._base_repo = SalarioBaseRepository(session, tenant_id)
        self._plus_repo = SalarioPlusRepository(session, tenant_id)
        self._materia_plus_repo = MateriaPlusRepository(session, tenant_id)
        self._context_repo = LiquidacionContextRepository(session, tenant_id)

    async def create_salario_base(
        self, *, rol: RolLiquidacion, monto: Decimal, desde: date, hasta: date | None = None
    ) -> SalarioBase:
        self._validate_vigencia(desde, hasta)
        if await self._base_repo.has_overlap(rol=rol, desde=desde, hasta=hasta):
            raise GrillaSalarialOverlapError("Ya existe una base salarial activa solapada para el rol")
        return await self._base_repo.create(rol=rol, monto=monto, desde=desde, hasta=hasta)

    async def list_salarios_base(self) -> list[SalarioBase]:
        return await self._base_repo.list()

    async def get_salario_base(self, salario_id: UUID) -> SalarioBase:
        record = await self._base_repo.get(salario_id)
        if record is None:
            raise GrillaSalarialNotFoundError("Salario base no encontrado")
        return record

    async def update_salario_base(
        self,
        salario_id: UUID,
        *,
        rol: RolLiquidacion | None = None,
        monto: Decimal | None = None,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> SalarioBase:
        current = await self.get_salario_base(salario_id)
        next_desde = desde or current.desde
        next_hasta = hasta if hasta is not None else current.hasta
        self._validate_vigencia(next_desde, next_hasta)
        next_rol = rol or current.rol
        if await self._base_repo.has_overlap(rol=next_rol, desde=next_desde, hasta=next_hasta, exclude_id=salario_id):
            raise GrillaSalarialOverlapError("Ya existe una base salarial activa solapada para el rol")
        updated = await self._base_repo.update(salario_id, rol=rol, monto=monto, desde=desde, hasta=hasta)
        if updated is None:
            raise GrillaSalarialNotFoundError("Salario base no encontrado")
        return updated

    async def delete_salario_base(self, salario_id: UUID) -> None:
        if not await self._base_repo.soft_delete(salario_id):
            raise GrillaSalarialNotFoundError("Salario base no encontrado")

    async def create_salario_plus(
        self,
        *,
        rol: RolLiquidacion,
        grupo: str,
        descripcion: str,
        monto: Decimal,
        desde: date,
        hasta: date | None = None,
    ) -> SalarioPlus:
        self._validate_vigencia(desde, hasta)
        if await self._plus_repo.has_overlap(rol=rol, grupo=grupo, desde=desde, hasta=hasta):
            raise GrillaSalarialOverlapError("Ya existe un plus activo solapado para rol y grupo")
        return await self._plus_repo.create(
            rol=rol,
            grupo=grupo,
            descripcion=descripcion,
            monto=monto,
            desde=desde,
            hasta=hasta,
        )

    async def list_salarios_plus(self) -> list[SalarioPlus]:
        return await self._plus_repo.list()

    async def get_salario_plus(self, plus_id: UUID) -> SalarioPlus:
        record = await self._plus_repo.get(plus_id)
        if record is None:
            raise GrillaSalarialNotFoundError("Salario plus no encontrado")
        return record

    async def delete_salario_plus(self, plus_id: UUID) -> None:
        if not await self._plus_repo.soft_delete(plus_id):
            raise GrillaSalarialNotFoundError("Salario plus no encontrado")

    async def create_materia_plus(
        self, *, materia_id: UUID, grupo: str, desde: date, hasta: date | None = None
    ) -> MateriaPlus:
        self._validate_vigencia(desde, hasta)
        if not await self._context_repo.materia_exists(materia_id):
            raise GrillaSalarialContextError("Materia inválida para el tenant")
        if await self._materia_plus_repo.has_overlap(materia_id=materia_id, desde=desde, hasta=hasta):
            raise GrillaSalarialOverlapError("Ya existe un mapeo Materia-Plus activo solapado")
        return await self._materia_plus_repo.create(materia_id=materia_id, grupo=grupo, desde=desde, hasta=hasta)

    async def list_materia_plus(self) -> list[MateriaPlus]:
        return await self._materia_plus_repo.list()

    async def get_materia_plus(self, materia_plus_id: UUID) -> MateriaPlus:
        record = await self._materia_plus_repo.get(materia_plus_id)
        if record is None:
            raise GrillaSalarialNotFoundError("Mapeo Materia-Plus no encontrado")
        return record

    async def delete_materia_plus(self, materia_plus_id: UUID) -> None:
        if not await self._materia_plus_repo.soft_delete(materia_plus_id):
            raise GrillaSalarialNotFoundError("Mapeo Materia-Plus no encontrado")

    def _validate_vigencia(self, desde: date, hasta: date | None) -> None:
        if hasta is not None and hasta < desde:
            raise GrillaSalarialValidationError("La fecha hasta no puede ser anterior a desde")
