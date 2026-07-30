"""
Ventana principal de PulseDesk RAD usando CustomTkinter.

Esta es la aplicación de escritorio que muestra:
- Panel de telemetría
- Lista de alertas
- Indicador de estado del sistema
"""

import customtkinter as ctk
from typing import Optional
import asyncio
import threading
from datetime import datetime

from core.events import (
    TelemetryReceived,
    AlertRaised,
    SystemHealthCheck,
    SourceFailed,
    SystemState
)
from ui.panels.telemetry_panel import TelemetryPanel
from ui.panels.alerts_panel import AlertsPanel
from ui.panels.status_panel import StatusPanel


class PulseDeskApp(ctk.CTk):
    """
    Aplicación principal de PulseDesk.
    
    Gestiona la ventana y los paneles de la interfaz.
    """
    
    def __init__(self, event_loop=None):
        """
        Inicializa la aplicación.
        
        Args:
            event_loop: Referencia al event loop del sistema
        """
        super().__init__()
        
        self.event_loop = event_loop
        self.running = True
        self._loop = None  # Almacenar referencia al loop asyncio
        
        # Configurar ventana
        self.title("PulseDesk RAD - Centro de Control de Eventos")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear layout
        self._create_layout()
        
        # Iniciar actualización de UI
        self.after(100, self._update_ui)
        
        # Configurar cierre de ventana
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def set_event_loop(self, loop):
        """Establece el event loop asyncio."""
        self._loop = loop
    
    def _create_layout(self):
        """Crea la estructura de la ventana."""
        # Frame principal con padding
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid: 2 columnas, 2 filas
        self.main_frame.grid_columnconfigure(0, weight=2)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        
        # Panel izquierdo: Telemetría (ocupa columna 0, filas 0-1)
        self.telemetry_panel = TelemetryPanel(self.main_frame)
        self.telemetry_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=(0, 5))
        
        # Panel superior derecho: Alertas
        self.alerts_panel = AlertsPanel(self.main_frame)
        self.alerts_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        
        # Panel inferior derecho: Estado
        self.status_panel = StatusPanel(self.main_frame)
        self.status_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
    
    def _update_ui(self):
        """Actualiza la UI desde el event loop (thread-safe)."""
        if not self.running:
            return
        
        try:
            # Actualizar paneles
            self.telemetry_panel.update()
            self.alerts_panel.update()
            self.status_panel.update()
        except Exception as e:
            print(f"[UI] Error updating: {e}")
        
        # Programar próxima actualización
        if self.running:
            self.after(100, self._update_ui)
    
    def _on_closing(self):
        """Maneja el cierre de la ventana."""
        print("[UI] Window closing...")
        self.running = False
        
        # Solicitar apagado al event loop
        if self.event_loop and not self.event_loop.shutdown_requested:
            try:
                # Usar el loop almacenado si existe
                if self._loop and not self._loop.is_closed():
                    # Crear tarea de apagado en el loop correcto
                    asyncio.run_coroutine_threadsafe(
                        self.event_loop.shutdown(),
                        self._loop
                    )
                else:
                    print("[UI] No event loop available for shutdown")
            except Exception as e:
                print(f"[UI] Error requesting shutdown: {e}")
        
        # Destruir ventana
        self.destroy()
    
    def handle_event(self, event) -> None:
        """
        Maneja un evento del sistema (llamado desde el event loop).
        
        Args:
            event: Evento a procesar
        """
        # Actualizar paneles según el tipo de evento
        if isinstance(event, TelemetryReceived):
            self.telemetry_panel.add_telemetry(event)
            
        elif isinstance(event, AlertRaised):
            self.alerts_panel.add_alert(event)
            
        elif isinstance(event, SystemHealthCheck):
            self.status_panel.update_health(event)
            
        elif isinstance(event, SourceFailed):
            self.status_panel.set_error(f"Source failed: {event.source_name}")
            
        elif isinstance(event, SystemState):
            self.status_panel.set_state(event)
    
    def run(self):
        """Ejecuta la aplicación."""
        try:
            self.mainloop()
        except KeyboardInterrupt:
            print("[UI] Interrupted by user")
            self._on_closing()