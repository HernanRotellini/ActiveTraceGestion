"""Cliente Moodle Web Services para sincronización de datos.

Comunicación async con Moodle vía su API WS usando httpx.
Soporta retry con exponential backoff para errores transitorios.
"""

import asyncio
from dataclasses import dataclass

import httpx


class MoodleError(ConnectionError):
    """Error de conexión con Moodle WS."""


class MoodleAuthError(MoodleError):
    """Error de autenticación con Moodle (token inválido)."""


@dataclass(frozen=True)
class MoodleConfig:
    """Configuración de conexión a Moodle para un tenant."""

    base_url: str
    token: str


class MoodleClient:
    """Cliente async para Moodle Web Services.

    Se inyecta como dependencia opcional en PadronService.
    Sin credenciales configuradas, las operaciones de sync fallan
    gracefulmente con un mensaje descriptivo.
    """

    def __init__(self, config: MoodleConfig | None = None) -> None:
        self.config = config
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """True si hay credenciales configuradas."""
        return self.config is not None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _call_ws(self, ws_function: str, **params: object) -> dict:
        """Llama a una función WS de Moodle con retry logic.

        Args:
            ws_function: Nombre de la función WS (ej: core_enrol_get_enrolled_users).
            **params: Parámetros de la llamada.

        Returns:
            Respuesta JSON de Moodle.

        Raises:
            MoodleAuthError: Si el token es inválido (401).
            MoodleError: Si hay error de conexión después de reintentos.
        """
        if not self.is_configured or self.config is None:
            raise MoodleError("Moodle no está configurado para este tenant")

        client = await self._get_client()
        url = f"{self.config.base_url.rstrip('/')}/webservice/rest/server.php"
        params_with_token: dict[str, object] = {
            "wstoken": self.config.token,
            "wsfunction": ws_function,
            "moodlewsrestformat": "json",
            **params,
        }

        max_retries = 3
        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                response = await client.post(url, data=params_with_token)
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                last_error = MoodleError(f"Error de conexión con Moodle: {exc}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # exponential backoff
                continue

            if response.status_code == 401:
                raise MoodleAuthError("Token de Moodle inválido o expirado")
            if response.status_code >= 500:
                last_error = MoodleError(f"Moodle respondió con error {response.status_code}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                continue

            data = response.json()
            if isinstance(data, dict) and "exception" in data:
                raise MoodleError(f"Error de Moodle WS: {data.get('message', 'unknown')}")

            return data  # type: ignore[return-value]

        raise MoodleError("No se pudo conectar con Moodle después de varios intentos") from last_error

    async def sync_usuarios(self, course_id: int) -> list[dict]:
        """Obtiene usuarios inscriptos en un curso de Moodle.

        Args:
            course_id: ID del curso en Moodle.

        Returns:
            Lista de dicts con: id, nombre, apellidos, email.
        """
        data = await self._call_ws("core_enrol_get_enrolled_users", courseid=course_id)
        if not isinstance(data, list):
            return []
        usuarios = []
        for user in data:
            usuarios.append({
                "id": user.get("id"),
                "nombre": user.get("firstname", ""),
                "apellidos": user.get("lastname", ""),
                "email": user.get("email", ""),
            })
        return usuarios

    async def sync_actividades(self, course_id: int) -> list[dict]:
        """Obtiene actividades de un curso de Moodle.

        Args:
            course_id: ID del curso en Moodle.

        Returns:
            Lista de dicts con: id, name, type, grademax.
        """
        data = await self._call_ws("core_course_get_contents", courseid=course_id)
        if not isinstance(data, list):
            return []
        actividades = []
        for section in data:
            modules = section.get("modules", [])
            for mod in modules:
                actividades.append({
                    "id": mod.get("id"),
                    "name": mod.get("name", ""),
                    "type": mod.get("modplural", ""),
                    "grademax": _extract_grademax(mod),
                })
        return actividades


def _extract_grademax(module: dict) -> float | None:
    """Extrae el grade_max de un módulo de Moodle si existe."""
    # La estructura de Moodle puede variar; intentamos varios caminos
    raw = module.get("grade_max")
    if raw is not None:
        try:
            return float(raw)
        except (ValueError, TypeError):
            return None
    # Buscar en los campos personalizados
    for field in module.get("customdata", []):
        if isinstance(field, dict) and field.get("name") == "grade_max":
            try:
                return float(field["value"])
            except (ValueError, TypeError):
                return None
    return None
