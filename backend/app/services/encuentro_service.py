"""Servicio de encuentros sincrónicos: slots recurrentes, instancias, HTML block."""

import io
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.encuentro import (
    DiaSemana,
    EstadoInstancia,
    InstanciaEncuentro,
    SlotEncuentro,
)
from app.repositories.encuentro_repository import EncuentroRepository


class EncuentroError(ValueError):
    """Error de dominio en operaciones de encuentros."""


class EncuentroService:
    """Orquesta operaciones de encuentros vía repositorios."""

    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        usuario_id: UUID,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.usuario_id = usuario_id
        self.repo = EncuentroRepository(session, tenant_id)

    # ── Crear slot recurrente ───────────────────────────────────

    async def crear_slot_recurrente(
        self,
        asignacion_id: UUID,
        materia_id: UUID,
        titulo: str,
        dia_semana: str,
        hora: time,
        fecha_inicio: date,
        cant_semanas: int,
        meet_url: str | None = None,
        vig_desde: datetime | None = None,
    ) -> dict:
        try:
            dia_enum = DiaSemana(dia_semana)
        except ValueError:
            raise EncuentroError(f"Día de semana inválido: {dia_semana}")

        if cant_semanas > 0 and vig_desde is None:
            vig_desde = datetime.now(UTC)

        slot = SlotEncuentro(
            tenant_id=self.tenant_id,
            asignacion_id=asignacion_id,
            materia_id=materia_id,
            titulo=titulo,
            dia_semana=dia_enum,
            hora=hora,
            fecha_inicio=fecha_inicio,
            cant_semanas=cant_semanas,
            meet_url=meet_url,
            vig_desde=vig_desde or fecha_inicio,
        )
        await self.repo.crear_slot(slot)

        instancias: list[InstanciaEncuentro] = []
        if cant_semanas > 0:
            for i in range(cant_semanas):
                instancia = InstanciaEncuentro(
                    tenant_id=self.tenant_id,
                    slot_id=slot.id,
                    materia_id=materia_id,
                    fecha=fecha_inicio + timedelta(weeks=i),
                    hora=hora,
                    titulo=titulo,
                    estado=EstadoInstancia.PROGRAMADO,
                    meet_url=meet_url,
                )
                instancias.append(instancia)
            await self.repo.crear_instancias_bulk(instancias)

        self._registrar_auditoria(
            "ENCUENTRO_CREAR_SLOT",
            recurso_id=str(slot.id),
            detalle={
                "materia_id": str(materia_id),
                "cant_semanas": cant_semanas,
                "instancias_generadas": len(instancias),
            },
        )

        return {
            "id": slot.id,
            "asignacion_id": slot.asignacion_id,
            "materia_id": slot.materia_id,
            "titulo": slot.titulo,
            "dia_semana": slot.dia_semana.value,
            "hora": str(slot.hora),
            "fecha_inicio": str(slot.fecha_inicio),
            "cant_semanas": slot.cant_semanas,
            "meet_url": slot.meet_url,
            "vig_desde": slot.vig_desde,
            "instancias": [
                {
                    "id": i.id,
                    "fecha": str(i.fecha),
                    "hora": str(i.hora),
                    "titulo": i.titulo,
                    "estado": i.estado.value,
                    "meet_url": i.meet_url,
                }
                for i in instancias
            ],
        }

    # ── Crear instancia única ───────────────────────────────────

    async def crear_instancia_unica(
        self,
        materia_id: UUID,
        fecha: date,
        hora: time,
        titulo: str,
        meet_url: str | None = None,
    ) -> dict:
        instancia = InstanciaEncuentro(
            tenant_id=self.tenant_id,
            materia_id=materia_id,
            fecha=fecha,
            hora=hora,
            titulo=titulo,
            estado=EstadoInstancia.PROGRAMADO,
            meet_url=meet_url,
        )
        await self.repo.crear_instancias_bulk([instancia])

        self._registrar_auditoria(
            "ENCUENTRO_CREAR_UNICO",
            recurso_id=str(instancia.id),
            detalle={
                "materia_id": str(materia_id),
                "fecha": str(fecha),
            },
        )

        return {
            "id": instancia.id,
            "materia_id": instancia.materia_id,
            "fecha": str(instancia.fecha),
            "hora": str(instancia.hora),
            "titulo": instancia.titulo,
            "estado": instancia.estado.value,
            "meet_url": instancia.meet_url,
        }

    # ── Actualizar instancia ────────────────────────────────────

    async def actualizar_instancia(
        self,
        instancia_id: UUID,
        estado: str | None = None,
        meet_url: str | None = None,
        video_url: str | None = None,
        comentario: str | None = None,
    ) -> dict:
        instancia = await self.repo.get_instancia(instancia_id)
        if instancia is None:
            raise EncuentroError("Instancia no encontrada")

        if estado is not None:
            try:
                instancia.estado = EstadoInstancia(estado)
            except ValueError:
                raise EncuentroError(f"Estado inválido: {estado}")
        if meet_url is not None:
            instancia.meet_url = meet_url
        if video_url is not None:
            instancia.video_url = video_url
        if comentario is not None:
            instancia.comentario = comentario

        self._registrar_auditoria(
            "ENCUENTRO_ACTUALIZAR",
            recurso_id=str(instancia_id),
            detalle={
                "estado": estado,
                "tiene_video": video_url is not None,
            },
        )

        return {
            "id": instancia.id,
            "slot_id": instancia.slot_id,
            "materia_id": instancia.materia_id,
            "fecha": str(instancia.fecha),
            "hora": str(instancia.hora),
            "titulo": instancia.titulo,
            "estado": instancia.estado.value,
            "meet_url": instancia.meet_url,
            "video_url": instancia.video_url,
            "comentario": instancia.comentario,
        }

    # ── Generar HTML block ──────────────────────────────────────

    async def generar_html_block(self, materia_id: UUID) -> str:
        instancias = await self.repo.listar_instancias(materia_id)
        if not instancias:
            return "<p>No hay encuentros programados.</p>"

        rows = io.StringIO()
        rows.write("<table border='1' cellpadding='8' cellspacing='0' style='border-collapse:collapse;width:100%'>")
        rows.write("<thead><tr><th>Fecha</th><th>Hora</th><th>Título</th><th>Enlace</th><th>Grabación</th><th>Estado</th></tr></thead><tbody>")
        for i in instancias:
            enlace = f"<a href='{i.meet_url}' target='_blank'>Enlace</a>" if i.meet_url else "-"
            grabacion = f"<a href='{i.video_url}' target='_blank'>Ver grabación</a>" if i.video_url else "-"
            rows.write(
                f"<tr><td>{i.fecha}</td><td>{i.hora}</td><td>{i.titulo}</td>"
                f"<td>{enlace}</td><td>{grabacion}</td><td>{i.estado.value}</td></tr>"
            )
        rows.write("</tbody></table>")
        return rows.getvalue()

    # ── Listar admin ────────────────────────────────────────────

    async def listar_admin(
        self,
        materia_id: UUID | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        estado: str | None = None,
    ) -> list[dict]:
        instancias = await self.repo.listar_admin(
            materia_id=materia_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            estado=estado,
        )
        return [
            {
                "id": i.id,
                "slot_id": i.slot_id,
                "materia_id": i.materia_id,
                "fecha": str(i.fecha),
                "hora": str(i.hora),
                "titulo": i.titulo,
                "estado": i.estado.value,
                "meet_url": i.meet_url,
                "video_url": i.video_url,
                "comentario": i.comentario,
                "created_at": i.created_at,
            }
            for i in instancias
        ]

    # ── Auditoría ───────────────────────────────────────────────

    def _registrar_auditoria(
        self,
        accion: str,
        recurso_id: str | None = None,
        recurso_tipo: str = "encuentro",
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
