"""
Bus de eventos propio para PulseDesk RAD.

Implementa los patrones Observer y Pub/Sub sin librerías externas.
Características:
- Suscripción y desuscripción de handlers
- Publicación de eventos
- Manejo de errores sin tumbar a otros handlers
- Prevención de fugas de memoria con weakref
- Temas (topics) para desacople
"""

import weakref
import traceback
from typing import Dict, List, Callable, Any, Optional, Set, Union
from collections import defaultdict
from dataclasses import dataclass
from core.events import Event


class EventBus:
    """
    Bus de eventos que implementa Pub/Sub.
    
    Los suscriptores se registran para un tipo de evento específico
    o para un tema (topic). Cuando se publica un evento, todos los
    handlers registrados son notificados.
    """
    
    def __init__(self):
        # Registro de handlers por tipo de evento (SOLO para eventos sin tema)
        self._handlers: Dict[type, List[weakref.ref]] = defaultdict(list)
        
        # Registro de handlers por tema (topic)
        self._topic_handlers: Dict[str, List[weakref.ref]] = defaultdict(list)
        
        # Registro de handlers por tipo de evento Y tema
        self._topic_type_handlers: Dict[str, Dict[type, List[weakref.ref]]] = defaultdict(lambda: defaultdict(list))
        
        # Para evitar recursión infinita
        self._publishing: bool = False
        
        # Estadísticas
        self._stats = {
            'published': 0,
            'handled': 0,
            'errors': 0,
            'dropped': 0
        }
    
    def subscribe(self, event_type: type, handler: Callable, topic: Optional[str] = None) -> None:
        """
        Suscribe un handler a un tipo de evento o tema.
        
        Args:
            event_type: Tipo de evento a escuchar
            handler: Función que manejará el evento
            topic: Tema opcional para suscripción
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        # Crear referencia débil para evitar fugas de memoria
        ref = weakref.ref(handler)
        
        if topic:
            # Suscripción por tema + tipo
            self._topic_type_handlers[topic][event_type].append(ref)
            print(f"[EventBus] Subscribed handler to topic '{topic}' for {event_type.__name__}")
        else:
            # Suscripción por tipo de evento (sin tema)
            self._handlers[event_type].append(ref)
            print(f"[EventBus] Subscribed handler to {event_type.__name__}")
        
        # Limpiar referencias muertas
        self._cleanup()
    
    def unsubscribe(self, handler: Callable, event_type: Optional[type] = None, 
                    topic: Optional[str] = None) -> bool:
        """
        Desuscribe un handler.
        
        Args:
            handler: Handler a desuscribir
            event_type: Tipo de evento específico (opcional)
            topic: Tema específico (opcional)
            
        Returns:
            True si se encontró y eliminó, False en caso contrario
        """
        removed = False
        
        # Buscar por tipo de evento (sin tema)
        if event_type and not topic:
            handlers = self._handlers.get(event_type, [])
            self._handlers[event_type] = [
                ref for ref in handlers 
                if ref() is not handler
            ]
            if len(handlers) != len(self._handlers[event_type]):
                removed = True
                if not self._handlers[event_type]:
                    del self._handlers[event_type]
        
        # Buscar por tema + tipo
        if topic and event_type:
            if topic in self._topic_type_handlers:
                handlers = self._topic_type_handlers[topic].get(event_type, [])
                self._topic_type_handlers[topic][event_type] = [
                    ref for ref in handlers 
                    if ref() is not handler
                ]
                if len(handlers) != len(self._topic_type_handlers[topic][event_type]):
                    removed = True
                    if not self._topic_type_handlers[topic][event_type]:
                        del self._topic_type_handlers[topic][event_type]
                    if not self._topic_type_handlers[topic]:
                        del self._topic_type_handlers[topic]
        
        # Buscar por tema (todos los tipos)
        if topic and not event_type:
            if topic in self._topic_type_handlers:
                for ev_type in list(self._topic_type_handlers[topic].keys()):
                    handlers = self._topic_type_handlers[topic][ev_type]
                    self._topic_type_handlers[topic][ev_type] = [
                        ref for ref in handlers 
                        if ref() is not handler
                    ]
                    if len(handlers) != len(self._topic_type_handlers[topic][ev_type]):
                        removed = True
                    if not self._topic_type_handlers[topic][ev_type]:
                        del self._topic_type_handlers[topic][ev_type]
                if not self._topic_type_handlers[topic]:
                    del self._topic_type_handlers[topic]
        
        # Si no se especificó tipo ni tema, buscar en todos lados
        if not event_type and not topic:
            # Buscar en handlers por tipo (sin tema)
            for ev_type in list(self._handlers.keys()):
                handlers = self._handlers[ev_type]
                self._handlers[ev_type] = [
                    ref for ref in handlers 
                    if ref() is not handler
                ]
                if len(handlers) != len(self._handlers[ev_type]):
                    removed = True
                if not self._handlers[ev_type]:
                    del self._handlers[ev_type]
            
            # Buscar en handlers por tema
            for t in list(self._topic_type_handlers.keys()):
                for ev_type in list(self._topic_type_handlers[t].keys()):
                    handlers = self._topic_type_handlers[t][ev_type]
                    self._topic_type_handlers[t][ev_type] = [
                        ref for ref in handlers 
                        if ref() is not handler
                    ]
                    if len(handlers) != len(self._topic_type_handlers[t][ev_type]):
                        removed = True
                    if not self._topic_type_handlers[t][ev_type]:
                        del self._topic_type_handlers[t][ev_type]
                if not self._topic_type_handlers[t]:
                    del self._topic_type_handlers[t]
        
        self._cleanup()
        return removed
    
    def publish(self, event: Event, topic: Optional[str] = None) -> None:
        """
        Publica un evento en el bus.
        
        Args:
            event: Evento a publicar
            topic: Tema para publicación (opcional)
        """
        if self._publishing:
            # Evitar recursión infinita
            print("[EventBus] Warning: Recursive publish detected")
            return
        
        self._publishing = True
        self._stats['published'] += 1
        
        try:
            # Limpiar referencias muertas
            self._cleanup()
            
            # Obtener tipo de evento
            event_type = type(event)
            
            # Colección de handlers a ejecutar
            all_handlers = []
            seen = set()
            
            if topic:
                # Si hay tema, buscar handlers por tema + tipo
                if topic in self._topic_type_handlers:
                    handlers = self._topic_type_handlers[topic].get(event_type, [])
                    for ref in handlers:
                        handler = ref()
                        if handler and id(handler) not in seen:
                            all_handlers.append(handler)
                            seen.add(id(handler))
                
                # También buscar handlers que escuchan TODOS los eventos en este tema
                if topic in self._topic_type_handlers:
                    # Buscar handlers para Event (clase base)
                    handlers = self._topic_type_handlers[topic].get(Event, [])
                    for ref in handlers:
                        handler = ref()
                        if handler and id(handler) not in seen:
                            all_handlers.append(handler)
                            seen.add(id(handler))
            else:
                # Sin tema: solo buscar handlers por tipo de evento
                handlers = self._handlers.get(event_type, [])
                for ref in handlers:
                    handler = ref()
                    if handler and id(handler) not in seen:
                        all_handlers.append(handler)
                        seen.add(id(handler))
                
                # También buscar handlers para Event (clase base)
                handlers = self._handlers.get(Event, [])
                for ref in handlers:
                    handler = ref()
                    if handler and id(handler) not in seen:
                        all_handlers.append(handler)
                        seen.add(id(handler))
            
            # Ejecutar todos los handlers
            for handler in all_handlers:
                try:
                    handler(event)
                    self._stats['handled'] += 1
                except Exception as e:
                    self._stats['errors'] += 1
                    print(f"[EventBus] Error in handler {handler.__name__ if hasattr(handler, '__name__') else str(handler)}: {e}")
                    traceback.print_exc()
                    
        except Exception as e:
            self._stats['errors'] += 1
            print(f"[EventBus] Error publishing event: {e}")
            traceback.print_exc()
        finally:
            self._publishing = False
    
    def _cleanup(self) -> None:
        """Limpia referencias débiles muertas."""
        # Limpiar handlers por tipo (sin tema)
        for event_type in list(self._handlers.keys()):
            handlers = self._handlers[event_type]
            self._handlers[event_type] = [
                ref for ref in handlers if ref() is not None
            ]
            if not self._handlers[event_type]:
                del self._handlers[event_type]
        
        # Limpiar handlers por tema + tipo
        for topic in list(self._topic_type_handlers.keys()):
            for event_type in list(self._topic_type_handlers[topic].keys()):
                handlers = self._topic_type_handlers[topic][event_type]
                self._topic_type_handlers[topic][event_type] = [
                    ref for ref in handlers if ref() is not None
                ]
                if not self._topic_type_handlers[topic][event_type]:
                    del self._topic_type_handlers[topic][event_type]
            if not self._topic_type_handlers[topic]:
                del self._topic_type_handlers[topic]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Retorna estadísticas del bus.
        
        Returns:
            Diccionario con estadísticas
        """
        return self._stats.copy()
    
    def clear(self) -> None:
        """Limpia todos los handlers registrados."""
        self._handlers.clear()
        self._topic_type_handlers.clear()
        self._cleanup()
    
    def has_subscribers(self, event_type: Optional[type] = None, 
                        topic: Optional[str] = None) -> bool:
        """
        Verifica si hay suscriptores para un tipo o tema.
        
        Args:
            event_type: Tipo de evento a verificar
            topic: Tema a verificar
            
        Returns:
            True si hay suscriptores, False en caso contrario
        """
        if event_type and topic:
            return bool(self._topic_type_handlers.get(topic, {}).get(event_type, []))
        if event_type:
            return bool(self._handlers.get(event_type, []))
        if topic:
            return bool(self._topic_type_handlers.get(topic, {}))
        return bool(self._handlers) or bool(self._topic_type_handlers)
    
    def get_subscriber_count(self, event_type: Optional[type] = None,
                             topic: Optional[str] = None) -> int:
        """
        Retorna el número de suscriptores para un tipo o tema.
        
        Args:
            event_type: Tipo de evento
            topic: Tema
            
        Returns:
            Número de suscriptores
        """
        self._cleanup()
        
        if event_type and topic:
            return len(self._topic_type_handlers.get(topic, {}).get(event_type, []))
        if event_type:
            return len(self._handlers.get(event_type, []))
        if topic:
            total = 0
            for handlers in self._topic_type_handlers.get(topic, {}).values():
                total += len(handlers)
            return total
        
        # Total de suscriptores únicos
        total = 0
        for handlers in self._handlers.values():
            total += len(handlers)
        for topic_data in self._topic_type_handlers.values():
            for handlers in topic_data.values():
                total += len(handlers)
        return total


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


# ============================================================================
# Ejemplo de uso
# ============================================================================

if __name__ == "__main__":
    # Crear bus
    bus = EventBus()
    
    # Definir handlers
    def handler1(event):
        print(f"Handler 1: {event}")
    
    def handler2(event):
        print(f"Handler 2: {event}")
    
    # Suscribir
    bus.subscribe(Event, handler1)
    bus.subscribe(Event, handler2, topic="test")
    
    # Publicar
    event = Event()
    bus.publish(event)
    
    # Estadísticas
    print(f"Stats: {bus.get_stats()}")