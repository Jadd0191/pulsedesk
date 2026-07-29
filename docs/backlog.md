# Backlog Priorizado - PulseDesk

**Proyecto**: PulseDesk RAD  
**Fecha**: 2026-07-29  
**Versión**: 1.0

---

## Épicas

### Épica 1: Fundación (Semanas 1-3)
*Objetivo: Establecer la base arquitectónica del sistema*

- [ ] **TB1**: Timebox y requisitos
- [ ] **TB2**: Catálogo de eventos
- [ ] **TB3**: Esqueleto del event loop

### Épica 2: Visibilidad (Semanas 4-6)
*Objetivo: Tener un prototipo visual funcional y desacoplado*

- [ ] **TB4**: Prototipo visual
- [ ] **TB5**: Emisor de eventos propio
- [ ] **TB6**: Patrones Observer/PubSub

### Épica 3: Entrega (Semanas 7-9)
*Objetivo: Robustez, pruebas y entrega profesional*

- [ ] **TB7**: Estado y concurrencia
- [ ] **TB8**: Testing y profiling
- [ ] **TB9**: Integración y empaquetado

---

## Historias de Usuario (Detalladas)

### US1 - Visualización de Telemetría en Vivo
**Como** operador de logística  
**Quiero** ver la telemetría de los vehículos en tiempo real  
**Para** monitorear su estado y tomar decisiones

**Criterios de Aceptación:**
- [ ] Los datos se actualizan automáticamente cada segundo
- [ ] La UI nunca se congela durante la actualización
- [ ] Se muestra: velocidad, temperatura y ubicación
- [ ] Los datos vienen del archivo de telemetría

**Prioridad**: MUST HAVE

---

### US2 - Recepción de Alertas Automáticas
**Como** operador de logística  
**Quiero** recibir alertas automáticas  
**Para** reaccionar rápidamente a incidentes

**Criterios de Aceptación:**
- [ ] Las alertas aparecen en la lista en <1 segundo
- [ ] Se mantienen las últimas 50 alertas
- [ ] Cada alerta tiene: timestamp, tipo, mensaje
- [ ] Las alertas vienen de la API simulada

**Prioridad**: MUST HAVE

---

### US3 - Indicador de Estado del Sistema
**Como** operador de logística  
**Quiero** conocer el estado general del sistema  
**Para** saber si todo funciona correctamente

**Criterios de Aceptación:**
- [ ] Indicador visual verde/ámbar/rojo
- [ ] Se actualiza automáticamente
- [ ] Verde: todas las fuentes funcionan
- [ ] Ámbar: alguna fuente con problemas
- [ ] Rojo: fuente crítica caída

**Prioridad**: SHOULD HAVE

---

### US4 - Extensibilidad de Fuentes de Datos
**Como** desarrollador  
**Quiero** añadir nuevas fuentes de datos sin modificar la UI  
**Para** facilitar el mantenimiento y la evolución del sistema

**Criterios de Aceptación:**
- [ ] Nueva fuente se añade sin modificar `ui/`
- [ ] La fuente implementa interfaz común
- [ ] Se registra en el event loop automáticamente
- [ ] Los eventos llegan al bus correctamente

**Prioridad**: MUST HAVE

---

### US5 - Apagado Limpio del Sistema
**Como** administrador  
**Quiero** que el sistema se apague limpiamente  
**Para** evitar corrupción de datos y recursos

**Criterios de Aceptación:**
- [ ] Ctrl+C cancela todas las tareas pendientes
- [ ] Cerrar ventana libera todos los recursos
- [ ] No se muestran trazas de error
- [ ] Se registra el apagado en logs

**Prioridad**: MUST HAVE

---

### US6 - Suite de Pruebas Automatizadas
**Como** desarrollador  
**Quiero** tener pruebas automatizadas  
**Para** garantizar la calidad del sistema

**Criterios de Aceptación:**
- [ ] Mínimo 15 pruebas
- [ ] Incluyen pruebas asíncronas
- [ ] Cubren: bus, fuentes, estado, apagado
- [ ] Todas en verde con `pytest -q`

**Prioridad**: SHOULD HAVE

---

### US7 - Personalización de Tema
**Como** operador de logística  
**Quiero** personalizar el tema de la interfaz  
**Para** mayor comodidad visual

**Criterios de Aceptación:**
- [ ] Opción dark/light mode
- [ ] Persistencia de preferencia
- [ ] Cambio en tiempo real

**Prioridad**: COULD HAVE

---

## Tareas Técnicas

### Infraestructura
- [ ] Configurar estructura de carpetas
- [ ] Inicializar repositorio Git
- [ ] Crear `pyproject.toml` con dependencias
- [ ] Configurar `.gitignore`

### Documentación
- [ ] Escribir `plan_rad.md`
- [ ] Escribir `backlog.md`
- [ ] Crear `README.md` inicial

---

## Definición de "Hecho" para el Backlog

Cada historia/tarea se considera "hecha" cuando:
1. ✅ Código implementado y commit subido
2. ✅ Pruebas automatizadas pasan (si aplica)
3. ✅ Documentación actualizada
4. ✅ Demo funcionando (si es visible para usuario)
5. ✅ Revisión de código realizada

---

## Entregables del Backlog

| ID | Historia | Estado | Sprint | Entregable |
|----|----------|--------|--------|------------|
| US1 | Telemetría en vivo | ⏳ Pendiente | S2 | Panel en UI |
| US2 | Alertas automáticas | ⏳ Pendiente | S2 | Lista de alertas |
| US3 | Indicador de estado | ⏳ Pendiente | S3 | Widget de estado |
| US4 | Extensibilidad | ⏳ Pendiente | S2 | Nueva fuente demo |
| US5 | Apagado limpio | ⏳ Pendiente | S3 | Graceful shutdown |
| US6 | Suite de pruebas | ⏳ Pendiente | S3 | pytest suite |
| US7 | Personalización tema | ⏳ Pendiente | S3 | Dark/light mode |

---

**Nota**: Este backlog se revisa y prioriza al inicio de cada sprint.