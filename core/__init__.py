"""
Core - Núcleo del sistema PulseDesk RAD

Este paquete contiene los componentes fundamentales del sistema:
- events: Catálogo de eventos
- loop: Event loop y ciclo de vida
- sources: Fuentes de datos
- state: Store de estado (por implementar)
- event_bus: Bus de eventos (por implementar)
"""

from .events import *
from .loop import EventLoop
from .sources import Source, HeartbeatSource

__all__ = [
    # Eventos
    'Event',
    'TelemetryReceived',
    'TelemetryBatchReceived',
    'AlertRaised',
    'AlertAcknowledged',
    'AlertCleared',
    'SourceStarted',
    'SourceStopped',
    'SourceFailed',
    'SourceRecovered',
    'StateChanged',
    'SystemHealthCheck',
    'ShutdownRequested',
    'ShutdownComplete',
    'SystemInitialized',
    'UIAction',
    'UserPreferenceChanged',
    'TaskStarted',
    'TaskCompleted',
    'TaskFailed',
    'AlertSeverity',
    'SourceStatus',
    'SystemState',
    # Loop
    'EventLoop',
    # Sources
    'Source',
    'HeartbeatSource',
]