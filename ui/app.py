"""
Ventana principal simplificada para debugging.
"""

import customtkinter as ctk
from typing import Optional
import threading
import queue

from core.event_bus import EventBus
from core.events import (
    TelemetryReceived,
    AlertRaised,
    SystemHealthCheck,
    SourceFailed,
    SystemState,
    ShutdownRequested
)


class PulseDeskApp(ctk.CTk):
    """Aplicación principal simplificada."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        super().__init__()
        
        self.event_bus = event_bus
        self.running = True
        self._handlers_registered = False
        self._event_queue = queue.Queue()
        
        self.title("PulseDesk RAD - Debug")
        self.geometry("800x600")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Label de estado
        self.status_label = ctk.CTkLabel(
            self,
            text="Esperando eventos...",
            font=ctk.CTkFont(size=16)
        )
        self.status_label.pack(pady=20)
        
        # Textbox para logs
        self.log_text = ctk.CTkTextbox(self, height=400)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.log_text.insert("end", "=== PulseDesk Debug ===\n")
        self.log_text.insert("end", f"EventBus: {event_bus is not None}\n\n")
        
        self._register_handlers()
        self.after(100, self._update_ui)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _register_handlers(self):
        if not self.event_bus:
            self.log_text.insert("end", "ERROR: No event bus\n")
            return
        
        if self._handlers_registered:
            return
        
        self.event_bus.subscribe(TelemetryReceived, self._queue_event)
        self.event_bus.subscribe(SystemHealthCheck, self._queue_event)
        
        self._handlers_registered = True
        self.log_text.insert("end", "Handlers registrados en el bus\n")
        self.log_text.see("end")
    
    def _queue_event(self, event):
        self._event_queue.put(event)
        self.log_text.insert("end", f"[QUEUE] Evento encolado: {event.__class__.__name__}\n")
        self.log_text.see("end")
    
    def _update_ui(self):
        if not self.running:
            return
        
        try:
            while True:
                event = self._event_queue.get_nowait()
                self._process_event(event)
        except queue.Empty:
            pass
        
        if self.running:
            self.after(100, self._update_ui)
    
    def _process_event(self, event):
        if isinstance(event, TelemetryReceived):
            self.log_text.insert("end", f"[TELEMETRY] {event.vehicle_id} - {event.speed:.1f} km/h\n")
            self.status_label.configure(text=f"Último: {event.vehicle_id} - {event.speed:.1f} km/h")
            
        elif isinstance(event, SystemHealthCheck):
            self.log_text.insert("end", f"[HEALTH] Uptime: {event.uptime_seconds:.1f}s\n")
            
        self.log_text.see("end")
    
    def _on_closing(self):
        self.running = False
        if self.event_bus:
            self.event_bus.publish(ShutdownRequested(shutdown_type="graceful"))
        self.destroy()
    
    def set_event_loop(self, loop):
        self._loop = loop
    
    def run(self):
        try:
            self.mainloop()
        except KeyboardInterrupt:
            self._on_closing()