"""
Panel de estado del sistema.

Muestra el estado general y la salud del sistema.
"""

import customtkinter as ctk
from datetime import datetime
from typing import Optional
from core.events import SystemHealthCheck, SystemState


class StatusPanel(ctk.CTkFrame):
    """
    Panel que muestra el estado del sistema.
    """
    
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10)
        
        self.state: SystemState = SystemState.INITIALIZING
        self.health_status: str = "unknown"
        self.uptime: float = 0.0
        self.error_message: Optional[str] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del panel."""
        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text="🔄 Estado del Sistema",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Frame para estado
        self.status_frame = ctk.CTkFrame(self, corner_radius=10)
        self.status_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Indicador de estado
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="🟡 Inicializando...",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_indicator.pack(pady=(15, 5))
        
        # Detalles
        self.details_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.details_frame.pack(fill="x", padx=15, pady=5)
        
        # Uptime
        self.uptime_label = ctk.CTkLabel(
            self.details_frame,
            text="⏱️ Uptime: 0.0s",
            font=ctk.CTkFont(size=12)
        )
        self.uptime_label.pack(anchor="w", pady=2)
        
        # Componentes
        self.components_label = ctk.CTkLabel(
            self.details_frame,
            text="📦 Componentes: cargando...",
            font=ctk.CTkFont(size=12)
        )
        self.components_label.pack(anchor="w", pady=2)
        
        # Errores
        self.error_label = ctk.CTkLabel(
            self.details_frame,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        self.error_label.pack(anchor="w", pady=2)
    
    def set_state(self, state: SystemState):
        """
        Actualiza el estado del sistema.
        
        Args:
            state: Nuevo estado del sistema
        """
        self.state = state
        
        # Actualizar indicador
        if state == SystemState.RUNNING:
            self.status_indicator.configure(text="🟢 Sistema Operando", text_color="green")
        elif state == SystemState.INITIALIZING:
            self.status_indicator.configure(text="🟡 Inicializando...", text_color="yellow")
        elif state == SystemState.DEGRADED:
            self.status_indicator.configure(text="🟠 Sistema Degradado", text_color="orange")
        elif state == SystemState.ERROR:
            self.status_indicator.configure(text="🔴 Error en el Sistema", text_color="red")
        elif state == SystemState.SHUTTING_DOWN:
            self.status_indicator.configure(text="🟤 Apagando...", text_color="gray")
        elif state == SystemState.SHUTDOWN:
            self.status_indicator.configure(text="⚫ Apagado", text_color="gray")
    
    def update_health(self, event: SystemHealthCheck):
        """
        Actualiza la salud del sistema.
        
        Args:
            event: Evento de health check
        """
        self.health_status = event.status
        self.uptime = event.uptime_seconds
        
        # Actualizar uptime
        self.uptime_label.configure(text=f"⏱️ Uptime: {self.uptime:.1f}s")
        
        # Actualizar componentes
        if event.components_status:
            comps = ", ".join([f"{k}: {v}" for k, v in event.components_status.items()])
            self.components_label.configure(text=f"📦 Componentes: {comps}")
        
        # Actualizar indicador según estado
        if event.status == "healthy":
            if self.state == SystemState.RUNNING:
                self.status_indicator.configure(text="🟢 Sistema Saludable", text_color="green")
        elif event.status == "degraded":
            self.status_indicator.configure(text="🟠 Sistema Degradado", text_color="orange")
        elif event.status == "unhealthy":
            self.status_indicator.configure(text="🔴 Sistema No Saludable", text_color="red")
    
    def set_error(self, error_message: str):
        """
        Muestra un mensaje de error.
        
        Args:
            error_message: Mensaje de error
        """
        self.error_message = error_message
        self.error_label.configure(text=f"❌ {error_message}")
    
    def update(self):
        """Actualización periódica del panel."""
        pass