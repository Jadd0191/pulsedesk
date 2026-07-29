# Tabla de Eventos - PulseDesk RAD

## Resumen

Esta tabla documenta todos los eventos del sistema, incluyendo quién los emite, quién los consume y qué información transportan.

---

## Eventos de Telemetría

| Evento | Emisor | Consumidor | Payload |
|--------|--------|------------|---------|
| **TelemetryReceived** | TelemetryFileSource | TelemetryPanel, StateStore | `vehicle_id`: str<br>`speed`: float (km/h)<br>`temperature`: float (°C)<br>`latitude`: float<br>`longitude`: float<br>`engine_status`: bool<br>`fuel_level`: float (0-100%)<br>`timestamp_data`: datetime |
| **TelemetryBatchReceived** | TelemetryFileSource (agrupación) | TelemetryPanel, StateStore | `vehicles_data`: List[Dict]<br>`count`: int<br>`source`: str |

---

## Eventos de Alertas

| Evento | Emisor | Consumidor | Payload |
|--------|--------|------------|---------|
| **AlertRaised** | AlertsAPISource | AlertsPanel, StateStore | `alert_id`: str<br>`severity`: AlertSeverity<br>`vehicle_id`: str<br>`message`: str<br>`category`: str<br>`timestamp_data`: datetime<br>`acknowledged`: bool (default: False) |
| **AlertAcknowledged** | UI (AlertsPanel) | StateStore | `alert_id`: str<br>`acknowledged_by`: str (default: "operator")<br>`timestamp_ack`: datetime |
| **AlertCleared** | UI (AlertsPanel) / Source | StateStore | `alert_id`: str<br>`reason`: str (default: "resolved") |

---

## Eventos de Fuentes de Datos

| Evento | Emisor | Consumidor | Payload |
|--------|--------|------------|---------|
| **SourceStarted** | TelemetryFileSource, AlertsAPISource, HeartbeatSource | StateStore, EventLoop, UI | `source_name`: str<br>`source_type`: str<br>`status`: SourceStatus |
| **SourceStopped** | TelemetryFileSource, AlertsAPISource, HeartbeatSource | StateStore, EventLoop | `source_name`: str<br>`reason`: Optional[str] |
| **SourceFailed** | TelemetryFileSource, AlertsAPISource, HeartbeatSource | StateStore, UI | `source_name`: str<br>`error_message`: str<br>`retry_count`: int<br>`max_retries`: int<br>`is_critical`: bool |
| **SourceRecovered** | TelemetryFileSource, AlertsAPISource, HeartbeatSource | StateStore, UI | `source_name`: str<br>`recovery_time`: float (segundos) |

---

## Eventos de Estado del Sistema

| Evento | Emisor | Consumidor | Payload |
|--------|--------|------------|---------|
| **StateChanged** | StateStore | UI, EventLoop | `old_state`: SystemState<br>`new_state`: SystemState<br>`reason`: Optional[str] |
| **SystemHealthCheck** | HeartbeatSource | StateStore, UI | `status`: str ("healthy", "degraded", "unhealthy")<br>`components_status`: Dict[str, str]<br>`uptime_seconds`: float |

---

## Eventos de Ciclo de Vida

| Evento | Emisor | Consumidor | Payload |
|--------|--------|------------|---------|
| **ShutdownRequested** | UI / Signal | EventLoop, Sources | `shutdown_type`: str ("graceful", "forced")<br>`reason`: Optional[str]<br>`timeout_seconds`: float (default: 5.0) |
| **ShutdownComplete** | EventLoop | UI, logs | `success`: bool<br>`duration_seconds`: float<br>`errors`: List[str] |
| **SystemInitialized** | EventLoop | UI, Sources | `config`: Dict[str, Any]<br>`start_time`: datetime |

---

## Eventos de UI y Usuario

| Evento | Emisor | Consumidor | Payload |
|--------|--------|------------|---------|
| **UIAction** | UI (widgets) | StateStore, Workers | `action`: str<br>`target`: str<br>`params`: Dict[str, Any] |
| **UserPreferenceChanged** | UI (settings panel) | UI, StateStore | `preference_name`: str<br>`old_value`: Any<br>`new_value`: Any |

---

## Eventos de Workers y Tareas

| Evento | Emisor | Consumidor | Payload |
|--------|--------|------------|---------|
| **TaskStarted** | Worker | UI, StateStore | `task_id`: str<br>`task_name`: str<br>`description`: str |
| **TaskCompleted** | Worker | UI, StateStore | `task_id`: str<br>`task_name`: str<br>`success`: bool<br>`duration_seconds`: float<br>`result`: Optional[Any] |
| **TaskFailed** | Worker | UI, StateStore | `task_id`: str<br>`task_name`: str<br>`error_message`: str<br>`retry_count`: int |

---

## Diagrama de Flujo de Eventos
┌─────────────────┐
│ Fuentes de │
│ Datos │
│ ┌───────────┐ │
│ │Telemetry │──┼──→ TelemetryReceived
│ │FileSource │ │
│ └───────────┘ │
│ ┌───────────┐ │
│ │AlertsAPI │──┼──→ AlertRaised
│ │Source │ │
│ └───────────┘ │
│ ┌───────────┐ │
│ │Heartbeat │──┼──→ SystemHealthCheck
│ │Source │ │
│ └───────────┘ │
└─────────────────┘
│
▼
┌─────────────────┐
│ Event Bus │
│ (Publish/ │
│ Subscribe) │
└─────────────────┘
│
▼
┌─────────────────────────────────────┐
│ Consumidores │
│ ┌──────────────┐ ┌───────────┐ │
│ │TelemetryPanel│ │StateStore │ │
│ └──────────────┘ └───────────┘ │
│ ┌──────────────┐ ┌───────────┐ │
│ │AlertsPanel │ │EventLoop │ │
│ └──────────────┘ └───────────┘ │
│ ┌──────────────┐ │
│ │StatusIndicator│ │
│ └──────────────┘ │
└─────────────────────────────────────┘


---

## Jerarquía de Eventos
Event (base)
├── TelemetryReceived
├── TelemetryBatchReceived
├── AlertRaised
├── AlertAcknowledged
├── AlertCleared
├── SourceStarted
├── SourceStopped
├── SourceFailed
├── SourceRecovered
├── StateChanged
├── SystemHealthCheck
├── ShutdownRequested
├── ShutdownComplete
├── SystemInitialized
├── UIAction
├── UserPreferenceChanged
├── TaskStarted
├── TaskCompleted
└── TaskFailed


---

## Enums Utilizados

### AlertSeverity
- `INFO`: Información general
- `WARNING`: Advertencia
- `ERROR`: Error no crítico
- `CRITICAL`: Error crítico que requiere atención inmediata

### SourceStatus
- `RUNNING`: Fuente operando normalmente
- `STOPPED`: Fuente detenida voluntariamente
- `ERROR`: Fuente en estado de error
- `CONNECTING`: Fuente intentando conectar
- `DISCONNECTED`: Fuente desconectada

### SystemState
- `INITIALIZING`: Sistema iniciándose
- `RUNNING`: Sistema operando normalmente
- `DEGRADED`: Sistema con algunas fallas
- `ERROR`: Sistema en estado de error
- `SHUTTING_DOWN`: Sistema apagándose
- `SHUTDOWN`: Sistema apagado

---

## Buenas Prácticas

1. **Inmutabilidad**: Todos los eventos son `frozen=True`, no se pueden modificar después de creados.

2. **Timestamp automático**: Cada evento tiene un timestamp automático al crearse.

3. **ID único**: Cada evento tiene un ID único generado automáticamente.

4. **Payload tipado**: Todos los payloads usan tipos estáticos para mayor seguridad.

5. **Eventos minimalistas**: Cada evento transporta solo la información necesaria.

6. **Eventos independientes**: Los eventos no contienen lógica de negocio, solo datos.

---

## Validación de Eventos

```python
# Ejemplo de validación en handlers
def handle_telemetry(event: TelemetryReceived):
    if event.speed < 0 or event.speed > 300:
        raise ValueError("Velocidad fuera de rango")
    if event.temperature < -50 or event.temperature > 150:
        raise ValueError("Temperatura fuera de rango")
    # Procesar evento válido...