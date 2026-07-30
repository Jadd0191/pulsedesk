# PulseDesk RAD

## Centro de Control de Eventos en Tiempo Real para Logística

### Visión del Proyecto

PulseDesk es una aplicación de escritorio orientada a eventos para monitoreo en tiempo real de operaciones logísticas. Construida con metodología RAD (Desarrollo Rápido de Aplicaciones), garantiza:

- Interfaz 100% responsiva (nunca se congela)
- Arquitectura orientada a eventos desacoplada
- Comunicación mediante bus de eventos propio
- Operaciones pesadas en hilos separados
- Apagado limpio y manejo de excepciones

### Tecnologías

- **Lenguaje**: Python 3.11+
- **UI**: CustomTkinter (moderno, dark theme)
- **Asincronía**: asyncio + threading
- **Pruebas**: pytest + pytest-asyncio
- **Profiling**: cProfile
- **Empaquetado**: PyInstaller

### Estructura del Proyecto
pulsedesk/
├── core/ # Núcleo del sistema
│ ├── events.py # Catálogo de eventos
│ ├── event_bus.py # Bus de eventos propio
│ ├── loop.py # Event loop
│ ├── state.py # Store de estado
│ └── sources/ # Fuentes de datos
├── workers/ # Tareas en segundo plano
├── ui/ # Interfaz de usuario
│ └── panels/ # Paneles de la UI
├── tests/ # Suite de pruebas
├── tools/ # Herramientas (profiling)
├── docs/ # Documentación
├── main.py # Punto de entrada
└── requirements.txt # Dependencias


### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/pulsedesk.git
cd pulsedesk

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt