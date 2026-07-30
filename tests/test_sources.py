"""
Pruebas para las fuentes de datos.

Verifica:
1. Creación de fuentes
2. Generación de eventos
3. Manejo de errores
"""

import pytest
import asyncio
from core.sources.telemetry_file import TelemetryFileSource
from core.sources.heartbeat import HeartbeatSource
from core.events import TelemetryReceived, SystemHealthCheck


class TestSources:
    """Pruebas para las fuentes de datos"""
    
    @pytest.mark.asyncio
    async def test_telemetry_source_creation(self):
        """Verifica la creación de la fuente de telemetría"""
        source = TelemetryFileSource(name="TestTelemetry", vehicles=3)
        assert source.name == "TestTelemetry"
        assert source.vehicles == 3
        assert len(source._vehicle_data) == 3
    
    @pytest.mark.asyncio
    async def test_telemetry_source_start_stop(self):
        """Verifica inicio y detención de la fuente de telemetría"""
        source = TelemetryFileSource(vehicles=2)
        
        await source.start()
        assert source.is_running is True
        
        await source.stop()
        assert source.is_running is False
    
    @pytest.mark.asyncio
    async def test_telemetry_source_generates_events(self):
        """Verifica que la fuente genera eventos de telemetría"""
        source = TelemetryFileSource(vehicles=2, interval=0.1)
        await source.start()
        
        events = []
        async for event in source:
            events.append(event)
            if len(events) >= 3:
                break
        
        assert len(events) == 3
        for event in events:
            assert isinstance(event, TelemetryReceived)
            assert event.vehicle_id.startswith("V-")
            assert event.speed >= 0
            assert event.temperature >= 0
        
        await source.stop()
    
    @pytest.mark.asyncio
    async def test_heartbeat_source_generates_events(self):
        """Verifica que la fuente de latido genera eventos"""
        source = HeartbeatSource(interval=0.1)
        await source.start()
        
        events = []
        async for event in source:
            events.append(event)
            if len(events) >= 3:
                break
        
        assert len(events) == 3
        for event in events:
            assert isinstance(event, SystemHealthCheck)
            assert event.status == "healthy"
        
        await source.stop()
    
    @pytest.mark.asyncio
    async def test_telemetry_source_vehicle_data(self):
        """Verifica que la fuente genera datos para diferentes vehículos"""
        source = TelemetryFileSource(vehicles=3, interval=0.1)
        await source.start()
        
        vehicle_ids = set()
        async for event in source:
            vehicle_ids.add(event.vehicle_id)
            if len(vehicle_ids) >= 3:
                break
        
        assert len(vehicle_ids) == 3
        
        await source.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])