"""
Script de prueba para verificar el bus de eventos.
"""

import threading
import time
import queue
from core.event_bus import EventBus
from core.events import Event, TelemetryReceived, SystemHealthCheck
from datetime import datetime


def test_bus():
    """Prueba simple del bus."""
    print("=" * 60)
    print("TEST: Verificación del EventBus")
    print("=" * 60)
    
    # Crear bus
    bus = EventBus()
    
    # Cola para eventos
    event_queue = queue.Queue()
    
    # Definir handler que pone eventos en la cola
    def queue_event(event):
        print(f"[Handler] Evento recibido: {event.__class__.__name__}")
        event_queue.put(event)
    
    # Suscribir handler
    print("\n[1] Suscribiendo handler...")
    bus.subscribe(TelemetryReceived, queue_event)
    bus.subscribe(SystemHealthCheck, queue_event)
    
    # Verificar suscripciones
    print(f"\n[2] Suscriptores: {bus.get_subscriber_count()}")
    
    # Publicar evento desde el hilo principal
    print("\n[3] Publicando evento desde hilo principal...")
    telemetry = TelemetryReceived(
        vehicle_id="V-TEST",
        speed=75.5,
        temperature=85.2,
        latitude=19.4326,
        longitude=-99.1332,
        engine_status=True,
        fuel_level=72.3,
        timestamp_data=datetime.now()
    )
    bus.publish(telemetry)
    
    # Verificar que llegó a la cola
    try:
        event = event_queue.get(timeout=1)
        print(f"[OK] Evento recibido en cola: {event.__class__.__name__}")
    except queue.Empty:
        print("[ERROR] No se recibió el evento en la cola")
        return False
    
    # Publicar desde otro hilo
    print("\n[4] Publicando evento desde otro hilo...")
    
    def publish_in_thread():
        health = SystemHealthCheck(
            status="healthy",
            components_status={"test": "running"},
            uptime_seconds=5.0
        )
        bus.publish(health)
        print("[Thread] Evento publicado desde hilo")
    
    thread = threading.Thread(target=publish_in_thread)
    thread.start()
    thread.join()
    
    # Verificar que llegó a la cola
    try:
        event = event_queue.get(timeout=1)
        print(f"[OK] Evento recibido en cola desde hilo: {event.__class__.__name__}")
    except queue.Empty:
        print("[ERROR] No se recibió el evento en la cola desde el hilo")
        return False
    
    print("\n[SUCCESS] El bus funciona correctamente!")
    return True


if __name__ == "__main__":
    test_bus()