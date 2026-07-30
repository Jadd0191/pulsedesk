"""
Event Loop principal de PulseDesk RAD.

Gestiona el ciclo de vida del sistema:
- Inicialización
- Registro de fuentes
- Bucle principal
- Apagado limpio (graceful shutdown)
"""

import asyncio
import signal
import sys
from typing import List, Optional
from datetime import datetime
from core.events import (
    Event,
    SystemInitialized,
    ShutdownRequested,
    ShutdownComplete,
    SourceStarted,
    SourceStopped,
    SourceFailed,
    StateChanged,
    SystemState
)
from core.sources.base import Source
from core.event_bus import EventBus


class EventLoop:
    """
    Bucle de eventos principal del sistema.
    
    Responsable de:
    1. Inicializar el sistema
    2. Registrar y gestionar fuentes de datos
    3. Ejecutar el bucle principal
    4. Manejar apagado limpio
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.sources: List[Source] = []
        self.tasks: List[asyncio.Task] = []
        self.running: bool = False
        self.shutdown_requested: bool = False
        self.state: SystemState = SystemState.INITIALIZING
        self.start_time: Optional[datetime] = None
        self._shutdown_timeout: float = 5.0
        self.event_bus: Optional[EventBus] = event_bus
    
    def set_event_bus(self, event_bus: EventBus) -> None:
        """Establece el bus de eventos."""
        self.event_bus = event_bus
    
    def register_source(self, source: Source) -> None:
        """
        Registra una fuente de datos en el sistema.
        
        Args:
            source: Fuente a registrar
        """
        if source in self.sources:
            print(f"[EventLoop] Source {source.name} already registered")
            return
        
        self.sources.append(source)
        print(f"[EventLoop] Registered source: {source.name}")
    
    def register_sources(self, sources: List[Source]) -> None:
        """
        Registra múltiples fuentes.
        
        Args:
            sources: Lista de fuentes a registrar
        """
        for source in sources:
            self.register_source(source)
    
    async def initialize(self) -> None:
        """Inicializa el sistema y todas las fuentes."""
        print("[EventLoop] Initializing system...")
        self.start_time = datetime.now()
        self.state = SystemState.INITIALIZING
        
        # Iniciar todas las fuentes
        for source in self.sources:
            try:
                await source.start()
                print(f"[EventLoop] Source {source.name} started successfully")
                
                # Publicar evento de inicio
                if self.event_bus:
                    event = SourceStarted(
                        source_name=source.name,
                        source_type=source.__class__.__name__,
                    )
                    self.event_bus.publish(event)
                
            except Exception as e:
                print(f"[EventLoop] Failed to start source {source.name}: {e}")
                if self.event_bus:
                    event = SourceFailed(
                        source_name=source.name,
                        error_message=str(e),
                        is_critical=True
                    )
                    self.event_bus.publish(event)
        
        self.state = SystemState.RUNNING
        
        # Publicar evento de inicialización
        if self.event_bus:
            init_event = SystemInitialized(
                config={
                    "sources_count": len(self.sources),
                    "sources": [s.name for s in self.sources]
                },
                start_time=self.start_time
            )
            self.event_bus.publish(init_event)
        
        print(f"[EventLoop] System initialized with {len(self.sources)} sources")
    
    async def run(self) -> None:
        """
        Ejecuta el bucle principal del sistema.
        
        Este método corre hasta que se solicita un apagado.
        """
        if not self.sources:
            print("[EventLoop] No sources registered. Exiting.")
            return
        
        self.running = True
        
        print("[EventLoop] Event loop running. Press Ctrl+C to stop.")
        
        try:
            # Inicializar sistema
            await self.initialize()
            
            # Crear tareas para cada fuente
            for source in self.sources:
                task = asyncio.create_task(self._run_source(source))
                self.tasks.append(task)
                print(f"[EventLoop] Task created for source: {source.name}")
            
            # Esperar a que se complete el apagado
            while not self.shutdown_requested:
                await asyncio.sleep(0.1)
                
                # Verificar si alguna tarea falló
                for task in self.tasks:
                    if task.done() and not task.cancelled():
                        try:
                            task.result()
                        except Exception as e:
                            print(f"[EventLoop] Task failed: {e}")
                            if self.event_bus:
                                self.event_bus.publish(
                                    SourceFailed(
                                        source_name="unknown",
                                        error_message=str(e),
                                        is_critical=False
                                    )
                                )
            
        except asyncio.CancelledError:
            print("[EventLoop] Event loop cancelled")
        except Exception as e:
            print(f"[EventLoop] Unexpected error: {e}")
        finally:
            await self.shutdown()
    
    async def _run_source(self, source: Source) -> None:
        """
        Ejecuta una fuente de datos.
        
        Args:
            source: Fuente a ejecutar
        """
        try:
            async for event in source:
                if self.shutdown_requested:
                    break
                
                # Publicar evento en el bus
                if self.event_bus:
                    self.event_bus.publish(event)
                else:
                    # Si no hay bus, solo imprimir
                    print(f"[{source.name}] Event: {event.__class__.__name__}")
                    
        except asyncio.CancelledError:
            print(f"[EventLoop] Source {source.name} task cancelled")
            raise
        except Exception as e:
            print(f"[EventLoop] Source {source.name} error: {e}")
            if self.event_bus:
                self.event_bus.publish(
                    SourceFailed(
                        source_name=source.name,
                        error_message=str(e),
                        is_critical=False
                    )
                )
    
    async def shutdown(self, timeout: float = 5.0) -> None:
        """
        Apagado limpio del sistema.
        
        Args:
            timeout: Tiempo máximo para el apagado (segundos)
        """
        if self.shutdown_requested:
            return
        
        self.shutdown_requested = True
        self.state = SystemState.SHUTTING_DOWN
        print("[EventLoop] Initiating graceful shutdown...")
        
        start_time = datetime.now()
        errors = []
        
        try:
            # Cancelar todas las tareas
            for task in self.tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=timeout)
                    except asyncio.TimeoutError:
                        errors.append(f"Task timeout")
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        errors.append(f"Task error: {e}")
            
            # Detener todas las fuentes
            for source in self.sources:
                try:
                    await source.stop()
                except Exception as e:
                    errors.append(f"Source {source.name} stop error: {e}")
            
        except Exception as e:
            errors.append(f"Shutdown error: {e}")
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            self.state = SystemState.SHUTDOWN
            self.running = False
            
            # Publicar evento de apagado
            if self.event_bus:
                shutdown_event = ShutdownComplete(
                    success=len(errors) == 0,
                    duration_seconds=duration,
                    errors=errors
                )
                self.event_bus.publish(shutdown_event)
            
            print(f"[EventLoop] Shutdown complete in {duration:.2f}s")
            if errors:
                print(f"[EventLoop] Errors during shutdown: {errors}")
    
    async def graceful_shutdown(self) -> None:
        """Alias para shutdown."""
        await self.shutdown(timeout=self._shutdown_timeout)