"""
Pruebas para el store de estado.
"""

import pytest
import threading
import time
from datetime import datetime

from core.state import StateStore, VehicleState, AlertState, SourceState
from core.events import (
    SystemState,
    SourceStatus,
    TelemetryReceived,
    AlertRaised,
    AlertSeverity
)


class TestStateStore:
    """Pruebas para el store de estado."""
    
    @pytest.fixture
    def store(self):
        """Crea un store limpio para cada prueba."""
        return StateStore()
    
    def test_initial_state(self, store):
        """Verifica el estado inicial."""
        assert store.system_state == SystemState.INITIALIZING
        assert store.uptime == 0.0
        assert store.get_vehicle_count() == 0
        assert store.get_alert_count() == 0
    
    def test_set_system_state(self, store):
        """Verifica cambio de estado del sistema."""
        store.set_system_state(SystemState.RUNNING, reason="Test")
        assert store.system_state == SystemState.RUNNING
    
    def test_update_vehicle(self, store):
        """Verifica actualización de vehículo."""
        event = TelemetryReceived(
            vehicle_id="V-001",
            speed=75.5,
            temperature=85.2,
            latitude=19.4326,
            longitude=-99.1332,
            engine_status=True,
            fuel_level=72.3,
            timestamp_data=datetime.now()
        )
        
        store.update_vehicle(event)
        
        vehicle = store.get_vehicle("V-001")
        assert vehicle is not None
        assert vehicle.speed == 75.5
        assert vehicle.temperature == 85.2
        assert vehicle.engine_status is True
    
    def test_multiple_vehicles(self, store):
        """Verifica múltiples vehículos."""
        for i in range(1, 4):
            event = TelemetryReceived(
                vehicle_id=f"V-{i:03d}",
                speed=50.0 + i * 10,
                temperature=70.0 + i * 5,
                latitude=19.4,
                longitude=-99.1,
                engine_status=True,
                fuel_level=80.0 - i * 5,
                timestamp_data=datetime.now()
            )
            store.update_vehicle(event)
        
        assert store.get_vehicle_count() == 3
        vehicles = store.get_all_vehicles()
        assert len(vehicles) == 3
    
    def test_add_alert(self, store):
        """Verifica adición de alertas."""
        event = AlertRaised(
            alert_id="A-001",
            severity=AlertSeverity.CRITICAL,
            vehicle_id="V-001",
            message="Engine overheating",
            category="mechanical",
            timestamp_data=datetime.now()
        )
        
        store.add_alert(event)
        
        alerts = store.get_alerts()
        assert len(alerts) == 1
        assert alerts[0].alert_id == "A-001"
        assert alerts[0].severity == "critical"
    
    def test_acknowledge_alert(self, store):
        """Verifica reconocimiento de alertas."""
        event = AlertRaised(
            alert_id="A-001",
            severity=AlertSeverity.CRITICAL,
            vehicle_id="V-001",
            message="Engine overheating",
            category="mechanical",
            timestamp_data=datetime.now()
        )
        
        store.add_alert(event)
        
        result = store.acknowledge_alert("A-001")
        assert result is True
        
        alerts = store.get_alerts()
        assert alerts[0].acknowledged is True
    
    def test_update_source(self, store):
        """Verifica actualización de fuentes."""
        store.update_source("Heartbeat", SourceStatus.RUNNING)
        
        source = store.get_source_status("Heartbeat")
        assert source is not None
        assert source.status == SourceStatus.RUNNING
    
    def test_source_error_count(self, store):
        """Verifica contador de errores de fuentes."""
        store.update_source("Telemetry", SourceStatus.ERROR, "Connection lost")
        
        source = store.get_source_status("Telemetry")
        assert source.error_count == 1
        assert source.last_error == "Connection lost"
    
    def test_callback_notification(self, store):
        """Verifica notificaciones de callbacks."""
        notifications = []
        
        def callback(event_type, data):
            notifications.append((event_type, data))
        
        store.add_callback(callback)
        
        store.set_system_state(SystemState.RUNNING)
        
        event = TelemetryReceived(
            vehicle_id="V-001",
            speed=75.5,
            temperature=85.2,
            latitude=19.4326,
            longitude=-99.1332,
            engine_status=True,
            fuel_level=72.3,
            timestamp_data=datetime.now()
        )
        store.update_vehicle(event)
        
        assert len(notifications) >= 2
    
    def test_thread_safety(self, store):
        """Verifica que el store es thread-safe."""
        def update_vehicles():
            for i in range(10):
                event = TelemetryReceived(
                    vehicle_id=f"V-{i:03d}",
                    speed=50.0,
                    temperature=70.0,
                    latitude=19.4,
                    longitude=-99.1,
                    engine_status=True,
                    fuel_level=80.0,
                    timestamp_data=datetime.now()
                )
                store.update_vehicle(event)
        
        threads = [threading.Thread(target=update_vehicles) for _ in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert store.get_vehicle_count() == 10
    
    def test_get_summary(self, store):
        """Verifica el resumen del estado."""
        store.set_system_state(SystemState.RUNNING)
        store.set_uptime(10.5)
        
        event = TelemetryReceived(
            vehicle_id="V-001",
            speed=75.5,
            temperature=85.2,
            latitude=19.4326,
            longitude=-99.1332,
            engine_status=True,
            fuel_level=72.3,
            timestamp_data=datetime.now()
        )
        store.update_vehicle(event)
        
        summary = store.get_summary()
        assert summary["system_state"] == "running"
        assert summary["uptime"] == 10.5
        assert summary["vehicles"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])