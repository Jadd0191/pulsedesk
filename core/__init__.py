"""
Core - Núcleo del sistema PulseDesk RAD
"""

from .events import *
from .event_bus import EventBus, subscribe_to
from .loop import EventLoop
from .sources import Source, HeartbeatSource, TelemetryFileSource
from .state import StateStore, VehicleState, AlertState, SourceState

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
    'TelemetryFileSource',
    # State
    'StateStore',
    'VehicleState',
    'AlertState',
    'SourceState',
]