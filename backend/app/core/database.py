"""Configuración del engine y sesión async de SQLAlchemy 2.0.

- Engine async único a nivel de módulo, creado en el arranque (lifespan).
- async_sessionmaker(expire_on_commit=False) como factory de sesiones.
- Base declarativa para modelos ORM.

La creación/disposición del engine la gestiona el lifespan de la app.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Se inicializa en create_engine_from_settings() o via lifespan
_engine = None  # type: ignore
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM del proyecto."""


def create_engine_from_url(database_url: str) -> None:
    """Crea el engine async y la sessionmaker a partir de una URL de conexión.

    Debe llamarse en el arranque (lifespan) antes de cualquier operación.

    Args:
        database_url: URL de PostgreSQL con driver asyncpg,
                      ej: "postgresql+asyncpg://user:pass@host:port/db"
    """
    global _engine, _sessionmaker  # noqa: PLW0603
    _engine = create_async_engine(database_url, echo=False, pool_size=5, max_overflow=10)
    _sessionmaker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def dispose_engine() -> None:
    """Cierra el engine y libera el pool de conexiones.

    Debe llamarse en el shutdown del lifespan.
    """
    global _engine, _sessionmaker  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _sessionmaker = None


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Retorna la sessionmaker global.

    Raises:
        RuntimeError: Si el engine no fue inicializado (create_engine_from_url no fue llamado).
    """
    if _sessionmaker is None:
        raise RuntimeError(
            "El engine de base de datos no fue inicializado. "
            "Llama a create_engine_from_url() antes de obtener sesiones."
        )
    return _sessionmaker
