"""
Core - Núcleo del sistema PulseDesk RAD

Este paquete contiene los componentes fundamentales del sistema:
- events: Catálogo de eventos
- event_bus: Bus de eventos (por implementar)
- loop: Event loop (por implementar)
- state: Store de estado (por implementar)
"""

from .events import (
    Event,
    TelemetryReceived,
    TelemetryBatchReceived,
    AlertRaised,
    AlertAcknowledged,
    AlertCleared,
    SourceStarted,
    SourceStopped,
    SourceFailed,
    SourceRecovered,
    StateChanged,
    SystemHealthCheck,
    ShutdownRequested,
    ShutdownComplete,
    SystemInitialized,
    UIAction,
    UserPreferenceChanged,
    TaskStarted,
    TaskCompleted,
    TaskFailed,
    AlertSeverity,
    SourceStatus,
    SystemState,
)

__all__ = [
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
]