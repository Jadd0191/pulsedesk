"""
Fuente de latido (Heartbeat).

Genera eventos de health check periódicos para demostrar
que el event loop funciona correctamente.
"""

import asyncio
from datetime import datetime
from typing import AsyncIterator, Optional
from core.sources.base import Source
from core.events import SystemHealthCheck, SourceStarted, SourceStopped, SourceFailed


class HeartbeatSource(Source):
    """
    Fuente que genera un latido periódico.
    
    Emite eventos SystemHealthCheck cada intervalo definido.
    """
    
    def __init__(self, name: str = "Heartbeat", interval: float = 1.0):
        super().__init__(name)
        self.interval = interval
        self._task: Optional[asyncio.Task] = None
        self._start_time: Optional[datetime] = None
    
    async def start(self) -> None:
        """Inicia la fuente de latido."""
        self._running = True
        self._start_time = datetime.now()
        print(f"[{self.name}] Source started")
    
    async def stop(self) -> None:
        """Detiene la fuente de latido."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print(f"[{self.name}] Source stopped")
    
    async def __aiter__(self) -> AsyncIterator[SystemHealthCheck]:
        """Genera eventos de health check periódicos."""
        try:
            async for event in self._heartbeat_loop():
                yield event
        except asyncio.CancelledError:
            print(f"[{self.name}] Heartbeat loop cancelled")
            raise
    
    async def _heartbeat_loop(self) -> AsyncIterator[SystemHealthCheck]:
        """Bucle interno que genera los latidos."""
        count = 0
        while self._running:
            try:
                # Simular procesamiento
                await asyncio.sleep(self.interval)
                
                count += 1
                uptime = (datetime.now() - self._start_time).total_seconds()
                
                # Generar evento de health check
                yield SystemHealthCheck(
                    status="healthy",
                    components_status={
                        "heartbeat": "running",
                        "event_loop": "active"
                    },
                    uptime_seconds=uptime
                )
                
                # Log cada 5 latidos
                if count % 5 == 0:
                    print(f"[{self.name}] Heartbeat #{count} - Uptime: {uptime:.1f}s")
                    
            except asyncio.CancelledError:
                print(f"[{self.name}] Heartbeat interrupted")
                break
            except Exception as e:
                print(f"[{self.name}] Heartbeat error: {e}")
                # En caso de error, generamos evento de falla
                yield SourceFailed(
                    source_name=self.name,
                    error_message=str(e),
                    retry_count=0,
                    is_critical=False
                )
                await asyncio.sleep(self.interval * 2)