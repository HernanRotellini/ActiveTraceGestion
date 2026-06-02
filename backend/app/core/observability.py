"""Instrumentación OpenTelemetry para FastAPI.

Configura la instrumentación de trazas para la aplicación FastAPI usando
OpenTelemetry. Activable por entorno; no bloquea el arranque si no hay
un backend de exportación configurado.
"""

import logging

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import Settings

logger = logging.getLogger(__name__)


def setup_observability(settings: Settings, app: object) -> None:
    """Inicializa OpenTelemetry e instrumenta la app FastAPI.

    Args:
        settings: Configuración del proyecto (para OTEL_SERVICE_NAME y endpoint).
        app: Instancia de la aplicación FastAPI a instrumentar.

    Nota: Si no hay OTEL_EXPORTER_OTLP_ENDPOINT configurado, la app
    igual arranca — solo no exporta trazas a un backend externo.
    """
    resource = Resource.create({
        "service.name": settings.OTEL_SERVICE_NAME,
    })

    provider = TracerProvider(resource=resource)

    # Configurar exporter solo si se proporcionó un endpoint
    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        try:
            # Import lazy: el paquete opentelemetry-exporter-otlp-proto-http
            # no es obligatorio si no se configura telemetría.
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # noqa: PLC0415
                OTLPSpanExporter,
            )
            otlp_exporter = OTLPSpanExporter(
                endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            )
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info("OTLP exporter configurado en %s", settings.OTEL_EXPORTER_OTLP_ENDPOINT)
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo configurar OTLP exporter: %s", exc)

    trace.set_tracer_provider(provider)

    # Instrumentar FastAPI
    FastAPIInstrumentor.instrument_app(app)

    logger.info(
        "OpenTelemetry inicializado para '%s'",
        settings.OTEL_SERVICE_NAME,
    )
