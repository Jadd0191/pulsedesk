# PulseDesk RAD

## Centro de Control de Eventos en Tiempo Real para Logística

### Estado del Proyecto

- ✅ **Fase 1**: Plan RAD y requisitos
- ✅ **Fase 2**: Catálogo de eventos
- ✅ **Fase 3**: Esqueleto del event loop
- ✅ **Fase 4**: Prototipo visual
- ✅ **Fase 5**: Emisor de eventos propio
- ✅ **Fase 6**: Patrones Observer/PubSub
- ✅ **Fase 7**: Estado y concurrencia
- ✅ **Fase 8**: Testing, depuración y profiling
- ⏳ **Fase 9**: Integración y empaquetado (pendiente)

### Pruebas

```bash
# Ejecutar todas las pruebas
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ --cov=core --cov=workers

# Ejecutar solo pruebas del bus
pytest tests/test_event_bus.py -v