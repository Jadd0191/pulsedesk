"""
Interfaz base para fuentes de datos.

Toda fuente de datos debe implementar esta interfaz para ser
registrada en el event loop.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from core.events import Event


class Source(ABC):
    """
    Clase base abstracta para todas las fuentes de datos.
    
    Cada fuente es un iterador asíncrono que produce eventos.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._running = False
    
    @abstractmethod
    async def start(self) -> None:
        """Inicia la fuente de datos."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Detiene la fuente de datos."""
        pass
    
    @abstractmethod
    async def __aiter__(self) -> AsyncIterator[Event]:
        """
        Iterador asíncrono que produce eventos.
        
        Yields:
            Event: Evento generado por la fuente
        """
        pass
    
    @property
    def is_running(self) -> bool:
        """Indica si la fuente está corriendo."""
        return self._running