"""
Bus de eventos propio para PulseDesk RAD.
"""

import weakref
import traceback
import threading
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from core.events import Event


class EventBus:
    """Bus de eventos con Pub/Sub."""
    
    def __init__(self):
        self._handlers: Dict[type, List[Callable]] = defaultdict(list)
        self._topic_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
        self._stats = {'published': 0, 'handled': 0, 'errors': 0}
    
    def subscribe(self, event_type: type, handler: Callable, topic: Optional[str] = None) -> None:
        """Suscribe un handler."""
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        with self._lock:
            if topic:
                self._topic_handlers[topic].append(handler)
                print(f"[EventBus] Subscribed to topic '{topic}'")
            else:
                self._handlers[event_type].append(handler)
                print(f"[EventBus] Subscribed to {event_type.__name__}")
    
    def unsubscribe(self, handler: Callable, event_type: Optional[type] = None, 
                    topic: Optional[str] = None) -> bool:
        """Desuscribe un handler."""
        removed = False
        with self._lock:
            if event_type:
                self._handlers[event_type] = [h for h in self._handlers.get(event_type, []) if h != handler]
            if topic:
                self._topic_handlers[topic] = [h for h in self._topic_handlers.get(topic, []) if h != handler]
        return removed
    
    def publish(self, event: Event, topic: Optional[str] = None) -> None:
        """Publica un evento."""
        self._stats['published'] += 1
        
        with self._lock:
            event_type = type(event)
            handlers = []
            
            # Handlers por tipo
            if event_type in self._handlers:
                handlers.extend(self._handlers[event_type])
            if Event in self._handlers:
                handlers.extend(self._handlers[Event])
            
            # Handlers por tema
            if topic and topic in self._topic_handlers:
                handlers.extend(self._topic_handlers[topic])
        
        # Ejecutar handlers
        for handler in handlers:
            try:
                handler(event)
                self._stats['handled'] += 1
            except Exception as e:
                self._stats['errors'] += 1
                print(f"[EventBus] Error en handler: {e}")
                traceback.print_exc()
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estadísticas."""
        return self._stats.copy()
    
    def clear(self) -> None:
        """Limpia todos los handlers."""
        with self._lock:
            self._handlers.clear()
            self._topic_handlers.clear()


# ============================================================================
# Decorador para suscripción automática
# ============================================================================

def subscribe_to(event_type: type, topic: Optional[str] = None):
    """
    Decorador para suscribir automáticamente un handler al bus.
    
    Args:
        event_type: Tipo de evento a suscribir
        topic: Tema opcional
    
    Ejemplo:
        @subscribe_to(TelemetryReceived)
        def handle_telemetry(event):
            print(f"Received: {event.vehicle_id}")
    """
    def decorator(func):
        func._subscribe_to = (event_type, topic)
        return func
    return decorator