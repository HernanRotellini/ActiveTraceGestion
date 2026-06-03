"""Integraciones con sistemas externos."""

from app.integrations.moodle_ws import MoodleClient, MoodleConfig, MoodleError

__all__ = [
    "MoodleClient",
    "MoodleConfig",
    "MoodleError",
]