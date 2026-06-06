"""Worker asíncrono de despacho de comunicaciones.

Procesa comunicaciones Pendiente que pueden ser enviadas:
- Si el tenant NO requiere aprobación → procesa directo
- Si el tenant requiere aprobación → salta (deben aprobarse manualmente)
"""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.database import create_engine_from_url, get_sessionmaker
from app.core.encryption import decrypt_sensitive_value
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.tenant import Tenant
from app.workers.stubs import simular_envio

logger = logging.getLogger(__name__)

POLL_INTERVAL_DEFAULT = 30
STUB_SUCCESS_RATE_DEFAULT = 0.95


class ComunicacionWorker:
    """Worker de polling que despacha comunicaciones Pendiente."""

    def __init__(
        self,
        settings: Settings | None = None,
        poll_interval: int = POLL_INTERVAL_DEFAULT,
        success_rate: float = STUB_SUCCESS_RATE_DEFAULT,
    ) -> None:
        self.settings = settings or Settings()  # type: ignore[call-arg]
        self.poll_interval = poll_interval
        self.success_rate = success_rate
        self._running = False

    async def start(self) -> None:
        """Inicia el bucle de polling."""
        logger.info(
            "ComunicacionWorker iniciado (poll cada %ds, success_rate=%.2f)",
            self.poll_interval,
            self.success_rate,
        )
        self._running = True

        engine = create_engine_from_url(self.settings.DATABASE_URL)
        sessionmaker = get_sessionmaker()

        try:
            while self._running:
                try:
                    async with sessionmaker() as session:
                        await self._poll(session)
                except Exception:
                    logger.exception("Error en ciclo de poll")
                await asyncio.sleep(self.poll_interval)
        except asyncio.CancelledError:
            logger.info("ComunicacionWorker detenido")
        finally:
            self._running = False

    def stop(self) -> None:
        """Detiene el worker."""
        self._running = False

    async def _poll(self, session: AsyncSession) -> None:
        """Un ciclo de poll: busca Pendientes y las procesa."""
        result = await session.execute(
            select(Comunicacion).where(
                Comunicacion.estado == EstadoComunicacion.PENDIENTE,
                Comunicacion.deleted_at.is_(None),
            )
            .order_by(Comunicacion.created_at.asc())
            .limit(50)
        )
        pendientes = list(result.scalars().all())
        if not pendientes:
            return

        logger.debug("Procesando %d comunicaciones Pendiente", len(pendientes))

        por_tenant: dict[str, list[Comunicacion]] = {}
        for c in pendientes:
            key = str(c.tenant_id)
            por_tenant.setdefault(key, []).append(c)

        for tenant_id_str, comunicaciones in por_tenant.items():
            tenant_id_uuid = comunicaciones[0].tenant_id
            tenant = await session.get(Tenant, tenant_id_uuid)
            tenant_settings = getattr(tenant, "settings", None) or {}
            aprobacion_obligatoria = tenant_settings.get("aprobacion_comunicaciones_obligatoria", False)

            if aprobacion_obligatoria:
                logger.debug(
                    "Tenant %s requiere aprobación — saltando %d comunicaciones",
                    tenant_id_str,
                    len(comunicaciones),
                )
                continue

            for com in comunicaciones:
                try:
                    await self._procesar(session, com)
                except Exception:
                    logger.exception("Error procesando comunicación %s", com.id)

        await session.commit()

    async def _procesar(self, session: AsyncSession, com: Comunicacion) -> None:
        """Procesa una comunicación: Pendiente → Enviando → Enviado/Error."""
        com.estado = EstadoComunicacion.ENVIANDO
        await session.flush()

        try:
            destinatario = decrypt_sensitive_value(
                com.destinatario, encryption_key=self.settings.ENCRYPTION_KEY
            )
        except Exception:
            logger.error("No se pudo descifrar destinatario para %s", com.id)
            com.estado = EstadoComunicacion.ERROR
            return

        exito = await simular_envio(
            destinatario,
            com.asunto,
            com.cuerpo,
            success_rate=self.success_rate,
        )

        if exito:
            com.estado = EstadoComunicacion.ENVIADO
            from datetime import UTC, datetime  # noqa: PLC0415
            com.enviado_at = datetime.now(UTC)
        else:
            com.estado = EstadoComunicacion.ERROR
