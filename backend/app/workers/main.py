"""Entrypoint del worker de background.

C-01: placeholder no-op. La tecnología real de la cola se define en ADR-003
(comunicaciones-cola-worker, C-12). Este archivo existe para que el servicio
`worker` en docker-compose tenga un entrypoint que correr.

COMPORTAMIENTO ACTUAL: log infinito cada 60 segundos. Reemplazar cuando se
implemente el sistema de colas real.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    """Loop principal del worker.

    Placeholder: log de heartbeat y sleep. No procesa nada todavía.
    """
    logger.info("Worker iniciado (placeholder — sin lógica de cola todavía)")
    try:
        while True:
            logger.debug("Worker heartbeat — sin tareas pendientes")
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        logger.info("Worker detenido")


if __name__ == "__main__":
    asyncio.run(main())
