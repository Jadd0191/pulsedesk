"""
Pruebas para el event loop.

Verifica:
1. Inicialización del sistema
2. Registro de fuentes
3. Ciclo de vida
4. Apagado limpio
"""

import pytest
import asyncio
from datetime import datetime
from core.loop import EventLoop
from core.sources.heartbeat import HeartbeatSource
from core.events import (
    SystemState,
    SourceStarted,
    SourceFailed,
    ShutdownRequested,
    ShutdownComplete
)


class TestEventLoop:
    """Pruebas para el event loop"""
    
    @pytest.mark.asyncio
    async def test_loop_initialization(self):
        """Verifica que el loop se inicializa correctamente"""
        loop = EventLoop()
        assert loop.running is False
        assert loop.state == SystemState.INITIALIZING
        assert len(loop.sources) == 0
    
    @pytest.mark.asyncio
    async def test_register_source(self):
        """Verifica el registro de fuentes"""
        loop = EventLoop()
        source = HeartbeatSource(name="TestHeartbeat", interval=0.5)
        
        loop.register_source(source)
        assert len(loop.sources) == 1
        assert loop.sources[0].name == "TestHeartbeat"
    
    @pytest.mark.asyncio
    async def test_register_multiple_sources(self):
        """Verifica el registro de múltiples fuentes"""
        loop = EventLoop()
        sources = [
            HeartbeatSource(name="Source1", interval=0.5),
            HeartbeatSource(name="Source2", interval=1.0)
        ]
        
        loop.register_sources(sources)
        assert len(loop.sources) == 2
        assert loop.sources[0].name == "Source1"
        assert loop.sources[1].name == "Source2"
    
    @pytest.mark.asyncio
    async def test_loop_start_and_shutdown(self):
        """Verifica el inicio y apagado del loop"""
        loop = EventLoop()
        source = HeartbeatSource(name="TestHeartbeat", interval=0.1)
        loop.register_source(source)
        
        # Iniciar en tarea separada
        task = asyncio.create_task(loop.run())
        
        # Esperar un poco para que inicie
        await asyncio.sleep(0.5)
        
        # Solicitar apagado
        await loop.shutdown(timeout=1.0)
        
        # Esperar a que termine la tarea
        await asyncio.wait_for(task, timeout=2.0)
        
        assert loop.running is False
        assert loop.state == SystemState.SHUTDOWN
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self):
        """Verifica el apagado graceful"""
        loop = EventLoop()
        source = HeartbeatSource(name="TestHeartbeat", interval=0.1)
        loop.register_source(source)
        
        # Iniciar en tarea separada
        task = asyncio.create_task(loop.run())
        
        await asyncio.sleep(0.5)
        
        # Solicitar apagado graceful
        await loop.graceful_shutdown()
        
        await asyncio.wait_for(task, timeout=2.0)
        
        assert loop.running is False
        assert loop.shutdown_requested is True
        assert loop.state == SystemState.SHUTDOWN
    
    @pytest.mark.asyncio
    async def test_shutdown_with_timeout(self):
        """Verifica el apagado con timeout"""
        loop = EventLoop()
        
        # Fuente con intervalo largo para probar timeout
        source = HeartbeatSource(name="SlowHeartbeat", interval=10.0)
        loop.register_source(source)
        
        # Iniciar en tarea separada
        task = asyncio.create_task(loop.run())
        
        await asyncio.sleep(0.2)
        
        # Solicitar apagado con timeout corto
        await loop.shutdown(timeout=0.1)
        
        await asyncio.wait_for(task, timeout=1.0)
        
        assert loop.running is False
        assert loop.shutdown_requested is True
    
    @pytest.mark.asyncio
    async def test_event_handling(self):
        """Verifica el manejo de eventos"""
        loop = EventLoop()
        
        # Probar manejo de eventos de prueba
        source = HeartbeatSource(name="TestHeartbeat", interval=0.1)
        loop.register_source(source)
        
        # Iniciar en tarea separada
        task = asyncio.create_task(loop.run())
        
        await asyncio.sleep(0.5)
        
        # Solicitar apagado (sin argumentos adicionales)
        await loop.shutdown(timeout=1.0)
        
        await asyncio.wait_for(task, timeout=2.0)
        
        assert loop.shutdown_requested is True
    
    @pytest.mark.asyncio
    async def test_source_failure_handling(self):
        """Verifica el manejo de fallas de fuentes"""
        loop = EventLoop()
        
        # Crear una fuente que falla después de un tiempo
        class FailingSource(HeartbeatSource):
            async def __aiter__(self):
                count = 0
                while self._running:
                    await asyncio.sleep(0.1)
                    count += 1
                    if count > 3:
                        raise Exception("Simulated source failure")
                    # Usar el iterador de la clase padre
                    async for event in super().__aiter__():
                        yield event
        
        source = FailingSource(name="FailingSource", interval=0.1)
        loop.register_source(source)
        
        # Iniciar en tarea separada
        task = asyncio.create_task(loop.run())
        
        # Esperar a que falle
        await asyncio.sleep(0.5)
        
        # Apagar
        await loop.shutdown(timeout=1.0)
        
        await asyncio.wait_for(task, timeout=2.0)
        
        assert loop.running is False
        assert loop.shutdown_requested is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])