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

## 2. Timeboxes (9 semanas • 1 por lección)

| # | Timebox | Objetivo | Entregable | Criterio de "Hecho" |
|---|---------|----------|------------|---------------------|
| **TB1** | Timebox y requisitos | Definir plan RAD, requisitos y alcance congelado | `docs/plan_rad.md` + `docs/backlog.md` | Documentos aprobados, alcance congelado y subido a GitHub |
| **TB2** | Catálogo de eventos | Definir todos los eventos del sistema como dataclasses | `core/events.py` + tabla evento→emisor→consumidor | Cada evento tiene payload tipado y documentado |
| **TB3** | Esqueleto del event loop | Implementar ciclo de vida: start, run, graceful shutdown | `core/loop.py` funcional | Arranca, procesa un latido y se apaga sin warnings |
| **TB4** | Prototipo visual | UI con panel de telemetría, alertas y estado | Ventana funcional + video ≤60s | El cliente puede ver reacción a evento en 5 minutos |
| **TB5** | Emisor de eventos propio | Bus de eventos sin librerías externas | `core/event_bus.py` + pruebas | Suscripción/desuscripción sin fugas de memoria |
| **TB6** | Patrones Observer/PubSub | Desacople total mediante topics | Diagrama + fuente nueva | Añadir fuente no requiere modificar `ui/` |
| **TB7** | Estado y concurrencia | Store de estado + operaciones bloqueantes en hilos | `core/state.py` + `workers/executor.py` | UI no se congela durante operaciones pesadas |
| **TB8** | Testing y profiling | Suite de pruebas + reporte de profiling | `pytest` verde + reporte antes/después | ≥15 pruebas, mejora cuantificada documentada |
| **TB9** | Integración y empaquetado | Demo final y entrega profesional | Repositorio final + video 3-5 min | Sistema bajo carga no se congela |

---

## 3. Requisitos Recolectados (Entrevista JAD Simulada)

### Participantes
- **Juan Pérez** - Operador de logística
- **María González** - Supervisora de operaciones
- **Desarrollador** - Tú

### Hallazgos Clave

**Problema actual:**
- El sistema anterior (script con `while True` y `time.sleep()`) congela la ventana al descargar datos
- Se pierden alertas porque el script deja de escuchar mientras procesa archivos grandes
- Nadie se atreve a tocarlo por miedo a romperlo

**Necesidades del operador:**
- Ver telemetría de 40 vehículos en tiempo real (velocidad, temperatura, ubicación)
- Recibir alertas automáticas (fuera de ruta, falla mecánica)
- Conocer el estado general del sistema

**Requerimientos técnicos:**
- Los datos vienen de: archivo de log (crece cada segundo), API interna (latencia variable)
- Se necesita un "latido" para saber que el sistema está vivo
- Si una fuente falla, debe mostrar error pero no detener todo
- Añadir nueva fuente no debe requerir reescribir la UI
- Ctrl+C o cerrar ventana debe cancelar tareas y liberar recursos sin errores

**Frecuencia de entregas:**
- Demo funcional al final de cada semana (timebox)
- No se acepta "big bang" al final

---

## 4. Clasificación MoSCoW

### MUST HAVE (Esencial para el MVP)
- UI responsiva (nunca se congela)
- Bus de eventos propio (desacople entre módulos)
- 3 fuentes de datos (telemetría, alertas, latido)
- Apagado limpio (cancelación de tareas sin errores)
- Panel de telemetría en vivo (actualización automática)
- Lista de alertas (últimas 50 en tiempo real)

### SHOULD HAVE (Importante pero no crítico)
- Indicador de estado (verde/ámbar/rojo)
- Suite de pruebas (≥15 pruebas asíncronas)
- Profiling documentado (reporte antes/después)
- Logging estructurado

### COULD HAVE (Deseable si hay tiempo)
- Empaquetado con PyInstaller (ejecutable standalone)
- Personalización de temas (dark/light mode)
- Configuración de fuentes vía archivo JSON

### WON'T HAVE (Fuera de alcance para v1.0)
- Histórico de datos en base de datos
- Dashboard con gráficos históricos
- Exportación de reportes en PDF
- Múltiples perfiles de usuario
- Notificaciones por email
- API REST externa

---

## 5. Backlog Priorizado

### Sprint 1 (Semanas 1-3): Fundación
- [ ] TB1: Plan RAD y requisitos
- [ ] TB2: Catálogo de eventos
- [ ] TB3: Esqueleto del event loop

### Sprint 2 (Semanas 4-6): Visibilidad y desacople
- [ ] TB4: Prototipo visual (framework RAD)
- [ ] TB5: Emisor de eventos propio
- [ ] TB6: Patrones Observer/PubSub

### Sprint 3 (Semanas 7-9): Robustez y entrega
- [ ] TB7: Estado y concurrencia
- [ ] TB8: Testing y profiling
- [ ] TB9: Integración y demo final

---

## 6. Historias de Usuario (Priorizadas)

| ID | Historia | Prioridad | Criterios de Aceptación |
|----|----------|-----------|--------------------------|
| **US1** | Como operador, quiero ver telemetría en vivo para monitorear los vehículos | MUST | Los datos se actualizan automáticamente, UI nunca se congela |
| **US2** | Como operador, quiero recibir alertas automáticas para reaccionar a incidentes | MUST | Las alertas aparecen en la lista en <1s, se mantienen las últimas 50 |
| **US3** | Como operador, quiero conocer el estado del sistema para saber si todo funciona | MUST | Indicador visual verde/ámbar/rojo, se actualiza automáticamente |
| **US4** | Como desarrollador, quiero añadir fuentes de datos sin tocar la UI para facilitar el mantenimiento | MUST | Nueva fuente se añade sin modificar `ui/` |
| **US5** | Como administrador, quiero que el sistema se apague limpiamente para evitar corrupción de datos | MUST | Ctrl+C o cerrar ventana cancela tareas y libera recursos |
| **US6** | Como desarrollador, quiero pruebas automatizadas para garantizar la calidad | SHOULD | Suite con ≥15 pruebas, todas en verde |
| **US7** | Como operador, quiero personalizar el tema de la interfaz para mayor comodidad | COULD | Opción dark/light mode funcional |

---

## 7. Riesgos y Mitigación

| Riesgo | Impacto | Probabilidad | Mitigación |
|--------|---------|--------------|------------|
| **Scope creep** | Alto | Media | Alcance congelado, espiral futura documentada, validación semanal |
| **UI bloqueante** | Alto | Alta | Todo trabajo >50ms va a hilos, pruebas de responsividad |
| **Fugas de memoria** | Medio | Media | Uso de weakref en suscripciones, pruebas específicas |
| **Manejo de excepciones** | Alto | Media | Cada handler tiene try/except, el bus no se detiene |
| **Rendimiento** | Medio | Baja | Profiling obligatorio, optimización medida |

---

## 8. Espiral Futura (Fuera de alcance v1.0)

- Dashboard con gráficos históricos (requiere base de datos)
- Persistencia en SQLite para auditoría
- Exportación de reportes en PDF
- Múltiples perfiles de usuario y autenticación
- Notificaciones por email/Slack
- Temas personalizables (solo dark/light mode básico en v1.0)
- API REST para consultas externas
- Configuración dinámica de fuentes vía UI

---

## 9. Criterios de Éxito del Proyecto

1. ✅ Demo funcional al final de cada timebox
2. ✅ UI nunca se congela bajo carga (medido con profiling)
3. ✅ Añadir una fuente nueva no requiere tocar `ui/`
4. ✅ Suite de pruebas con ≥15 casos, todos verdes
5. ✅ Reporte de profiling muestra mejora cuantificada
6. ✅ Apagado limpio sin trazas de error
7. ✅ Video demo de 3-5 minutos mostrando el sistema en acción

---

## 10. Aprobación

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| Desarrollador | [Jadd] | 2026-07-29 | ✅ |
| Cliente (simulado) | PulseLogix | 2026-07-29 | ✅ |

**Alcance congelado**: Cualquier cambio requiere aprobación formal y ajuste de timeboxes.