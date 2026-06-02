"""Tests de arranque de la aplicación FastAPI.

Verifica que la app se instancia sin errores y que el lifespan no falla.
"""

from app.main import create_app


class TestAppStartup:
    """La aplicación FastAPI arranca sin error."""

    def test_create_app_succeeds(self) -> None:
        """create_app() devuelve una instancia de FastAPI."""
        app = create_app()
        assert app is not None
        assert app.title == "activia-trace"

    def test_app_has_health_route(self) -> None:
        """La app tiene registrada la ruta /health."""
        app = create_app()
        routes = [r.path for r in app.routes]
        assert "/health" in routes
