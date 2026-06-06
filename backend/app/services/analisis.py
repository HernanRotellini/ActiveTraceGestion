"""Servicios de análisis: atrasados, ranking, reportes, monitor."""

import csv
import io
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permisos import ANALISIS_CONSULTAR, ANALISIS_EXPORTAR
from app.repositories.analisis import AnalisisRepository
from app.repositories.asignaciones import AsignacionRepository

logger = logging.getLogger(__name__)

ROLES_GLOBALES: frozenset[str] = frozenset({"COORDINADOR", "ADMIN", "NEXO"})


class AnalisisService:

    def __init__(self, session: AsyncSession, tenant_id: UUID, usuario_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.usuario_id = usuario_id
        self._repo = AnalisisRepository(session, tenant_id)

    async def compute_atrasados(self, materia_id: UUID) -> list[dict]:
        self._registrar_auditoria(ANALISIS_CONSULTAR, materia_id, {"tipo": "atrasados"})
        return await self._repo.listar_atrasados(materia_id)

    async def compute_ranking(self, materia_id: UUID) -> dict:
        items = await self._repo.ranking_aprobados(materia_id)
        self._registrar_auditoria(ANALISIS_CONSULTAR, materia_id, {"tipo": "ranking"})
        return {"items": items, "total": len(items)}

    async def compute_reportes_rapidos(self, materia_id: UUID) -> dict:
        self._registrar_auditoria(ANALISIS_CONSULTAR, materia_id, {"tipo": "reportes_rapidos"})
        return await self._repo.reportes_rapidos(materia_id)

    async def compute_notas_finales(self, materia_id: UUID, actividades: list[str]) -> dict:
        items = await self._repo.notas_finales(materia_id, actividades)
        self._registrar_auditoria(ANALISIS_CONSULTAR, materia_id, {"tipo": "notas_finales", "actividades": actividades})
        return {"items": items, "total": len(items)}

    async def compute_tps_sin_corregir(self, materia_id: UUID) -> dict:
        items = await self._repo.tps_sin_corregir(materia_id)
        self._registrar_auditoria(ANALISIS_CONSULTAR, materia_id, {"tipo": "tps_sin_corregir"})
        return {"items": items, "total": len(items)}

    async def get_monitor(
        self,
        filtros: dict,
        usuario_roles: list[str],
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        tiene_scope_global = any(r in ROLES_GLOBALES for r in usuario_roles)

        if tiene_scope_global:
            result = await self._repo.monitor(
                filtros, limit=per_page, offset=(page - 1) * per_page
            )
        else:
            asignacion_repo = AsignacionRepository(self.session, self.tenant_id)
            asignaciones = await asignacion_repo.list_by_usuario(self.usuario_id)
            asignacion_ids = [a.id for a in asignaciones]
            result = await self._repo.monitor_por_asignaciones(
                filtros, asignacion_ids, limit=per_page, offset=(page - 1) * per_page
            )

        result["page"] = page
        result["per_page"] = per_page
        self._registrar_auditoria(ANALISIS_CONSULTAR, filtros.get("materia_id"), {"tipo": "monitor", "filtros": filtros})
        return result

    async def exportar_tps_csv(self, materia_id: UUID) -> str:
        items = await self._repo.tps_sin_corregir(materia_id)
        self._registrar_auditoria(ANALISIS_EXPORTAR, materia_id, {"tipo": "exportar_tps_csv", "cantidad": len(items)})

        output = io.StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(["alumno", "actividad", "materia_id"])
        for item in items:
            writer.writerow([
                item.get("alumno_nombre", ""),
                item.get("actividad", ""),
                str(item.get("materia_id", "")),
            ])
        return output.getvalue()

    def _registrar_auditoria(self, accion: str, materia_id: UUID | None, detalle: dict | None = None) -> None:
        try:
            from app.models.audit import AuditLog  # noqa: PLC0415

            entry = AuditLog(
                tenant_id=self.tenant_id,
                actor_id=self.usuario_id,
                accion=accion,
                recurso_id=str(materia_id) if materia_id else None,
                recurso_tipo="materia",
                detalle=detalle or {},
            )
            self.session.add(entry)
        except (ImportError, Exception):
            pass
