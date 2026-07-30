"""
UI ultra simple para PulseDesk RAD.
"""

import customtkinter as ctk
import queue
from datetime import datetime

from core.event_bus import EventBus
from core.events import (
    TelemetryReceived,
    AlertRaised,
    SystemHealthCheck,
    ShutdownRequested
)
from ui.panels.telemetry_panel import TelemetryPanel
from ui.panels.alerts_panel import AlertsPanel
from ui.panels.status_panel import StatusPanel


class PulseDeskApp(ctk.CTk):
    """Aplicación principal ultra simple."""
    
    def __init__(self, event_bus=None):
        super().__init__()
        
        self.event_bus = event_bus
        self.title("PulseDesk RAD")
        self.geometry("1200x700")
        self.running = True
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Cola de eventos
        self.event_queue = queue.Queue()
        
        # Crear paneles
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.main_frame.grid_columnconfigure(0, weight=2)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        
        self.telemetry_panel = TelemetryPanel(self.main_frame)
        self.telemetry_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=(0, 5))
        
        self.alerts_panel = AlertsPanel(self.main_frame)
        self.alerts_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        
        self.status_panel = StatusPanel(self.main_frame)
        self.status_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
        
        # Suscribirse al bus
        if self.event_bus:
            # Guardar referencias a los métodos para que no se pierdan
            self._on_telemetry = self._handle_telemetry
            self._on_alert = self._handle_alert
            self._on_health = self._handle_health
            
            self.event_bus.subscribe(TelemetryReceived, self._on_telemetry)
            self.event_bus.subscribe(AlertRaised, self._on_alert)
            self.event_bus.subscribe(SystemHealthCheck, self._on_health)
            print("[UI] Suscrito a eventos")
        
        # Iniciar procesamiento de eventos
        self.after(100, self.process_events)
        
        # Configurar cierre
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        print("[UI] UI inicializada")
    
    def _handle_telemetry(self, event):
        """Recibe telemetría."""
        self.event_queue.put(('telemetry', event))
    
    def _handle_alert(self, event):
        """Recibe alerta."""
        self.event_queue.put(('alert', event))
    
    def _handle_health(self, event):
        """Recibe health check."""
        self.event_queue.put(('health', event))
    
    def process_events(self):
        """Procesa eventos en cola."""
        if not self.running:
            return
        
        try:
            count = 0
            while True:
                event_type, event = self.event_queue.get_nowait()
                count += 1
                
                if event_type == 'telemetry':
                    self.telemetry_panel.add_telemetry(event)
                    print(f"[UI] Telemetry: {event.vehicle_id} - {event.speed:.1f} km/h")
                elif event_type == 'alert':
                    self.alerts_panel.add_alert(event)
                    print(f"[UI] Alert: {event.alert_id}")
                elif event_type == 'health':
                    self.status_panel.update_health(event)
                    print(f"[UI] Health: {event.uptime_seconds:.1f}s")
            
            if count > 0:
                print(f"[UI] Procesados {count} eventos")
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"[UI] Error: {e}")
            import traceback
            traceback.print_exc()
        
        self.after(100, self.process_events)
    
    def on_close(self):
        """Cierra la aplicación."""
        print("[UI] Cerrando...")
        self.running = False
        if self.event_bus:
            try:
                self.event_bus.publish(
                    ShutdownRequested(shutdown_type="graceful", reason="Window closed")
                )
            except:
                pass
        self.destroy()