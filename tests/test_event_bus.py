"""
Pruebas para el bus de eventos.

Verifica:
1. Suscripción y publicación
2. Desuscripción
3. Prevención de fugas de memoria
4. Manejo de errores
5. Temas (topics)
"""

import pytest
import gc
import weakref
from core.event_bus import EventBus
from core.events import Event, TelemetryReceived, AlertRaised, AlertSeverity
from datetime import datetime


class TestEventBus:
    """Pruebas para el bus de eventos"""
    
    @pytest.fixture
    def bus(self):
        """Crea un bus limpio para cada prueba."""
        return EventBus()
    
    def test_subscribe_and_publish(self, bus):
        """Verifica que la suscripción y publicación funcionan."""
        results = []
        
        def handler(event):
            results.append(event)
        
        bus.subscribe(Event, handler)
        event = Event()
        bus.publish(event)
        
        assert len(results) == 1
        assert results[0] is event
    
    def test_multiple_handlers(self, bus):
        """Verifica que múltiples handlers reciben el evento."""
        results1 = []
        results2 = []
        
        def handler1(event):
            results1.append(event)
        
        def handler2(event):
            results2.append(event)
        
        bus.subscribe(Event, handler1)
        bus.subscribe(Event, handler2)
        
        event = Event()
        bus.publish(event)
        
        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0] is event
        assert results2[0] is event
    
    def test_unsubscribe(self, bus):
        """Verifica que la desuscripción funciona."""
        results = []
        
        def handler(event):
            results.append(event)
        
        bus.subscribe(Event, handler)
        
        # Desuscribir
        bus.unsubscribe(handler, Event)
        
        event = Event()
        bus.publish(event)
        
        assert len(results) == 0
    
    def test_unsubscribe_by_topic(self, bus):
        """Verifica desuscripción por tema."""
        results = []
        
        def handler(event):
            results.append(event)
        
        bus.subscribe(Event, handler, topic="test")
        
        # Desuscribir por tema
        bus.unsubscribe(handler, topic="test")
        
        event = Event()
        bus.publish(event, topic="test")
        
        assert len(results) == 0
    
    def test_unsubscribe_all(self, bus):
        """Verifica desuscripción de todas las suscripciones."""
        results = []
        
        def handler(event):
            results.append(event)
        
        bus.subscribe(Event, handler)
        bus.subscribe(Event, handler, topic="test")
        
        # Desuscribir sin especificar tipo ni tema
        bus.unsubscribe(handler)
        
        event = Event()
        bus.publish(event)
        bus.publish(event, topic="test")
        
        assert len(results) == 0
    
    def test_topic_subscription(self, bus):
        """Verifica suscripción por temas."""
        topic_results = []
        other_results = []
        
        def topic_handler(event):
            topic_results.append(event)
        
        def other_handler(event):
            other_results.append(event)
        
        bus.subscribe(Event, topic_handler, topic="test")
        bus.subscribe(Event, other_handler)
        
        event = Event()
        bus.publish(event, topic="test")
        
        # Solo el handler del tema debe recibir
        assert len(topic_results) == 1
        assert len(other_results) == 0
        
        # Publicar sin tema - solo el otro handler
        bus.publish(event)
        assert len(other_results) == 1
    
    def test_specific_event_type(self, bus):
        """Verifica suscripción a tipos específicos de eventos."""
        telemetry_results = []
        alert_results = []
        
        def telemetry_handler(event):
            telemetry_results.append(event)
        
        def alert_handler(event):
            alert_results.append(event)
        
        bus.subscribe(TelemetryReceived, telemetry_handler)
        bus.subscribe(AlertRaised, alert_handler)
        
        # Publicar evento de telemetría
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
        bus.publish(telemetry)
        
        # Publicar evento de alerta
        alert = AlertRaised(
            alert_id="A-001",
            severity=AlertSeverity.CRITICAL,
            vehicle_id="V-001",
            message="Engine overheating",
            category="mechanical",
            timestamp_data=datetime.now()
        )
        bus.publish(alert)
        
        assert len(telemetry_results) == 1
        assert len(alert_results) == 1
    
    def test_error_handling(self, bus):
        """Verifica que los errores en handlers no afectan a otros."""
        results = []
        
        def failing_handler(event):
            raise ValueError("Handler error")
        
        def working_handler(event):
            results.append(event)
        
        bus.subscribe(Event, failing_handler)
        bus.subscribe(Event, working_handler)
        
        event = Event()
        bus.publish(event)
        
        # El handler que funciona debe haber procesado el evento
        assert len(results) == 1
        
        # Verificar estadísticas de errores
        stats = bus.get_stats()
        assert stats['errors'] >= 1
        assert stats['handled'] >= 1
    
    def test_no_memory_leaks(self, bus):
        """
        Verifica que no hay fugas de memoria (weakref funciona).
        
        Esta prueba es crítica: el handler debe ser recolectado
        cuando ya no se usa.
        """
        results = []
        
        def create_handler():
            def handler(event):
                results.append(event)
            return handler
        
        # Crear y suscribir un handler
        handler = create_handler()
        bus.subscribe(Event, handler)
        
        # Eliminar referencia al handler
        handler_ref = weakref.ref(handler)
        del handler
        
        # Forzar garbage collection
        gc.collect()
        
        # El handler debería estar muerto
        assert handler_ref() is None
        
        # Publicar evento - no debería fallar
        bus.publish(Event())
        
        # La referencia débil debería haber sido limpiada
        # Verificar que el bus no tiene handlers muertos
        bus._cleanup()
        assert bus.get_subscriber_count(Event) == 0
    
    def test_cleanup_dead_references(self, bus):
        """Verifica que las referencias muertas se limpian automáticamente."""
        results = []
        
        class Handler:
            def __call__(self, event):
                results.append(event)
        
        # Crear handler y suscribir
        handler = Handler()
        bus.subscribe(Event, handler)
        
        # Eliminar handler
        del handler
        
        # Forzar garbage collection
        gc.collect()
        
        # Limpiar referencias muertas
        bus._cleanup()
        
        # No debería haber suscriptores
        assert not bus.has_subscribers(Event)
    
    def test_stats(self, bus):
        """Verifica que las estadísticas se actualizan correctamente."""
        def handler(event):
            pass
        
        bus.subscribe(Event, handler)
        
        # Publicar eventos
        for _ in range(5):
            bus.publish(Event())
        
        stats = bus.get_stats()
        assert stats['published'] == 5
        assert stats['handled'] == 5
    
    def test_clear(self, bus):
        """Verifica que clear() elimina todos los handlers."""
        def handler(event):
            pass
        
        bus.subscribe(Event, handler)
        bus.subscribe(Event, handler, topic="test")
        
        assert bus.has_subscribers()
        
        bus.clear()
        
        assert not bus.has_subscribers()
        assert bus.get_subscriber_count() == 0
    
    def test_has_subscribers(self, bus):
        """Verifica has_subscribers() funciona correctamente."""
        def handler(event):
            pass
        
        assert not bus.has_subscribers()
        
        bus.subscribe(Event, handler)
        assert bus.has_subscribers(Event)
        assert not bus.has_subscribers(TelemetryReceived)
        
        bus.subscribe(Event, handler, topic="test")
        assert bus.has_subscribers(topic="test")
        assert not bus.has_subscribers(topic="other")
    
    def test_get_subscriber_count(self, bus):
        """Verifica get_subscriber_count() funciona correctamente."""
        def handler1(event):
            pass
        
        def handler2(event):
            pass
        
        bus.subscribe(Event, handler1)
        bus.subscribe(Event, handler2)
        bus.subscribe(Event, handler1, topic="test")
        
        assert bus.get_subscriber_count(Event) == 2
        assert bus.get_subscriber_count(topic="test") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])