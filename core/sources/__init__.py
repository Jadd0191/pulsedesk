"""
Fuentes de datos para PulseDesk RAD.

Cada fuente implementa la interfaz Source y produce eventos.
"""

from .base import Source
from .heartbeat import HeartbeatSource

__all__ = [
    'Source',
    'HeartbeatSource',
]