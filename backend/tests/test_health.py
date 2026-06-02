"""Tests para el endpoint GET /health.

Verifica liveness de la app y readiness de la base de datos.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    """GET /health responde correctamente."""

    async def test_health_returns_200(self, async_client: AsyncClient) -> None:
        """GET /health → 200 OK con status field."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    async def test_health_has_database_field(self, async_client: AsyncClient) -> None:
        """La respuesta incluye estado de la base de datos."""
        response = await async_client.get("/health")
        data = response.json()
        assert "database" in data
        # Sin DB de test conectada → database: down (degradado, no crash)
        assert data["database"] in ("up", "down")

    async def test_health_response_is_json(self, async_client: AsyncClient) -> None:
        """La respuesta es JSON válido."""
        response = await async_client.get("/health")
        assert response.headers["content-type"].startswith("application/json")
