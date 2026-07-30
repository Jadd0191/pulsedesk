"""
Ventana principal de PulseDesk RAD - Versión simplificada.
"""

import customtkinter as ctk
from typing import Optional
import queue

from core.event_bus import EventBus
from core.events import (
    TelemetryReceived,
    AlertRaised,
    SystemHealthCheck,
    SourceFailed,
    ShutdownRequested
)
from ui.panels.telemetry_panel import TelemetryPanel
from ui.panels.alerts_panel import AlertsPanel
from ui.panels.status_panel import StatusPanel


class PulseDeskApp(ctk.CTk):
    """Aplicación principal de PulseDesk."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        super().__init__()
        
        self.event_bus = event_bus
        self.event_loop = None
        self.running = True
        self._closing = False  # Flag para evitar cierre duplicado
        
        # Cola para eventos (thread-safe)
        self._event_queue = queue.Queue()
        self._handlers_registered = False
        
        # Configurar ventana
        self.title("PulseDesk RAD - Centro de Control de Eventos")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear layout
        self._create_layout()
        
        # Registrar handlers en el bus
        self._register_handlers()
        
        # Iniciar actualización de UI
        self.after(500, self._process_events)
        
        # Configurar cierre
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _register_handlers(self):
        """Registra los handlers en el event bus."""
        if not self.event_bus:
            print("[UI] No event bus disponible")
            return
        
        if self._handlers_registered:
            return
        
        # Suscribir handlers
        self.event_bus.subscribe(TelemetryReceived, self._queue_event)
        self.event_bus.subscribe(AlertRaised, self._queue_event)
        self.event_bus.subscribe(SystemHealthCheck, self._queue_event)
        self.event_bus.subscribe(SourceFailed, self._queue_event)
        
        self._handlers_registered = True
        print("[UI] Handlers registrados en el bus")
    
    def _queue_event(self, event):
        """Pone un evento en la cola."""
        if self.running:
            self._event_queue.put(event)
    
    def _create_layout(self):
        """Crea la estructura de la ventana."""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.main_frame.grid_columnconfigure(0, weight=2)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        
        # Panel de telemetría
        self.telemetry_panel = TelemetryPanel(self.main_frame)
        self.telemetry_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=(0, 5))
        
        # Panel de alertas
        self.alerts_panel = AlertsPanel(self.main_frame)
        self.alerts_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        
        # Panel de estado
        self.status_panel = StatusPanel(self.main_frame)
        self.status_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
    
    def _process_events(self):
        """Procesa eventos de la cola en el hilo principal."""
        if not self.running or self._closing:
            return
        
        try:
            # Procesar todos los eventos en la cola
            while True:
                event = self._event_queue.get_nowait()
                self._handle_event(event)
        except queue.Empty:
            pass
        except Exception as e:
            print(f"[UI] Error procesando eventos: {e}")
        
        # Programar próxima ejecución
        if self.running and not self._closing:
            self.after(500, self._process_events)
    
    def _handle_event(self, event):
        """Maneja un evento desde la cola."""
        try:
            if isinstance(event, TelemetryReceived):
                self.telemetry_panel.add_telemetry(event)
                print(f"[UI] Telemetry: {event.vehicle_id} - {event.speed:.1f} km/h")
                
            elif isinstance(event, AlertRaised):
                self.alerts_panel.add_alert(event)
                print(f"[UI] Alert: {event.alert_id} - {event.message}")
                
            elif isinstance(event, SystemHealthCheck):
                self.status_panel.update_health(event)
                print(f"[UI] Health: uptime={event.uptime_seconds:.1f}s")
                
            elif isinstance(event, SourceFailed):
                self.status_panel.set_error(f"Fallo: {event.source_name}")
                print(f"[UI] Source failed: {event.source_name}")
                
        except Exception as e:
            print(f"[UI] Error manejando evento {event.__class__.__name__}: {e}")
    
    def _on_closing(self):
        """Maneja el cierre de la ventana."""
        # Evitar cierre duplicado
        if self._closing:
            return
        
        self._closing = True
        self.running = False
        
        print("[UI] Cerrando aplicación...")
        
        # Publicar evento de apagado
        if self.event_bus:
            try:
                self.event_bus.publish(
                    ShutdownRequested(shutdown_type="graceful", reason="Window closed")
                )
            except Exception as e:
                print(f"[UI] Error publicando shutdown: {e}")
        
        # Destruir ventana
        try:
            self.destroy()
        except Exception:
            pass
    
    def run(self):
        """Ejecuta la aplicación."""
        try:
            self.mainloop()
        except KeyboardInterrupt:
            print("[UI] Interrupción de teclado")
            self._on_closing()
        except Exception as e:
            print(f"[UI] Error en mainloop: {e}")
            self._on_closing()