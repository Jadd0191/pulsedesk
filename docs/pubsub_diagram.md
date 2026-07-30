# Diagrama de Flujo Pub/Sub - PulseDesk RAD

## Arquitectura de Comunicación Desacoplada
┌─────────────────────────────────────────────────────────────────────────────┐
│ SISTEMA PULSEDESK RAD │
│ │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│ │ Fuentes de │ │ Fuentes de │ │ Fuentes de │ │
│ │ Datos │ │ Datos │ │ Datos │ │
│ │ │ │ │ │ │ │
│ │ HeartbeatSource │ │TelemetryFileSource│ │ AlertsAPISource │ │
│ │ │ │ │ │ │ │
│ └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘ │
│ │ │ │ │
│ │ Publican eventos │ Publican eventos │ Publican │
│ │ en el bus │ en el bus │ eventos │
│ ▼ ▼ ▼ │
│ ┌──────────────────────────────────────────────────────────────────────┐ │
│ │ │ │
│ │ EVENT BUS (Pub/Sub) │ │
│ │ │ │
│ │ ┌─────────────────────────────────────────────────────────────┐ │ │
│ │ │ Suscripciones: │ │ │
│ │ │ - TelemetryReceived → TelemetryPanel, StateStore │ │ │
│ │ │ - AlertRaised → AlertsPanel, StateStore │ │ │
│ │ │ - SystemHealthCheck → StatusPanel, StateStore │ │ │
│ │ │ - SourceFailed → StatusPanel, StateStore │ │ │
│ │ │ - ShutdownRequested → EventLoop, Sources │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │ │ │
│ └──────────────────────────────────────────────────────────────────────┘ │
│ │ │ │ │
│ │ Entrega eventos │ Entrega eventos │ Entrega │
│ ▼ ▼ ▼ │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│ │ Consumidores │ │ Consumidores │ │ Consumidores │ │
│ │ │ │ │ │ │ │
│ │ TelemetryPanel │ │ AlertsPanel │ │ StatusPanel │ │
│ │ │ │ │ │ │ │
│ │ StateStore │ │ StateStore │ │ StateStore │ │
│ │ │ │ │ │ │ │
│ │ EventLoop │ │ EventLoop │ │ EventLoop │ │
│ └──────────────────┘ └──────────────────┘ └──────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────────────────┘


## Flujo de Eventos

### 1. Publicación de Eventos

```python
# Ejemplo: HeartbeatSource publica un evento
event = SystemHealthCheck(
    status="healthy",
    components_status={"heartbeat": "running"},
    uptime_seconds=10.0
)
event_bus.publish(event)