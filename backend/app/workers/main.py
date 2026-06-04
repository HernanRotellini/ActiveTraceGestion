"""Entrypoint del worker de background.

Arranca el ComunicacionWorker (C-12) que despacha comunicaciones Pendiente
mediante polling a la base de datos.
"""

import asyncio
import logging

from app.workers.comunicaciones_worker import ComunicacionWorker

logger = logging.getLogger(__name__)


async def main() -> None:
    """Loop principal del worker — delega al ComunicacionWorker."""
    logger.info("Worker iniciado — arrancando ComunicacionWorker")
    worker = ComunicacionWorker()
    try:
        await worker.start()
    except asyncio.CancelledError:
        logger.info("Worker detenido")


if __name__ == "__main__":
    asyncio.run(main())
