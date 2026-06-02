"""Logging estructurado en JSON.

Configura el logger raíz para emitir logs en formato JSON (una línea por evento)
con campos timestamp, level y message. Nunca se registran secretos ni PII en claro.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatea registros de log como JSON en una línea."""

    def format(self, record: logging.LogRecord) -> str:
        """Convierte un LogRecord a JSON string."""
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Incluir excepción si existe
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Incluir extra data del record
        for key, value in record.__dict__.items():
            if key not in (
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "message",
                "module",
                "msecs",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ):
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def configure_json_logging(level: int = logging.INFO) -> None:
    """Configura el logger raíz con formato JSON.

    Args:
        level: Nivel de logging (default: INFO). Usar logging.DEBUG para desarrollo.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Limpiar handlers existentes para evitar duplicados
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    # Silenciar loggers ruidosos de terceros si es necesario
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
