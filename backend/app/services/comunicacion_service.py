"""Servicio de comunicaciones: preview, envío masivo, aprobación, cancelación."""

import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.encryption import decrypt_sensitive_value, encrypt_sensitive_value
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.tenant import Tenant
from app.repositories.analisis import AnalisisRepository
from app.repositories.comunicacion_repository import ComunicacionRepository


class ComunicacionError(ValueError):
    """Error de dominio en operaciones de comunicaciones."""


VARIABLES_SOPORTADAS = {"nombre", "apellido", "materia", "comision"}


def _sustituir_variables(texto: str, variables: dict[str, str]) -> str:
    """Reemplaza variables {{var}} en el texto usando str.replace."""
    resultado = texto
    for clave, valor in variables.items():
        resultado = resultado.replace("{{" + clave + "}}", valor)
    return resultado


def _preview(asunto: str, cuerpo: str, variables: dict[str, str]) -> tuple[str, str]:
    """Renderiza asunto y cuerpo con las variables provistas (RN-16)."""
    return (
        _sustituir_variables(asunto, variables),
        _sustituir_variables(cuerpo, variables),
    )


class ComunicacionService:
    """Orquesta operaciones de comunicaciones vía repositorios."""

    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        usuario_id: UUID,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.usuario_id = usuario_id
        self.settings = settings or Settings()  # type: ignore[call-arg]
        self.com_repo = ComunicacionRepository(session, tenant_id)

    async def preview(
        self, asunto: str, cuerpo: str, variables: dict[str, str]
    ) -> dict[str, str]:
        """Renderiza preview de asunto y cuerpo (RN-16)."""
        asunto_r, cuerpo_r = _preview(asunto, cuerpo, variables)
        return {
            "asunto_renderizado": asunto_r,
            "cuerpo_renderizado": cuerpo_r,
        }

    async def enviar_masivo(
        self, materia_id: UUID, asunto: str, cuerpo: str
    ) -> dict:
        """Encola comunicaciones por alumno atrasado de una materia (F3.2).

        Returns:
            Dict con lote_id y mensajes_creados.
        """
        analisis = AnalisisRepository(self.session, self.tenant_id)
        atrasados = await analisis.listar_atrasados(materia_id)

        if not atrasados:
            return {"lote_id": uuid.uuid4(), "mensajes_creados": 0}

        materia_nombre = await self._obtener_materia_nombre(materia_id)

        lote_id = uuid.uuid4()
        comunicaciones: list[Comunicacion] = []

        for atr in atrasados:
            entrada_id = atr["entrada_padron_id"]
            alumno_nombre = atr.get("alumno_nombre", "")

            entrada = await self._obtener_entrada(entrada_id)
            nombre = entrada.get("nombre", "") if entrada else alumno_nombre
            apellido = entrada.get("apellidos", "") if entrada else ""
            comision = entrada.get("comision", "") if entrada else ""

            variables = {
                "nombre": nombre,
                "apellido": apellido,
                "materia": materia_nombre,
                "comision": comision,
            }

            asunto_final, cuerpo_final = _preview(asunto, cuerpo, variables)

            destinatario_plano = entrada.get("email", "") if entrada else ""
            destinatario_cifrado = encrypt_sensitive_value(
                destinatario_plano, encryption_key=self.settings.ENCRYPTION_KEY
            )

            com = Comunicacion(
                tenant_id=self.tenant_id,
                enviado_por_id=self.usuario_id,
                materia_id=materia_id,
                destinatario=destinatario_cifrado,
                asunto=asunto_final,
                cuerpo=cuerpo_final,
                estado=EstadoComunicacion.PENDIENTE,
                lote_id=lote_id,
            )
            comunicaciones.append(com)

        await self.com_repo.create_batch(comunicaciones)

        self._registrar_auditoria(
            "COMUNICACION_ENVIAR",
            recurso_id=str(materia_id),
            recurso_tipo="materia",
            detalle={"cantidad": len(comunicaciones), "lote_id": str(lote_id)},
        )

        return {"lote_id": lote_id, "mensajes_creados": len(comunicaciones)}

    async def aprobar_lote(self, lote_id: UUID) -> int:
        """Aprueba un lote de comunicaciones (RN-17)."""
        afectados = await self.com_repo.aprobar_lote(lote_id)
        if afectados == 0:
            raise ComunicacionError("No hay comunicaciones Pendiente en este lote")

        self._registrar_auditoria(
            "COMUNICACION_APROBAR",
            recurso_id=str(lote_id),
            recurso_tipo="lote",
            detalle={"lote_id": str(lote_id), "afectados": afectados},
        )
        return afectados

    async def cancelar_lote(self, lote_id: UUID) -> int:
        """Cancela un lote de comunicaciones."""
        afectados = await self.com_repo.cancelar_lote(lote_id)
        self._registrar_auditoria(
            "COMUNICACION_CANCELAR",
            recurso_id=str(lote_id),
            recurso_tipo="lote",
            detalle={"lote_id": str(lote_id), "afectados": afectados},
        )
        return afectados

    async def cancelar_comunicacion(self, comunicacion_id: UUID) -> bool:
        """Cancela una comunicación individual."""
        ok = await self.com_repo.cancelar_comunicacion(comunicacion_id)
        if ok:
            self._registrar_auditoria(
                "COMUNICACION_CANCELAR",
                recurso_id=str(comunicacion_id),
                recurso_tipo="comunicacion",
                detalle={"comunicacion_id": str(comunicacion_id)},
            )
        return ok

    async def listar_lotes(self) -> dict:
        """Lista lotes con resumen de estados."""
        lotes = await self.com_repo.list_lotes()
        return {"items": lotes, "total": len(lotes)}

    async def detalle_lote(self, lote_id: UUID) -> dict:
        """Retorna detalle de comunicaciones de un lote."""
        comunicaciones = await self.com_repo.detalle_lote(lote_id)
        if not comunicaciones:
            raise ComunicacionError("Lote no encontrado o vacío")

        items = []
        for c in comunicaciones:
            destinatario_plano = self._desencriptar_destinatario(c.destinatario)
            items.append({
                "id": c.id,
                "materia_id": c.materia_id,
                "destinatario": destinatario_plano,
                "asunto": c.asunto,
                "cuerpo": c.cuerpo,
                "estado": c.estado.value,
                "lote_id": c.lote_id,
                "enviado_at": c.enviado_at,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            })

        return {
            "lote_id": lote_id,
            "materia_id": comunicaciones[0].materia_id,
            "comunicaciones": items,
        }

    async def aprobacion_requerida(self) -> bool:
        """Verifica si el tenant requiere aprobación de comunicaciones."""
        tenant = await self.session.get(Tenant, self.tenant_id)
        if tenant is None:
            return False
        settings = getattr(tenant, "settings", None) or {}
        return bool(settings.get("aprobacion_comunicaciones_obligatoria", False))

    async def _obtener_materia_nombre(self, materia_id: UUID) -> str:
        from app.models.estructura_academica import Materia  # noqa: PLC0415
        materia = await self.session.get(Materia, materia_id)
        return materia.nombre if materia else ""

    async def _obtener_entrada(self, entrada_id: UUID) -> dict | None:
        from app.models.padron import EntradaPadron  # noqa: PLC0415
        entrada = await self.session.get(EntradaPadron, entrada_id)
        if entrada is None:
            return None
        return {
            "nombre": entrada.nombre,
            "apellidos": entrada.apellidos,
            "email": entrada.email,
            "comision": entrada.comision,
        }

    def _desencriptar_destinatario(self, ciphertext: str) -> str:
        try:
            return decrypt_sensitive_value(ciphertext, encryption_key=self.settings.ENCRYPTION_KEY)
        except Exception:
            return "[cifrado]"

    def _registrar_auditoria(
        self,
        accion: str,
        recurso_id: str | None = None,
        recurso_tipo: str = "comunicacion",
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
