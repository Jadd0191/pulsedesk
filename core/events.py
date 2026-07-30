"""
Catálogo de Eventos - PulseDesk RAD

Este módulo define todos los eventos del sistema como dataclasses tipadas.
Cada evento tiene un payload específico y está documentado con su emisor,
consumidor y propósito.

Seguimiento de eventos:
- Todos los eventos heredan de Event base
- Los eventos son inmutables (frozen=True)
- Cada evento tiene timestamp automático
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


# ============================================================================
# Enumeraciones para tipado seguro
# ============================================================================

class AlertSeverity(Enum):
    """Niveles de severidad para alertas"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SourceStatus(Enum):
    """Estados posibles para una fuente de datos"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"


class SystemState(Enum):
    """Estados generales del sistema"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


# ============================================================================
# Evento Base
# ============================================================================

@dataclass(frozen=True)
class Event:
    """
    Clase base para todos los eventos del sistema.
    Todo evento debe tener un timestamp y un ID único.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# Eventos de Telemetría
# ============================================================================

@dataclass(frozen=True, kw_only=True)
class TelemetryReceived(Event):
    """
    Evento emitido cuando se reciben datos de telemetría de un vehículo.
    
    Emisor: TelemetryFileSource
    Consumidor: TelemetryPanel, StateStore
    Payload: Datos del vehículo incluyendo posición y estado
    """
    vehicle_id: str
    speed: float           # km/h
    temperature: float     # °C
    latitude: float
    longitude: float
    engine_status: bool
    fuel_level: float      # 0-100%
    timestamp_data: datetime  # Timestamp de los datos (no del evento)


@dataclass(frozen=True, kw_only=True)
class TelemetryBatchReceived(Event):
    """
    Evento emitido cuando se recibe un lote de datos de telemetría.
    
    Emisor: TelemetryFileSource (agrupación)
    Consumidor: TelemetryPanel, StateStore
    Payload: Lista de datos de telemetría
    """
    vehicles_data: List[Dict[str, Any]]
    count: int
    source: str


# ============================================================================
# Eventos de Alertas
# ============================================================================

@dataclass(frozen=True, kw_only=True)
class AlertRaised(Event):
    """
    Evento emitido cuando se genera una nueva alerta.
    
    Emisor: AlertsAPISource
    Consumidor: AlertsPanel, StateStore
    Payload: Información de la alerta generada
    """
    alert_id: str
    severity: AlertSeverity
    vehicle_id: str
    message: str
    category: str
    timestamp_data: datetime
    acknowledged: bool = False


@dataclass(frozen=True, kw_only=True)
class AlertAcknowledged(Event):
    """
    Evento emitido cuando un operador reconoce una alerta.
    
    Emisor: UI (AlertsPanel)
    Consumidor: StateStore
    Payload: ID de la alerta reconocida
    """
    alert_id: str
    acknowledged_by: str = "operator"
    timestamp_ack: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True, kw_only=True)
class AlertCleared(Event):
    """
    Evento emitido cuando una alerta se resuelve y se limpia.
    
    Emisor: UI (AlertsPanel) o source automático
    Consumidor: StateStore
    Payload: ID de la alerta limpiada
    """
    alert_id: str
    reason: str = "resolved"


# ============================================================================
# Eventos de Fuentes de Datos
# ============================================================================

@dataclass(frozen=True, kw_only=True)
class SourceStarted(Event):
    """
    Evento emitido cuando una fuente de datos inicia correctamente.
    
    Emisor: Source (TelemetryFileSource, AlertsAPISource, HeartbeatSource)
    Consumidor: StateStore, EventLoop, UI
    Payload: Información de la fuente iniciada
    """
    source_name: str
    source_type: str
    status: SourceStatus = SourceStatus.RUNNING


@dataclass(frozen=True, kw_only=True)
class SourceStopped(Event):
    """
    Evento emitido cuando una fuente de datos se detiene correctamente.
    
    Emisor: Source
    Consumidor: StateStore, EventLoop
    Payload: Información de la fuente detenida
    """
    source_name: str
    reason: Optional[str] = None


@dataclass(frozen=True, kw_only=True)
class SourceFailed(Event):
    """
    Evento emitido cuando una fuente de datos falla.
    
    Emisor: Source
    Consumidor: StateStore, UI (indicador de estado)
    Payload: Información del error
    """
    source_name: str
    error_message: str
    retry_count: int = 0
    max_retries: int = 3
    is_critical: bool = False


@dataclass(frozen=True, kw_only=True)
class SourceRecovered(Event):
    """
    Evento emitido cuando una fuente se recupera de un error.
    
    Emisor: Source
    Consumidor: StateStore, UI
    Payload: Información de recuperación
    """
    source_name: str
    recovery_time: float


# ============================================================================
# Eventos de Estado del Sistema
# ============================================================================

@dataclass(frozen=True, kw_only=True)
class StateChanged(Event):
    """
    Evento emitido cuando cambia el estado general del sistema.
    
    Emisor: StateStore
    Consumidor: UI, EventLoop
    Payload: Nuevo estado del sistema
    """
    old_state: SystemState
    new_state: SystemState
    reason: Optional[str] = None


@dataclass(frozen=True, kw_only=True)
class SystemHealthCheck(Event):
    """
    Evento de health check periódico.
    
    Emisor: HeartbeatSource
    Consumidor: StateStore, UI
    Payload: Estado de salud del sistema
    """
    status: str
    components_status: Dict[str, str]
    uptime_seconds: float


# ============================================================================
# Eventos de Ciclo de Vida
# ============================================================================

@dataclass(frozen=True, kw_only=True)
class ShutdownRequested(Event):
    """
    Evento emitido cuando se solicita el apagado del sistema.
    
    Emisor: UI (botón cerrar) o Signal (Ctrl+C)
    Consumidor: EventLoop, Sources
    Payload: Tipo y razón del apagado
    """
    shutdown_type: str
    reason: Optional[str] = None
    timeout_seconds: float = 5.0


@dataclass(frozen=True, kw_only=True)
class ShutdownComplete(Event):
    """
    Evento emitido cuando el apagado del sistema se completa.
    
    Emisor: EventLoop
    Consumidor: UI, logs
    Payload: Resultado del apagado
    """
    success: bool
    duration_seconds: float
    errors: List[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class SystemInitialized(Event):
    """
    Evento emitido cuando el sistema completa su inicialización.
    
    Emisor: EventLoop
    Consumidor: UI, Sources
    Payload: Configuración del sistema
    """
    config: Dict[str, Any]
    start_time: datetime = field(default_factory=datetime.now)


# ============================================================================
# Eventos de UI y Usuario
# ============================================================================

@dataclass(frozen=True, kw_only=True)
class UIAction(Event):
    """
    Evento genérico para acciones de UI.
    
    Emisor: UI (widgets)
    Consumidor: StateStore, Workers
    Payload: Acción del usuario
    """
    action: str
    target: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class UserPreferenceChanged(Event):
    """
    Evento emitido cuando el usuario cambia preferencias.
    
    Emisor: UI (settings panel)
    Consumidor: UI, StateStore
    Payload: Preferencias cambiadas
    """
    preference_name: str
    old_value: Any
    new_value: Any


# ============================================================================
# Eventos de Workers y Tareas
# ============================================================================

@dataclass(frozen=True, kw_only=True)
class TaskStarted(Event):
    """
    Evento emitido cuando una tarea en background inicia.
    
    Emisor: Worker
    Consumidor: UI, StateStore
    Payload: Información de la tarea
    """
    task_id: str
    task_name: str
    description: str


@dataclass(frozen=True, kw_only=True)
class TaskCompleted(Event):
    """
    Evento emitido cuando una tarea en background finaliza.
    
    Emisor: Worker
    Consumidor: UI, StateStore
    Payload: Resultado de la tarea
    """
    task_id: str
    task_name: str
    success: bool
    duration_seconds: float
    result: Optional[Any] = None


@dataclass(frozen=True, kw_only=True)
class TaskFailed(Event):
    """
    Evento emitido cuando una tarea en background falla.
    
    Emisor: Worker
    Consumidor: UI, StateStore
    Payload: Error de la tarea
    """
    task_id: str
    task_name: str
    error_message: str
    retry_count: int = 0


# ============================================================================
# Utilidades para testing
# ============================================================================

def get_event_metadata(event: Event) -> Dict[str, Any]:
    """Obtiene metadatos de un evento."""
    return {
        "event_id": event.event_id,
        "event_type": event.__class__.__name__,
        "timestamp": event.timestamp.isoformat(),
    }


# ============================================================================
# Ejemplo de uso
# ============================================================================

if __name__ == "__main__":
    # Ejemplo de creación de un evento
    telemetry = TelemetryReceived(
        vehicle_id="V-001",
        speed=75.5,
        temperature=85.2,
        latitude=19.4326,
        longitude=-99.1332,
        engine_status=True,
        fuel_level=72.3,
        timestamp_data=datetime.now()
    )
    
    print(f"Evento creado: {telemetry.__class__.__name__}")
    print(f"ID: {telemetry.event_id}")
    print(f"Timestamp: {telemetry.timestamp}")
    print(f"Datos: vehicle_id={telemetry.vehicle_id}, speed={telemetry.speed}km/h")