"""
Punto de entrada principal de PulseDesk RAD.

Ejecuta el event loop con las fuentes registradas y la interfaz gráfica.
"""

import asyncio
import sys
import threading
from core.loop import EventLoop
from core.sources.heartbeat import HeartbeatSource
from ui.app import PulseDeskApp


async def run_event_loop(app, loop):
    """
    Ejecuta el event loop del sistema.
    
    Args:
        app: Referencia a la aplicación UI
        loop: Referencia al event loop asyncio
    """
    # Crear event loop
    event_loop = EventLoop()
    
    # Crear y registrar fuentes
    heartbeat = HeartbeatSource(name="Heartbeat", interval=1.0)
    event_loop.register_source(heartbeat)
    
    # Conectar UI al event loop
    app.event_loop = event_loop
    app.set_event_loop(loop)
    
    # Ejecutar el sistema
    try:
        await event_loop.run()
    except KeyboardInterrupt:
        print("\n[Main] Keyboard interrupt received")
        await event_loop.graceful_shutdown()
    except Exception as e:
        print(f"[Main] Fatal error: {e}")
        sys.exit(1)
    
    # Cerrar UI
    app.running = False
    app.destroy()


def run_ui():
    """Ejecuta la interfaz de usuario en el hilo principal."""
    # Crear aplicación
    app = PulseDeskApp()
    
    # Crear event loop asyncio
    loop = asyncio.new_event_loop()
    
    def start_loop():
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_event_loop(app, loop))
        except Exception as e:
            print(f"[Main] Event loop error: {e}")
        finally:
            loop.close()
    
    # Ejecutar event loop en hilo separado
    thread = threading.Thread(target=start_loop, daemon=True)
    thread.start()
    
    # Ejecutar UI en hilo principal
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n[Main] Interrupted by user")
        app._on_closing()
    finally:
        # Cerrar event loop
        if not loop.is_closed():
            loop.call_soon_threadsafe(loop.stop)
        sys.exit(0)


if __name__ == "__main__":
    print("=" * 60)
    print("PULSEDESK RAD - Centro de Control de Eventos en Tiempo Real")
    print("=" * 60)
    print()
    print("Iniciando interfaz gráfica...")
    print()
    
    run_ui()