# =============================================================================
# activia-trace — Dockerfile multi-stage (convención Easypanel)
# =============================================================================
# Etapa 1: builder — instala dependencias
# Etapa 2: runtime — imagen mínima Python 3.13-slim con solo lo necesario
# =============================================================================

# ── Stage 1: Builder ───────────────────────────────────────────
FROM python:3.13-alpine AS builder

WORKDIR /build

# Instalar dependencias del sistema necesarias para compilar wheels
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copiar solo pyproject.toml para cachear capa de dependencias
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# ── Stage 2: Runtime ───────────────────────────────────────────
FROM python:3.13-alpine AS runtime

# Crear usuario no-root
RUN addgroup -S trace && adduser -S trace -G trace

WORKDIR /app

# Copiar solo el entorno instalado desde builder (sin toolchain de build)
COPY --from=builder /install /usr/local

# Copiar código de la aplicación
COPY app/ app/
COPY alembic.ini .
COPY alembic/ alembic/
COPY tests/ tests/
COPY pyproject.toml .

ARG INSTALL_TEST_DEPS=false
RUN if [ "$INSTALL_TEST_DEPS" = "true" ]; then \
        pip install --no-cache-dir "pytest>=8.3.0" "pytest-asyncio>=0.24.0" "httpx>=0.28.0" "coverage>=7.6.0"; \
    fi

# Pydantic v2: desactivar Rust para reducir tamaño (opcional)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

USER trace

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
