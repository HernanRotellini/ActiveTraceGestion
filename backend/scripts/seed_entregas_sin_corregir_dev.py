"""Carga datos mínimos para probar Entregas sin corregir.

No escribe tablas manualmente: usa CalificacionService con el mismo flujo
preview + confirm que la API de importación de calificaciones.
"""

import asyncio
from uuid import UUID

from sqlalchemy import select

from app.core.config import Settings
from app.core.database import create_engine_from_url, dispose_engine, get_sessionmaker
from app.models.auth import AuthUser
from app.services.calificaciones import CalificacionService

MATERIA_PROGRAMACION_I = UUID("611c70fc-17a6-4030-9339-4704e6c475ae")
COHORTE_SISTEMAS_2026 = UUID("1b73b942-cb57-41cd-b5a9-9b7a630fef61")


async def main() -> None:
    settings = Settings()
    create_engine_from_url(settings.DATABASE_URL)
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        result = await session.execute(
            select(AuthUser).where(AuthUser.email == "admin@test.com")
        )
        admin = result.scalar_one()

        service = CalificacionService(session, admin.tenant_id, admin.id)
        csv_content = (
            "Nombre,Apellidos,Email,Trabajo Final\n"
            "Alumno,Uno,alumno1@test.com,Aprobado\n"
        ).encode("utf-8")

        preview = await service.importar_grades(
            MATERIA_PROGRAMACION_I,
            COHORTE_SISTEMAS_2026,
            "entregas_textuales.csv",
            csv_content,
        )
        import_result = await service.confirmar_import(
            preview["preview_token"],
            ["Trabajo Final"],
        )
        await session.commit()

        print(import_result)

    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
