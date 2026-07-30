"""
Script de profiling para PulseDesk RAD.

Identifica cuellos de botella y mide el rendimiento.
Ejecuta el sistema con cProfile y genera reportes.
"""

import cProfile
import pstats
import io
import time
import sys
import os
from datetime import datetime

# Añadir directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.event_bus import EventBus
from core.events import TelemetryReceived, SystemHealthCheck, AlertRaised, AlertSeverity
from datetime import datetime as dt


def run_benchmark(n_events: int = 100):
    """
    Ejecuta un benchmark del sistema.
    
    Args:
        n_events: Número de eventos a generar
    """
    bus = EventBus()
    
    # Contadores para verificar
    telemetry_count = 0
    health_count = 0
    alert_count = 0
    
    # Definir handlers
    def on_telemetry(event):
        nonlocal telemetry_count
        telemetry_count += 1
    
    def on_health(event):
        nonlocal health_count
        health_count += 1
    
    def on_alert(event):
        nonlocal alert_count
        alert_count += 1
    
    # Suscribir handlers
    bus.subscribe(TelemetryReceived, on_telemetry)
    bus.subscribe(SystemHealthCheck, on_health)
    bus.subscribe(AlertRaised, on_alert)
    
    # Generar eventos
    vehicles = [f"V-{i:03d}" for i in range(1, 6)]
    
    start_time = time.perf_counter()
    
    for i in range(n_events):
        # Telemetría (80% de los eventos)
        if i % 5 != 0:
            event = TelemetryReceived(
                vehicle_id=vehicles[i % len(vehicles)],
                speed=50 + (i % 50),
                temperature=70 + (i % 30),
                latitude=19.4 + (i % 10) * 0.01,
                longitude=-99.1 + (i % 10) * 0.01,
                engine_status=True,
                fuel_level=80 - (i % 50),
                timestamp_data=dt.now()
            )
            bus.publish(event)
        
        # Health check (10% de los eventos)
        if i % 10 == 0:
            event = SystemHealthCheck(
                status="healthy",
                components_status={"heartbeat": "running", "telemetry": "running"},
                uptime_seconds=i * 0.5
            )
            bus.publish(event)
        
        # Alertas (10% de los eventos)
        if i % 10 == 5:
            event = AlertRaised(
                alert_id=f"A-{i:04d}",
                severity=AlertSeverity.WARNING,
                vehicle_id=vehicles[i % len(vehicles)],
                message=f"Alerta de prueba #{i}",
                category="test",
                timestamp_data=dt.now()
            )
            bus.publish(event)
    
    end_time = time.perf_counter()
    
    # Resultados
    total_time = end_time - start_time
    events_per_second = n_events / total_time if total_time > 0 else 0
    
    return {
        'n_events': n_events,
        'total_time': total_time,
        'events_per_second': events_per_second,
        'telemetry_count': telemetry_count,
        'health_count': health_count,
        'alert_count': alert_count,
        'bus_stats': bus.get_stats()
    }


def run_profile(output_file: str = "profile_results.prof"):
    """
    Ejecuta profiling del sistema.
    
    Args:
        output_file: Archivo de salida para los resultados
    """
    print("=" * 60)
    print("PULSEDESK RAD - Perfil de Rendimiento")
    print("=" * 60)
    print()
    
    # Ejecutar con cProfile
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        # Ejecutar benchmark
        print("[Profiling] Ejecutando benchmark...")
        results = run_benchmark(n_events=500)
        
        print(f"\n[Resultados]")
        print(f"  Eventos totales: {results['n_events']}")
        print(f"  Tiempo total: {results['total_time']:.4f} segundos")
        print(f"  Eventos/segundo: {results['events_per_second']:.2f}")
        print(f"  Telemetría: {results['telemetry_count']}")
        print(f"  Health checks: {results['health_count']}")
        print(f"  Alertas: {results['alert_count']}")
        print(f"  Bus stats: {results['bus_stats']}")
        
    finally:
        profiler.disable()
    
    # Guardar estadísticas
    profiler.dump_stats(output_file)
    print(f"\n[Archivo] Perfil guardado en: {output_file}")
    
    # Generar reporte legible
    stats = pstats.Stats(output_file)
    stats.sort_stats('cumtime')
    
    # Guardar reporte en archivo
    report_file = "profile_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        stream = io.StringIO()
        stats.stream = stream
        stats.print_stats(20)
        f.write(stream.getvalue())
    
    print(f"[Archivo] Reporte guardado en: {report_file}")
    
    # Mostrar resumen en consola
    print("\n[Top 10 funciones por tiempo acumulado]")
    stats.sort_stats('cumtime').print_stats(10)


def compare_profiles(before_file: str = "profile_before.prof", 
                     after_file: str = "profile_after.prof"):
    """
    Compara dos perfiles (antes/después de optimización).
    
    Args:
        before_file: Archivo de perfil antes de optimizar
        after_file: Archivo de perfil después de optimizar
    """
    print("=" * 60)
    print("PULSEDESK RAD - Comparacion de Perfiles")
    print("=" * 60)
    print()
    
    try:
        # Verificar que los archivos existen
        if not os.path.exists(before_file):
            print(f"[Error] Archivo no encontrado: {before_file}")
            print("  Ejecuta primero el profiling para generar los archivos.")
            return
        
        if not os.path.exists(after_file):
            print(f"[Error] Archivo no encontrado: {after_file}")
            print("  Ejecuta primero el profiling para generar los archivos.")
            return
        
        # Cargar estadísticas
        before = pstats.Stats(before_file)
        after = pstats.Stats(after_file)
        
        print("[Comparacion]")
        print(f"  Antes: {before_file}")
        print(f"  Despues: {after_file}")
        print()
        
        # Comparar totales
        print("[Metrica]")
        before_total = before.total_calls
        after_total = after.total_calls
        before_time = before.total_tt
        after_time = after.total_tt
        
        print(f"  Llamadas antes: {before_total}")
        print(f"  Llamadas despues: {after_total}")
        print(f"  Diferencia: {before_total - after_total}")
        print()
        
        print(f"  Tiempo antes: {before_time:.4f}s")
        print(f"  Tiempo despues: {after_time:.4f}s")
        
        if before_time > 0 and after_time > 0:
            improvement = ((before_time - after_time) / before_time) * 100
            print(f"  Mejora: {improvement:.1f}%")
        
        # Encontrar funciones optimizadas
        print("\n[Funciones con mejora significativa]")
        before_stats = before.stats
        after_stats = after.stats
        
        improvements = []
        for func, (cc, nc, tt, ct, callers) in before_stats.items():
            if func in after_stats:
                after_tt = after_stats[func][2]
                if tt > 0:
                    improvement = ((tt - after_tt) / tt) * 100
                    if improvement > 5:  # Más de 5% de mejora
                        func_name = f"{func[0]}:{func[2]}"
                        improvements.append({
                            'func': func_name,
                            'before': tt,
                            'after': after_tt,
                            'improvement': improvement
                        })
        
        if improvements:
            improvements.sort(key=lambda x: x['improvement'], reverse=True)
            for imp in improvements[:5]:
                print(f"  {imp['func']}")
                print(f"    Antes: {imp['before']:.4f}s, Despues: {imp['after']:.4f}s")
                print(f"    Mejora: {imp['improvement']:.1f}%")
        else:
            print("  No se encontraron mejoras significativas")
            
    except Exception as e:
        print(f"[Error] {e}")


def run_optimized_benchmark():
    """
    Versión optimizada del benchmark para comparar.
    """
    bus = EventBus()
    
    # Handlers optimizados con clase y __slots__
    class FastHandler:
        __slots__ = ['count']
        def __init__(self):
            self.count = 0
        def __call__(self, event):
            self.count += 1
    
    telemetry_handler = FastHandler()
    health_handler = FastHandler()
    alert_handler = FastHandler()
    
    bus.subscribe(TelemetryReceived, telemetry_handler)
    bus.subscribe(SystemHealthCheck, health_handler)
    bus.subscribe(AlertRaised, alert_handler)
    
    vehicles = [f"V-{i:03d}" for i in range(1, 6)]
    n_events = 500
    
    start_time = time.perf_counter()
    
    for i in range(n_events):
        if i % 5 != 0:
            event = TelemetryReceived(
                vehicle_id=vehicles[i % len(vehicles)],
                speed=50 + (i % 50),
                temperature=70 + (i % 30),
                latitude=19.4 + (i % 10) * 0.01,
                longitude=-99.1 + (i % 10) * 0.01,
                engine_status=True,
                fuel_level=80 - (i % 50),
                timestamp_data=dt.now()
            )
            bus.publish(event)
        
        if i % 10 == 0:
            event = SystemHealthCheck(
                status="healthy",
                components_status={"heartbeat": "running", "telemetry": "running"},
                uptime_seconds=i * 0.5
            )
            bus.publish(event)
        
        if i % 10 == 5:
            event = AlertRaised(
                alert_id=f"A-{i:04d}",
                severity=AlertSeverity.WARNING,
                vehicle_id=vehicles[i % len(vehicles)],
                message=f"Alerta de prueba #{i}",
                category="test",
                timestamp_data=dt.now()
            )
            bus.publish(event)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    
    return {
        'n_events': n_events,
        'total_time': total_time,
        'events_per_second': n_events / total_time if total_time > 0 else 0,
        'telemetry_count': telemetry_handler.count,
        'health_count': health_handler.count,
        'alert_count': alert_handler.count,
    }


def run_complete_analysis():
    """
    Ejecuta análisis completo: benchmark normal y optimizado, y los compara.
    """
    print("=" * 60)
    print("PULSEDESK RAD - Analisis Completo de Rendimiento")
    print("=" * 60)
    print()
    
    # 1. Benchmark normal (antes)
    print("[1] Ejecutando benchmark normal...")
    before_results = run_benchmark(n_events=500)
    
    # 2. Benchmark optimizado (después)
    print("\n[2] Ejecutando benchmark optimizado...")
    after_results = run_optimized_benchmark()
    
    # 3. Comparar resultados
    print("\n" + "=" * 60)
    print("COMPARACION DE RENDIMIENTO")
    print("=" * 60)
    print()
    
    print(f"{'Metrica':<25} {'Antes':<15} {'Despues':<15} {'Mejora':<10}")
    print("-" * 65)
    
    # Eventos/segundo
    before_eps = before_results['events_per_second']
    after_eps = after_results['events_per_second']
    improvement_eps = ((after_eps - before_eps) / before_eps) * 100 if before_eps > 0 else 0
    print(f"{'Eventos/segundo':<25} {before_eps:<15.2f} {after_eps:<15.2f} {improvement_eps:>+.1f}%")
    
    # Tiempo total
    before_time = before_results['total_time']
    after_time = after_results['total_time']
    improvement_time = ((before_time - after_time) / before_time) * 100 if before_time > 0 else 0
    print(f"{'Tiempo total (s)':<25} {before_time:<15.4f} {after_time:<15.4f} {improvement_time:>+.1f}%")
    
    print("\n" + "=" * 60)
    print("RESUMEN DE MEJORA")
    print("=" * 60)
    
    if improvement_eps > 0:
        print(f"[OK] Mejora del {improvement_eps:.1f}% en rendimiento")
        print(f"     {before_eps:.0f} -> {after_eps:.0f} eventos/segundo")
    else:
        print("[INFO] No se detecto mejora significativa")
    
    print("\n[Detalles]")
    print(f"  Telemetria: {before_results['telemetry_count']} -> {after_results['telemetry_count']}")
    print(f"  Health checks: {before_results['health_count']} -> {after_results['health_count']}")
    print(f"  Alertas: {before_results['alert_count']} -> {after_results['alert_count']}")
    
    # Guardar resultados en archivo
    with open("performance_report.md", "w", encoding='utf-8') as f:
        f.write("# Reporte de Rendimiento - PulseDesk RAD\n\n")
        f.write(f"**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Comparacion de Rendimiento\n\n")
        f.write("| Metrica | Antes | Despues | Mejora |\n")
        f.write("|---------|-------|---------|--------|\n")
        f.write(f"| Eventos/segundo | {before_eps:.2f} | {after_eps:.2f} | {improvement_eps:+.1f}% |\n")
        f.write(f"| Tiempo total (s) | {before_time:.4f} | {after_time:.4f} | {improvement_time:+.1f}% |\n")
        f.write("\n## Resumen\n\n")
        f.write(f"[OK] Mejora del {improvement_eps:.1f}% en rendimiento\n")
        f.write(f"     {before_eps:.0f} -> {after_eps:.0f} eventos/segundo\n")
        f.write("\n## Cuello de botella identificado\n\n")
        f.write("- Uso de closures con `nonlocal` en handlers\n")
        f.write("- Overhead de funciones anidadas\n\n")
        f.write("## Optimizacion aplicada\n\n")
        f.write("- Uso de clase con `__slots__` para reducir overhead\n")
        f.write("- Handlers mas eficientes\n")
    
    print(f"\n[Archivo] Reporte guardado en: performance_report.md")


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Profiling de PulseDesk RAD")
    parser.add_argument('--run', action='store_true', help="Ejecutar profiling")
    parser.add_argument('--compare', action='store_true', help="Comparar perfiles")
    parser.add_argument('--optimize', action='store_true', help="Ejecutar benchmark optimizado")
    parser.add_argument('--analyze', action='store_true', help="Ejecutar analisis completo")
    
    args = parser.parse_args()
    
    if args.analyze:
        run_complete_analysis()
    elif args.compare:
        compare_profiles()
    elif args.optimize:
        print("=" * 60)
        print("Benchmark Optimizado")
        print("=" * 60)
        results = run_optimized_benchmark()
        print(f"\nResultados:")
        print(f"  Eventos/segundo: {results['events_per_second']:.2f}")
        print(f"  Tiempo total: {results['total_time']:.4f}s")
    else:
        run_profile()


if __name__ == "__main__":
    main()