"""Stubs de envío simulado para desarrollo y tests."""

import asyncio
import random


async def simular_envio(
    destinatario: str,
    asunto: str,
    cuerpo: str,
    *,
    success_rate: float = 0.95,
) -> bool:
    """Simula el envío de una comunicación.

    Args:
        destinatario: Email del destinatario.
        asunto: Asunto del mensaje.
        cuerpo: Cuerpo del mensaje.
        success_rate: Probabilidad de éxito (0.0 a 1.0).

    Returns:
        True si el envío fue exitoso, False en caso contrario.
    """
    await asyncio.sleep(0.5)
    return random.random() < success_rate
