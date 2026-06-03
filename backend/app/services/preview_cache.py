"""Caché temporal en memoria para previews de importación de padrón.

Almacena los resultados del preview para que puedan ser confirmados
en un paso posterior. TTL de 30 minutos.
"""

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class PreviewEntry:
    """Entrada de preview almacenada en caché."""

    materia_id: str
    cohorte_id: str
    columnas: list[dict[str, str]]  # [{"nombre": ..., "mapeo": ...}]
    filas: list[dict[str, str]]  # [{"fila": ..., "datos": {...}}]
    total_filas: int
    created_at: float = field(default_factory=time.time)


TTL_SECONDS = 30 * 60  # 30 minutos

_cache: dict[str, PreviewEntry] = {}


def _limpiar_expirados() -> None:
    """Elimina entradas expiradas del caché."""
    now = time.time()
    expirados = [k for k, v in _cache.items() if now - v.created_at > TTL_SECONDS]
    for k in expirados:
        del _cache[k]


def guardar_preview(
    materia_id: str,
    cohorte_id: str,
    columnas: list[dict[str, str]],
    filas: list[dict[str, str]],
    total_filas: int,
) -> str:
    """Guarda un preview y devuelve el token.

    Args:
        materia_id: ID de la materia.
        cohorte_id: ID de la cohorte.
        columnas: Columnas detectadas con su mapeo.
        filas: Filas de preview.
        total_filas: Total de filas parseadas.

    Returns:
        Token UUID para recuperar el preview.
    """
    _limpiar_expirados()
    token = str(uuid.uuid4())
    _cache[token] = PreviewEntry(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        columnas=columnas,
        filas=filas,
        total_filas=total_filas,
    )
    return token


def obtener_preview(token: str) -> PreviewEntry | None:
    """Recupera un preview por token.

    Args:
        token: Token del preview.

    Returns:
        PreviewEntry si existe y no ha expirado, None en caso contrario.
    """
    _limpiar_expirados()
    entry = _cache.get(token)
    if entry is None:
        return None
    if time.time() - entry.created_at > TTL_SECONDS:
        del _cache[token]
        return None
    return entry


def eliminar_preview(token: str) -> None:
    """Elimina un preview del caché."""
    _cache.pop(token, None)
