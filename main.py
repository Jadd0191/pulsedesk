"""
Main definitivo con logs de depuración.
"""

import threading
import time
import random
from datetime import datetime

from core.event_bus import EventBus
from core.events import (
    TelemetryReceived, 
    SystemHealthCheck, 
    AlertRaised, 
    AlertSeverity,
    ShutdownRequested
)
from ui.app_simple import PulseDeskApp


def generate_events(bus, stop_event):
    """Genera eventos en un hilo separado."""
    counter = 0
    vehicles = [f"V-{i:03d}" for i in range(1, 6)]
    vehicles_data = {}
    
    for v in vehicles:
        vehicles_data[v] = {
            'speed': random.uniform(20, 80),
            'temperature': random.uniform(60, 90),
            'latitude': 19.4 + random.uniform(-0.1, 0.1),
            'longitude': -99.1 + random.uniform(-0.1, 0.1),
            'engine_status': True,
            'fuel_level': random.uniform(30, 90)
        }
    
    print("[Generator] Iniciando generación de eventos...")
    
    while not stop_event.is_set():
        try:
            counter += 1
            
            vehicle = random.choice(vehicles)
            data = vehicles_data[vehicle]
            
            data['speed'] = max(0, min(150, data['speed'] + random.uniform(-5, 5)))
            data['temperature'] = max(50, min(110, data['temperature'] + random.uniform(-2, 2)))
            data['latitude'] += random.uniform(-0.005, 0.005)
            data['longitude'] += random.uniform(-0.005, 0.005)
            data['fuel_level'] = max(0, min(100, data['fuel_level'] - random.uniform(0, 0.5)))
            
            if random.random() < 0.02:
                data['engine_status'] = False
            else:
                data['engine_status'] = True
            
            telemetry = TelemetryReceived(
                vehicle_id=vehicle,
                speed=data['speed'],
                temperature=data['temperature'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                engine_status=data['engine_status'],
                fuel_level=data['fuel_level'],
                timestamp_data=datetime.now()
            )
            
            # Publicar con logs
            print(f"[Generator] Publicando: {vehicle} - {data['speed']:.1f} km/h")
            bus.publish(telemetry)
            
            if counter % 5 == 0:
                health = SystemHealthCheck(
                    status="healthy",
                    components_status={"heartbeat": "running", "telemetry": "running"},
                    uptime_seconds=counter * 0.5
                )
                bus.publish(health)
            
            if counter % 10 == 0:
                alert = AlertRaised(
                    alert_id=f"A-{counter:04d}",
                    severity=random.choice([AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.ERROR]),
                    vehicle_id=random.choice(vehicles),
                    message=f"Alerta #{counter}: {random.choice(['Temperatura alta', 'Velocidad excesiva', 'Falla de motor'])}",
                    category=random.choice(["mechanical", "route", "safety"]),
                    timestamp_data=datetime.now()
                )
                bus.publish(alert)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[Generator] Error: {e}")
            time.sleep(1)
    
    print("[Generator] Detenido")


def main():
    """Función principal."""
    print("=" * 60)
    print("PULSEDESK RAD - Centro de Control de Eventos en Tiempo Real")
    print("=" * 60)
    print()
    
    bus = EventBus()
    app = PulseDeskApp(event_bus=bus)
    
    stop_event = threading.Event()
    thread = threading.Thread(target=generate_events, args=(bus, stop_event), daemon=True)
    thread.start()
    
    try:
        print("[Main] UI iniciada - esperando eventos...")
        app.mainloop()
    except KeyboardInterrupt:
        print("\n[Main] Interrupción de teclado")
    except Exception as e:
        print(f"[Main] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[Main] Deteniendo...")
        stop_event.set()
        time.sleep(0.5)
        try:
            app.destroy()
        except:
            pass
        print("[Main] Sistema terminado")


if __name__ == "__main__":
    main()