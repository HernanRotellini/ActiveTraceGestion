"""Router de sincronización con Moodle Web Services."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import get_current_user, get_db
from app.integrations.moodle_ws import MoodleClient, MoodleConfig
from app.services.auth import CurrentUser
from app.services.padron import PadronError, PadronService

router = APIRouter(prefix="/api/v1/moodle", tags=["moodle"])


@router.post("/sync/{materia_id}")
async def sync_desde_moodle(
    materia_id: str,
    cohorte_id: str,
    course_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Sincroniza padrón desde Moodle WS para una materia.

    Args:
        materia_id: UUID de la materia en activia-trace.
        cohorte_id: UUID de la cohorte.
        course_id: ID del curso en Moodle.
    """
    settings = Settings()  # type: ignore[call-arg]

    # Construir MoodleClient desde configuración del tenant
    moodle_config = _build_moodle_config(settings, current_user.tenant_id)
    moodle_client = MoodleClient(config=moodle_config)

    service = PadronService(
        session=db,
        tenant_id=current_user.tenant_id,
        current_user_id=current_user.user_id,
        encryption_key=settings.ENCRYPTION_KEY,
    )

    try:
        result = await service.sync_desde_moodle(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            moodle_client=moodle_client,
            course_id=course_id,
        )
    except PadronError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return result


def _build_moodle_config(settings: Settings, tenant_id: str) -> MoodleConfig | None:
    """Construye la config de Moodle desde variables de entorno.

    Por ahora usa variables globales. En el futuro se puede extender
    para leer configuración por tenant desde la DB.
    """
    base_url = getattr(settings, "MOODLE_BASE_URL", None)
    token = getattr(settings, "MOODLE_TOKEN", None)
    if base_url and token:
        return MoodleConfig(base_url=base_url, token=token)
    return None
