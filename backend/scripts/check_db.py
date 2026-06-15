"""Check database state - what tables exist and alembic version."""
import asyncio, sys

if sys.platform == "win32":
    import asyncio as _a
    _a.set_event_loop_policy(_a.WindowsSelectorEventLoopPolicy())

import sqlalchemy as sa
from app.core.config import Settings
from app.core.database import create_engine_from_url, get_sessionmaker, dispose_engine


async def check():
    settings = Settings()
    connect_args = {"ssl": False} if sys.platform == "win32" else {}
    create_engine_from_url(settings.DATABASE_URL, connect_args=connect_args)
    sm = get_sessionmaker()
    async with sm() as s:
        try:
            r = await s.execute(sa.text("SELECT version_num FROM alembic_version"))
            print("alembic_version:", r.scalar())
        except Exception as e:
            print("No alembic_version table:", e)

        try:
            r = await s.execute(sa.text("SELECT count(*) FROM tenants"))
            print("tenants count:", r.scalar())
        except Exception as e:
            print("tenants table error:", e)

        r = await s.execute(
            sa.text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
        )
        tables = [row[0] for row in r.fetchall()]
        print(f"tables ({len(tables)}): {', '.join(tables)}")
    await dispose_engine()


asyncio.run(check())
