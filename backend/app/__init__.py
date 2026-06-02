"""activia-trace backend."""

import asyncio
import sys

# Windows: SelectorEventLoop en lugar de ProactorEventLoop para compatibilidad
# con asyncpg (SSL handshake falla con ProactorEventLoop).
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
