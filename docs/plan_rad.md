# Plan RAD - PulseDesk
## Centro de Control de Eventos en Tiempo Real para Logística

**Proyecto**: PulseDesk RAD  
**Módulo**: 3 - Metodología de desarrollo rápido de aplicaciones con programación orientada a eventos usando Python  
**Fecha**: 2026-07-29  
**Versión**: 1.0  
**Desarrollador**: Jadd

---

## 1. Visión del Proyecto

PulseDesk es un centro de control de escritorio en tiempo real para la empresa de logística PulseLogix. El sistema debe:

- Monitorear fuentes de datos en tiempo real (archivos, APIs, latidos)
- Reaccionar a eventos sin bloquear la interfaz de usuario
- Mostrar telemetría, alertas y estado del sistema en vivo
- Permitir añadir nuevas fuentes de datos sin modificar la UI

**Filosofía**: Prototipa rápido, valida temprano. Nada bloquea el bucle principal.

---

## 2. Timeboxes (9 semanas • 1 por lección) - CUMPLIMIENTO REAL

| # | Timebox | Objetivo | Entregable | Estado |
|---|---------|----------|------------|--------|
| **TB1** | Timebox y requisitos | Definir plan RAD, requisitos y alcance congelado | `docs/plan_rad.md` + `docs/backlog.md` | ✅ COMPLETADO |
| **TB2** | Catálogo de eventos | Definir todos los eventos del sistema como dataclasses | `core/events.py` + tabla evento→emisor→consumidor | ✅ COMPLETADO |
| **TB3** | Esqueleto del event loop | Implementar ciclo de vida: start, run, graceful shutdown | `core/loop.py` funcional | ✅ COMPLETADO |
| **TB4** | Prototipo visual | UI con panel de telemetría, alertas y estado | Ventana funcional + video ≤60s | ✅ COMPLETADO |
| **TB5** | Emisor de eventos propio | Bus de eventos sin librerías externas | `core/event_bus.py` + pruebas | ✅ COMPLETADO |
| **TB6** | Patrones Observer/PubSub | Desacople total mediante topics | Diagrama + fuente nueva | ✅ COMPLETADO |
| **TB7** | Estado y concurrencia | Store de estado + operaciones bloqueantes en hilos | `core/state.py` + `workers/executor.py` | ✅ COMPLETADO |
| **TB8** | Testing y profiling | Suite de pruebas + reporte de profiling | `pytest` verde + reporte antes/después | ✅ COMPLETADO |
| **TB9** | Integración y empaquetado | Demo final y entrega profesional | Repositorio final + video 3-5 min | ✅ COMPLETADO |

---

## 3. Entregables Finales

- [x] Código fuente completo de PulseDesk con la estructura indicada
- [x] README.md con instalación, arquitectura, framework elegido y justificación
- [x] docs/plan_rad.md con los 9 timeboxes y su cumplimiento real
- [x] Tabla de eventos (emisor → consumidor → payload)
- [x] Suite de pruebas y captura de pytest -q en verde
- [x] Reporte de profiling antes/después con la optimización aplicada
- [x] Demo en video de 3–5 minutos (archivo o enlace en el README)
- [x] Historial Git con al menos un commit por fase