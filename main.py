import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import random

# --- IMPORTACIÓN PARA LA GRÁFICA ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# 1. SIMULACIÓN DEL SISTEMA (TU BACKEND)
# ==========================================
class PulseDeskSystem:
    def __init__(self):
        self.running = True
        self.heartbeat_count = 0
        self.telemetry_count = 0

    def get_heartbeat(self):
        self.heartbeat_count += 1
        return self.heartbeat_count, f"Heartbeat #{self.heartbeat_count} - Uptime: {self.heartbeat_count * 5}s"

    def get_telemetry(self):
        self.telemetry_count += 1
        # Simulamos velocidad (esto en tu código real vendrá de tus sensores)
        current_speed = random.randint(0, 120) 
        return current_speed, f"Telemetry #{self.telemetry_count} | Vel: {current_speed} km/h"

# ==========================================
# 2. INTERFAZ GRÁFICA (EL DASHBOARD)
# ==========================================
class PulseDeskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PulseDesk RAD - Dashboard Visual")
        self.root.geometry("900x700")
        
        # Conexión al sistema simulado
        self.system = PulseDeskSystem()

        # --- PARTE 1: ÁREA DE LOGS (La lista de texto) ---
        self.log_frame = tk.Frame(root)
        self.log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(self.log_frame, text="📋 Logs del Sistema", font=("Arial", 12, "bold")).pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, width=40, height=25, font=("Consolas", 10))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.insert(tk.END, "=== PulseDesk Debug ===\nEventBus: True\nEsperando eventos...\n\n")

        # --- PARTE 2: GRÁFICA EN TIEMPO REAL (La novedad) ---
        self.graph_frame = tk.Frame(root)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(self.graph_frame, text="📈 Velocidad en Tiempo Real", font=("Arial", 12, "bold")).pack(anchor="w")

        # Crear el espacio para el gráfico de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Datos para la gráfica
        self.speed_data = []  # Guarda las velocidades
        self.time_data = []   # Guarda los segundos transcurridos

        # --- PARTE 3: ESTADO ACTUAL (Texto grande abajo) ---
        self.status_label = tk.Label(root, text="Estado: Inicializando...", font=("Arial", 14, "bold"), fg="blue")
        self.status_label.pack(side=tk.BOTTOM, pady=20)

        # --- INICIO DEL MOTOR DE LA INTERFAZ ---
        self.update_gui()

    def log_event(self, message):
        """Añade texto al área de logs con hora real"""
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END) # Baja el scroll automáticamente

    def update_gui(self):
        """Esta función se ejecuta cada 1 segundo y actualiza TODO"""
        
        if not self.system.running:
            return

        # 1. OBTENER DATOS DEL SISTEMA
        hb_count, hb_status = self.system.get_heartbeat()
        current_speed, tele_status = self.system.get_telemetry()

        # 2. ACTUALIZAR EL TEXTO DE ESTADO (Parte de abajo)
        self.status_label.config(text=f"🔴 Heartbeat: {hb_status} | 🚗 {tele_status}")

        # 3. ACTUALIZAR LA GRÁFICA
        # Añadimos el nuevo dato a las listas
        self.speed_data.append(current_speed)
        self.time_data.append(len(self.speed_data)) # El tiempo es simplemente el contador de datos

        # Si la lista se hace muy larga, borramos los datos antiguos para que no se relentice
        if len(self.speed_data) > 50:
            self.speed_data.pop(0)
            self.time_data.pop(0)

        # Dibujar la gráfica
        self.ax.clear()
        self.ax.plot(self.time_data, self.speed_data, color='#00aaff', linewidth=2)
        self.ax.set_ylim(0, 140) # Límite de velocidad (0 a 140 km/h)
        self.ax.set_title("Velocidad del vehículo")
        self.ax.set_ylabel("Km/h")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Este comando es el que "pinta" el gráfico en la ventana
        self.canvas.draw()

        # 4. LOGS EN PANTALLA (Solo cada pocos segundos para no saturar)
        if hb_count % 5 == 0:
            self.log_event(f"Sistema actualizado: {hb_status}")

        # 5. PROGRAMAR LA SIGUIENTE ACTUALIZACIÓN EN 1 SEGUNDO
        self.root.after(1000, self.update_gui)

# ==========================================
# 3. EJECUCIÓN DEL PROGRAMA
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PulseDeskApp(root)
    root.mainloop()