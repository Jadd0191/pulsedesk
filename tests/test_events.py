"""
Pruebas para el catálogo de eventos.

Verifica que:
1. Los eventos se crean correctamente
2. Los payloads están tipados
3. Los eventos son inmutables
4. Los timestamps y IDs se generan automáticamente
"""

import pytest
from datetime import datetime
from core.events import (
    Event,
    TelemetryReceived,
    AlertRaised,
    AlertSeverity,
    SourceFailed,
    SourceStatus,
    StateChanged,
    SystemState,
    ShutdownRequested,
    get_event_metadata,
)


class TestEvents:
    """Pruebas para los eventos del sistema"""
    
    def test_event_creation(self):
        """Verifica que un evento base se crea correctamente"""
        event = Event()
        assert event.event_id is not None
        assert isinstance(event.timestamp, datetime)
        assert isinstance(event.event_id, str)
    
    def test_event_with_custom_id(self):
        """Verifica que se puede pasar un ID personalizado"""
        custom_id = "custom-123"
        event = Event(event_id=custom_id)
        assert event.event_id == custom_id
    
    def test_event_immutable(self):
        """Verifica que los eventos son inmutables (frozen)"""
        event = Event()
        with pytest.raises(Exception):  # dataclass frozen
            event.event_id = "new-id"  # type: ignore
    
    def test_telemetry_event(self):
        """Verifica la creación de eventos de telemetría"""
        now = datetime.now()
        telemetry = TelemetryReceived(
            vehicle_id="V-001",
            speed=75.5,
            temperature=85.2,
            latitude=19.4326,
            longitude=-99.1332,
            engine_status=True,
            fuel_level=72.3,
            timestamp_data=now
        )
        
        assert telemetry.vehicle_id == "V-001"
        assert telemetry.speed == 75.5
        assert telemetry.temperature == 85.2
        assert telemetry.latitude == 19.4326
        assert telemetry.longitude == -99.1332
        assert telemetry.engine_status is True
        assert telemetry.fuel_level == 72.3
        assert telemetry.timestamp_data == now
        assert isinstance(telemetry.timestamp, datetime)
    
    def test_alert_event(self):
        """Verifica la creación de eventos de alerta"""
        now = datetime.now()
        alert = AlertRaised(
            alert_id="A-001",
            severity=AlertSeverity.CRITICAL,
            vehicle_id="V-005",
            message="Engine overheating",
            category="mechanical",
            timestamp_data=now
        )
        
        assert alert.alert_id == "A-001"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.vehicle_id == "V-005"
        assert alert.message == "Engine overheating"
        assert alert.category == "mechanical"
        assert alert.timestamp_data == now
        assert alert.acknowledged is False
    
    def test_source_failed_event(self):
        """Verifica la creación de eventos de falla de fuente"""
        failed = SourceFailed(
            source_name="TelemetryFile",
            error_message="File not found",
            retry_count=2,
            max_retries=3,
            is_critical=True
        )
        
        assert failed.source_name == "TelemetryFile"
        assert failed.error_message == "File not found"
        assert failed.retry_count == 2
        assert failed.max_retries == 3
        assert failed.is_critical is True
    
    def test_state_changed_event(self):
        """Verifica la creación de eventos de cambio de estado"""
        state_change = StateChanged(
            old_state=SystemState.INITIALIZING,
            new_state=SystemState.RUNNING,
            reason="Initialization complete"
        )
        
        assert state_change.old_state == SystemState.INITIALIZING
        assert state_change.new_state == SystemState.RUNNING
        assert state_change.reason == "Initialization complete"
    
    def test_shutdown_requested_event(self):
        """Verifica la creación de eventos de apagado"""
        shutdown = ShutdownRequested(
            shutdown_type="graceful",
            reason="User requested",
            timeout_seconds=10.0
        )
        
        assert shutdown.shutdown_type == "graceful"
        assert shutdown.reason == "User requested"
        assert shutdown.timeout_seconds == 10.0
    
    def test_event_metadata(self):
        """Verifica que la metadata de eventos funciona"""
        event = Event()
        metadata = get_event_metadata(event)
        
        assert metadata["event_id"] == event.event_id
        assert metadata["event_type"] == "Event"
        assert "timestamp" in metadata
        assert isinstance(metadata["timestamp"], str)
    
    def test_event_inheritance(self):
        """Verifica que todos los eventos heredan de Event"""
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
        
        assert isinstance(telemetry, Event)
        assert hasattr(telemetry, 'event_id')
        assert hasattr(telemetry, 'timestamp')
    
    def test_enum_values(self):
        """Verifica los valores de los enums"""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"
        
        assert SourceStatus.RUNNING.value == "running"
        assert SourceStatus.STOPPED.value == "stopped"
        assert SourceStatus.ERROR.value == "error"
        
        assert SystemState.INITIALIZING.value == "initializing"
        assert SystemState.RUNNING.value == "running"
        assert SystemState.SHUTDOWN.value == "shutdown"
    
    def test_event_with_list_payload(self):
        """Verifica eventos con payloads de lista"""
        # Esto sería para TelemetryBatchReceived cuando se implemente
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])