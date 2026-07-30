"""
Panel de telemetría en tiempo real.

Muestra los datos de los vehículos en una tabla.
"""

import customtkinter as ctk
from datetime import datetime
from typing import Dict, List, Optional
from core.events import TelemetryReceived


class TelemetryPanel(ctk.CTkFrame):
    """
    Panel que muestra la telemetría de los vehículos.
    """
    
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10)
        
        self.telemetry_data: Dict[str, Dict] = {}
        self.max_items = 20
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del panel."""
        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text="📊 Telemetría en Vivo",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Subtítulo
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Datos de vehículos en tiempo real",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.subtitle_label.pack(pady=(0, 10), padx=10, anchor="w")
        
        # Frame para tabla
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Headers
        headers = ["ID", "Velocidad", "Temp", "Motor", "Combustible"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="gray70"
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Configurar columnas
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(2, weight=1)
        self.table_frame.grid_columnconfigure(3, weight=1)
        self.table_frame.grid_columnconfigure(4, weight=1)
        
        # Contenedor para filas de datos
        self.data_frame = ctk.CTkScrollableFrame(self.table_frame, height=300)
        self.data_frame.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=(0, 0))
        
        # Configurar grid del data_frame
        self.data_frame.grid_columnconfigure(0, weight=1)
        self.data_frame.grid_columnconfigure(1, weight=1)
        self.data_frame.grid_columnconfigure(2, weight=1)
        self.data_frame.grid_columnconfigure(3, weight=1)
        self.data_frame.grid_columnconfigure(4, weight=1)
        
        # Fila para cada vehículo
        self.data_rows: Dict[str, List[ctk.CTkLabel]] = {}
        
        # Etiqueta de "sin datos"
        self.empty_label = ctk.CTkLabel(
            self.data_frame,
            text="Esperando datos de telemetría...",
            text_color="gray50"
        )
        self.empty_label.grid(row=0, column=0, columnspan=5, pady=50)
    
    def add_telemetry(self, event: TelemetryReceived):
        """
        Añade un dato de telemetría al panel.
        
        Args:
            event: Evento de telemetría recibido
        """
        vehicle_id = event.vehicle_id
        
        # Almacenar datos
        self.telemetry_data[vehicle_id] = {
            'speed': event.speed,
            'temperature': event.temperature,
            'engine_status': event.engine_status,
            'fuel_level': event.fuel_level,
            'timestamp': event.timestamp_data
        }
        
        # Actualizar UI
        self._update_vehicle_row(vehicle_id)
    
    def _update_vehicle_row(self, vehicle_id: str):
        """
        Actualiza la fila de un vehículo en la tabla.
        
        Args:
            vehicle_id: ID del vehículo
        """
        data = self.telemetry_data.get(vehicle_id)
        if not data:
            return
        
        # Ocultar etiqueta de "sin datos"
        self.empty_label.grid_remove()
        
        # Si ya existe la fila, actualizar
        if vehicle_id in self.data_rows:
            row_widgets = self.data_rows[vehicle_id]
            
            # Actualizar valores
            row_widgets[1].configure(text=f"{data['speed']:.1f} km/h")
            row_widgets[2].configure(text=f"{data['temperature']:.1f}°C")
            
            # Motor
            engine_status = "🟢 ON" if data['engine_status'] else "🔴 OFF"
            row_widgets[3].configure(text=engine_status)
            
            # Combustible
            fuel = data['fuel_level']
            fuel_color = "green" if fuel > 50 else "orange" if fuel > 20 else "red"
            row_widgets[4].configure(text=f"{fuel:.1f}%", text_color=fuel_color)
            
        else:
            # Crear nueva fila
            row = len(self.data_rows)
            
            # ID del vehículo
            id_label = ctk.CTkLabel(self.data_frame, text=vehicle_id, font=ctk.CTkFont(weight="bold"))
            id_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # Velocidad
            speed_label = ctk.CTkLabel(self.data_frame, text=f"{data['speed']:.1f} km/h")
            speed_label.grid(row=row, column=1, padx=5, pady=2, sticky="w")
            
            # Temperatura
            temp_label = ctk.CTkLabel(self.data_frame, text=f"{data['temperature']:.1f}°C")
            temp_label.grid(row=row, column=2, padx=5, pady=2, sticky="w")
            
            # Motor
            engine_status = "🟢 ON" if data['engine_status'] else "🔴 OFF"
            engine_label = ctk.CTkLabel(self.data_frame, text=engine_status)
            engine_label.grid(row=row, column=3, padx=5, pady=2, sticky="w")
            
            # Combustible
            fuel = data['fuel_level']
            fuel_color = "green" if fuel > 50 else "orange" if fuel > 20 else "red"
            fuel_label = ctk.CTkLabel(self.data_frame, text=f"{fuel:.1f}%", text_color=fuel_color)
            fuel_label.grid(row=row, column=4, padx=5, pady=2, sticky="w")
            
            # Guardar referencias
            self.data_rows[vehicle_id] = [id_label, speed_label, temp_label, engine_label, fuel_label]
        
        # Limitar número de filas
        if len(self.data_rows) > self.max_items:
            # Eliminar la fila más antigua
            oldest_key = next(iter(self.data_rows))
            for widget in self.data_rows[oldest_key]:
                widget.destroy()
            del self.data_rows[oldest_key]
            del self.telemetry_data[oldest_key]
    
    def update(self):
        """Actualización periódica del panel."""
        pass