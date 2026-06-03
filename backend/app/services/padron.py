"""Servicio de padrón de alumnos: importación, versionado y sync Moodle."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import encrypt_sensitive_value
from app.integrations.moodle_ws import MoodleClient
from app.models.padron import EntradaPadron, VersionPadron
from app.repositories.padron import EntradaPadronRepository, VersionPadronRepository
from app.services.file_parser import ColumnaDetectada, FilaParseada, ResultadoParseo, parsear_archivo
from app.services.preview_cache import PreviewEntry, eliminar_preview, guardar_preview, obtener_preview


class PadronError(ValueError):
    """Error de dominio en operaciones de padrón."""


class PreviewExpiredError(PadronError):
    """El preview ha expirado (30 min TTL)."""


class PadronService:
    """Orquesta operaciones de padrón vía repositorios."""

    def __init__(self, session: AsyncSession, tenant_id: UUID, current_user_id: UUID, encryption_key: str) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.current_user_id = current_user_id
        self.encryption_key = encryption_key
        self.version_repo = VersionPadronRepository(session, tenant_id)
        self.entrada_repo = EntradaPadronRepository(session, tenant_id)

    async def preview_importar(self, materia_id: str, cohorte_id: str, filename: str, contenido: bytes) -> dict:
        """Paso 1: Parsea el archivo y genera un preview con token.

        Args:
            materia_id: UUID de la materia.
            cohorte_id: UUID de la cohorte.
            filename: Nombre del archivo (para detectar extensión).
            contenido: Contenido binario del archivo.

        Returns:
            Dict con preview_token, columnas, filas preview, total_filas.
        """
        resultado = parsear_archivo(filename, contenido)
        columnas = [{"nombre": c.nombre, "mapeo": c.mapeo} for c in resultado.columnas]
        filas = [{"fila": f.fila, "datos": f.datos} for f in resultado.filas]
        token = guardar_preview(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            columnas=columnas,
            filas=filas,
            total_filas=resultado.total_filas,
        )
        return {
            "preview_token": token,
            "columnas_detectadas": columnas,
            "filas_preview": filas,
            "total_filas": resultado.total_filas,
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
        }

    async def confirmar_importar(self, preview_token: str) -> dict:
        """Paso 2: Confirma la importación usando un token de preview.

        Crea una nueva versión de padrón y todas sus entradas.

        Args:
            preview_token: Token del preview.

        Returns:
            Dict con version_id, materia_id, cohorte_id, entry_count.

        Raises:
            PreviewExpiredError: Si el token expiró o es inválido.
            PadronError: Si ocurre un error de dominio.
        """
        preview = obtener_preview(preview_token)
        if preview is None:
            raise PreviewExpiredError("El preview ha expirado o es inválido (TTL: 30 min)")

        materia_id = UUID(preview.materia_id)
        cohorte_id = UUID(preview.cohorte_id)

        version = await self.version_repo.crear_version(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            cargado_por=self.current_user_id,
        )

        entradas = []
        for fila_data in preview.filas:
            datos = fila_data["datos"] if isinstance(fila_data, dict) else fila_data.datos
            email_encrypted = encrypt_sensitive_value(
                datos.get("email", ""),
                encryption_key=self.encryption_key,
            )
            entrada = EntradaPadron(
                tenant_id=self.tenant_id,
                version_id=version.id,
                nombre=datos.get("nombre", ""),
                apellidos=datos.get("apellidos", ""),
                email=email_encrypted,
                comision=datos.get("comision", ""),
                regional=datos.get("regional"),
            )
            entradas.append(entrada)

        entry_count = await self.entrada_repo.bulk_insert(entradas)

        # Limpiar preview usado
        eliminar_preview(preview_token)

        return {
            "version_id": str(version.id),
            "materia_id": str(materia_id),
            "cohorte_id": str(cohorte_id),
            "entry_count": entry_count,
        }

    async def listar_versiones(self, materia_id: str, page: int = 1, size: int = 20) -> dict:
        """Lista versiones de padrón para una materia."""
        items, total = await self.version_repo.listar_por_materia(
            UUID(materia_id), page=page, size=size
        )
        return {
            "items": [
                {
                    "id": str(v.id),
                    "materia_id": str(v.materia_id),
                    "cohorte_id": str(v.cohorte_id),
                    "cargado_por": str(v.cargado_por),
                    "cargado_at": v.cargado_at.isoformat(),
                    "activa": v.activa,
                    "created_at": v.created_at.isoformat(),
                    "updated_at": v.updated_at.isoformat(),
                }
                for v in items
            ],
            "total": total,
            "page": page,
            "size": size,
        }

    async def vaciar_materia(self, materia_id: str) -> dict:
        """Vacía los datos de padrón del usuario actual para una materia.

        Sigue RN-04: scope (usuario_id, materia_id).

        Args:
            materia_id: UUID de la materia.

        Returns:
            Dict con materia_id y affected_count.
        """
        affected = await self.entrada_repo.vaciar_por_usuario_y_materia(
            usuario_id=self.current_user_id,
            materia_id=UUID(materia_id),
        )
        return {
            "materia_id": materia_id,
            "affected_count": affected,
        }

    async def sync_desde_moodle(
        self,
        materia_id: str,
        cohorte_id: str,
        moodle_client: MoodleClient,
        course_id: int,
    ) -> dict:
        """Sincroniza padrón desde Moodle WS.

        Obtiene usuarios inscriptos de un curso Moodle y los importa
        como una nueva versión de padrón.

        Args:
            materia_id: UUID de la materia.
            cohorte_id: UUID de la cohorte.
            moodle_client: Instancia configurada de MoodleClient.
            course_id: ID del curso en Moodle.

        Returns:
            Dict con resultado de la importación.

        Raises:
            PadronError: Si Moodle no está configurado o hay error de conexión.
        """
        if not moodle_client.is_configured:
            raise PadronError("Moodle no está configurado para este tenant")

        try:
            usuarios = await moodle_client.sync_usuarios(course_id)
        except Exception as exc:
            raise PadronError(f"Error al sincronizar con Moodle: {exc}") from exc

        if not usuarios:
            return {
                "version_id": None,
                "materia_id": materia_id,
                "cohorte_id": cohorte_id,
                "entry_count": 0,
                "message": "No se encontraron usuarios en el curso de Moodle",
            }

        version = await self.version_repo.crear_version(
            materia_id=UUID(materia_id),
            cohorte_id=UUID(cohorte_id),
            cargado_por=self.current_user_id,
        )

        entradas = []
        for user in usuarios:
            email_encrypted = encrypt_sensitive_value(
                user.get("email", ""),
                encryption_key=self.encryption_key,
            )
            entrada = EntradaPadron(
                tenant_id=self.tenant_id,
                version_id=version.id,
                nombre=user.get("nombre", ""),
                apellidos=user.get("apellidos", ""),
                email=email_encrypted,
                comision="",  # Moodle no siempre expone comisión
                regional=None,
            )
            entradas.append(entrada)

        entry_count = await self.entrada_repo.bulk_insert(entradas)
        return {
            "version_id": str(version.id),
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "entry_count": entry_count,
        }
