"""
Punto de entrada principal de PulseDesk RAD.

Ejecuta el event loop con las fuentes registradas.
"""

import asyncio
import sys
from core.loop import EventLoop
from core.sources.heartbeat import HeartbeatSource


async def main():
    """Función principal del sistema."""
    print("=" * 60)
    print("PULSEDESK RAD - Centro de Control de Eventos en Tiempo Real")
    print("=" * 60)
    print()
    
    # Crear event loop
    event_loop = EventLoop()
    
    # Crear y registrar fuentes
    heartbeat = HeartbeatSource(name="Heartbeat", interval=1.0)
    event_loop.register_source(heartbeat)
    
    # Ejecutar el sistema
    try:
        await event_loop.run()
    except KeyboardInterrupt:
        print("\n[Main] Keyboard interrupt received")
        await event_loop.graceful_shutdown()
    except Exception as e:
        print(f"[Main] Fatal error: {e}")
        sys.exit(1)
    
    print("[Main] System terminated successfully")
    sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Main] Interrupted by user")
        sys.exit(0)