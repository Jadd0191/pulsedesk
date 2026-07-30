"""
Panel de alertas en tiempo real.

Muestra las alertas del sistema en una lista.
"""

import customtkinter as ctk
from datetime import datetime
from typing import List, Dict, Optional
from core.events import AlertRaised, AlertSeverity


class AlertsPanel(ctk.CTkFrame):
    """
    Panel que muestra las alertas del sistema.
    """
    
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10)
        
        self.alerts: List[Dict] = []
        self.max_alerts = 50
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del panel."""
        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text="🚨 Alertas del Sistema",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Contador de alertas
        self.count_label = ctk.CTkLabel(
            self,
            text="0 alertas",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.count_label.pack(pady=(0, 10), padx=10, anchor="w")
        
        # Frame para lista de alertas
        self.list_frame = ctk.CTkScrollableFrame(self, height=400)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Etiqueta de "sin alertas"
        self.empty_label = ctk.CTkLabel(
            self.list_frame,
            text="✅ No hay alertas activas",
            text_color="green"
        )
        self.empty_label.pack(pady=50)
    
    def add_alert(self, event: AlertRaised):
        """
        Añade una alerta al panel.
        
        Args:
            event: Evento de alerta
        """
        # Crear diccionario de alerta
        alert = {
            'id': event.alert_id,
            'severity': event.severity,
            'vehicle_id': event.vehicle_id,
            'message': event.message,
            'category': event.category,
            'timestamp': event.timestamp_data,
            'acknowledged': event.acknowledged
        }
        
        # Añadir al principio (más reciente primero)
        self.alerts.insert(0, alert)
        
        # Limitar número de alertas
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop()
        
        # Actualizar UI
        self._update_alerts()
    
    def _update_alerts(self):
        """Actualiza la lista de alertas en la UI."""
        # Limpiar lista
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not self.alerts:
            # Mostrar "sin alertas"
            self.empty_label = ctk.CTkLabel(
                self.list_frame,
                text="✅ No hay alertas activas",
                text_color="green"
            )
            self.empty_label.pack(pady=50)
            self.count_label.configure(text="0 alertas")
            return
        
        # Actualizar contador
        self.count_label.configure(text=f"{len(self.alerts)} alertas")
        
        # Crear filas para cada alerta
        for alert in self.alerts:
            self._create_alert_row(alert)
    
    def _create_alert_row(self, alert: Dict):
        """
        Crea una fila para una alerta.
        
        Args:
            alert: Diccionario con datos de la alerta
        """
        # Frame para la fila
        row_frame = ctk.CTkFrame(self.list_frame, corner_radius=5)
        row_frame.pack(fill="x", pady=2, padx=5)
        
        # Color según severidad
        severity = alert['severity']
        if severity == AlertSeverity.CRITICAL:
            color = "#FF0000"
            severity_text = "CRÍTICA"
        elif severity == AlertSeverity.ERROR:
            color = "#FF6600"
            severity_text = "ERROR"
        elif severity == AlertSeverity.WARNING:
            color = "#FFAA00"
            severity_text = "ADVERTENCIA"
        else:
            color = "#00AAFF"
            severity_text = "INFO"
        
        # Severidad
        severity_label = ctk.CTkLabel(
            row_frame,
            text=severity_text,
            text_color=color,
            font=ctk.CTkFont(weight="bold", size=12)
        )
        severity_label.pack(side="left", padx=5, pady=5)
        
        # Vehículo
        vehicle_label = ctk.CTkLabel(
            row_frame,
            text=f"🚗 {alert['vehicle_id']}",
            font=ctk.CTkFont(size=11)
        )
        vehicle_label.pack(side="left", padx=5, pady=5)
        
        # Mensaje
        message_label = ctk.CTkLabel(
            row_frame,
            text=alert['message'],
            font=ctk.CTkFont(size=11)
        )
        message_label.pack(side="left", padx=5, pady=5)
        
        # Categoría
        category_label = ctk.CTkLabel(
            row_frame,
            text=f"[{alert['category']}]",
            text_color="gray70",
            font=ctk.CTkFont(size=10)
        )
        category_label.pack(side="left", padx=5, pady=5)
        
        # Hora
        if 'timestamp' in alert:
            time_str = alert['timestamp'].strftime("%H:%M:%S")
        else:
            time_str = datetime.now().strftime("%H:%M:%S")
        
        time_label = ctk.CTkLabel(
            row_frame,
            text=time_str,
            text_color="gray60",
            font=ctk.CTkFont(size=10)
        )
        time_label.pack(side="right", padx=5, pady=5)
    
    def update(self):
        """Actualización periódica del panel."""
        pass