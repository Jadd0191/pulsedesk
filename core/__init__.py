"""
Core - Núcleo del sistema PulseDesk RAD

Este paquete contiene los componentes fundamentales del sistema:
- events: Catálogo de eventos
- event_bus: Bus de eventos propio
- loop: Event loop y ciclo de vida
- sources: Fuentes de datos
- state: Store de estado (por implementar)
"""

from .events import *
from .event_bus import EventBus, subscribe_to
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
    # EventBus
    'EventBus',
    'subscribe_to',
    # Loop
    'EventLoop',
    # Sources
    'Source',
    'HeartbeatSource',
]