"""
Prueba directa de la UI sin asyncio.
"""

import customtkinter as ctk
import threading
import time
import random
from datetime import datetime

from core.event_bus import EventBus
from core.events import TelemetryReceived
from ui.panels.telemetry_panel import TelemetryPanel


class TestApp(ctk.CTk):
    """Aplicación de prueba."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Prueba UI - PulseDesk")
        self.geometry("800x600")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear panel de telemetría
        self.telemetry_panel = TelemetryPanel(self)
        self.telemetry_panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botón para agregar datos
        self.btn = ctk.CTkButton(
            self,
            text="Agregar Telemetría",
            command=self.add_telemetry
        )
        self.btn.pack(pady=10)
        
        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(self, text="Esperando...")
        self.status_label.pack(pady=5)
        
        # Contador
        self.counter = 0
        
        # Iniciar auto-generación
        self.after(1000, self.auto_add)
    
    def add_telemetry(self):
        """Agrega un dato de telemetría."""
        self.counter += 1
        vehicle_id = f"V-{self.counter:03d}"
        
        event = TelemetryReceived(
            vehicle_id=vehicle_id,
            speed=random.uniform(20, 100),
            temperature=random.uniform(60, 95),
            latitude=19.4 + random.uniform(-0.1, 0.1),
            longitude=-99.1 + random.uniform(-0.1, 0.1),
            engine_status=random.choice([True, True, True, False]),
            fuel_level=random.uniform(10, 95),
            timestamp_data=datetime.now()
        )
        
        self.telemetry_panel.add_telemetry(event)
        self.status_label.configure(text=f"Último: {vehicle_id}")
    
    def auto_add(self):
        """Auto-agrega datos cada segundo."""
        if self.counter < 10:
            self.add_telemetry()
            self.after(1000, self.auto_add)
        else:
            self.status_label.configure(text="¡10 vehículos agregados!")
    
    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = TestApp()
    app.run()