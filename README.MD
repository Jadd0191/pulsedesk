# PulseDesk RAD

## Centro de Control de Eventos en Tiempo Real para Logística

### Visión del Proyecto

PulseDesk es una aplicación de escritorio orientada a eventos para monitoreo en tiempo real de operaciones logísticas. Construida con metodología RAD (Desarrollo Rápido de Aplicaciones), garantiza:

- ✅ Interfaz 100% responsiva (nunca se congela)
- ✅ Arquitectura orientada a eventos desacoplada
- ✅ Comunicación mediante bus de eventos propio
- ✅ Operaciones pesadas en hilos separados
- ✅ Apagado limpio y manejo de excepciones

### Tecnologías

- **Lenguaje**: Python 3.11+
- **Asincronía**: asyncio
- **UI**: [PyQt6 / CustomTkinter / Kivy] (a definir)
- **Pruebas**: pytest + pytest-asyncio
- **Profiling**: cProfile

### Estructura del Proyecto
pulsedesk/
├── docs/ # Documentación
│ ├── plan_rad.md # Plan de timeboxes y requisitos
│ └── backlog.md # Backlog priorizado
├── core/ # Núcleo del sistema
│ ├── event_bus.py # Bus de eventos propio
│ ├── events.py # Dataclasses de eventos
│ ├── loop.py # Event loop y ciclo de vida
│ ├── state.py # Store de estado
│ └── sources/ # Fuentes de datos
├── ui/ # Interfaz de usuario
├── workers/ # Tareas en segundo plano
├── tests/ # Suite de pruebas
└── tools/ # Herramientas (profiling, etc.)


### Estado del Proyecto

- ✅ **Fase 1**: Plan RAD y requisitos (completada)
- ⏳ **Fase 2**: Catálogo de eventos (pendiente)
- ⏳ **Fase 3**: Esqueleto del event loop (pendiente)
- ⏳ **Fase 4**: Prototipo visual (pendiente)
- ⏳ **Fase 5**: Emisor de eventos (pendiente)
- ⏳ **Fase 6**: Patrones Observer/PubSub (pendiente)
- ⏳ **Fase 7**: Estado y concurrencia (pendiente)
- ⏳ **Fase 8**: Testing y profiling (pendiente)
- ⏳ **Fase 9**: Integración y empaquetado (pendiente)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/[tu-usuario]/pulsedesk.git
cd pulsedesk

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias (pendiente)
# pip install -e .

