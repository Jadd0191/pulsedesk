"""
Ejecutor de tareas pesadas fuera del hilo de UI.

Mueve operaciones bloqueantes a hilos separados usando run_in_executor.
"""

import asyncio
import time
import random
from typing import Any, Callable, Optional, TypeVar, List, Dict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from core.event_bus import EventBus
from core.events import (
    TaskStarted,
    TaskCompleted,
    TaskFailed,
    TelemetryReceived
)

T = TypeVar('T')


class TaskExecutor:
    """
    Ejecutor de tareas pesadas en hilos separados.
    
    Características:
    - Usa run_in_executor para operaciones bloqueantes
    - Notifica estado de tareas mediante eventos
    - Thread-safe
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None, max_workers: int = 4):
        """
        Inicializa el ejecutor.
        
        Args:
            event_bus: Bus de eventos para notificaciones
            max_workers: Número máximo de hilos
        """
        self.event_bus = event_bus
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._task_counter = 0
        self._running = True
    
    async def execute(self, func: Callable[..., T], *args, 
                      task_name: str = "unknown",
                      description: str = "") -> T:
        """
        Ejecuta una función en un hilo separado.
        
        Args:
            func: Función a ejecutar
            *args: Argumentos de la función
            task_name: Nombre de la tarea
            description: Descripción de la tarea
            
        Returns:
            Resultado de la función
            
        Raises:
            Exception: Si la función falla
        """
        if not self._running:
            raise RuntimeError("Executor is stopped")
        
        task_id = f"task_{self._task_counter:04d}"
        self._task_counter += 1
        
        start_time = datetime.now()
        
        # Notificar inicio
        if self.event_bus:
            self.event_bus.publish(
                TaskStarted(
                    task_id=task_id,
                    task_name=task_name,
                    description=description
                )
            )
        
        try:
            # Ejecutar en hilo separado
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                self.executor,
                func,
                *args
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Notificar éxito
            if self.event_bus:
                self.event_bus.publish(
                    TaskCompleted(
                        task_id=task_id,
                        task_name=task_name,
                        success=True,
                        duration_seconds=duration,
                        result=result
                    )
                )
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            # Notificar fallo
            if self.event_bus:
                self.event_bus.publish(
                    TaskFailed(
                        task_id=task_id,
                        task_name=task_name,
                        error_message=str(e),
                        retry_count=0
                    )
                )
            
            raise e
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Apaga el ejecutor.
        
        Args:
            wait: Esperar a que terminen las tareas
        """
        self._running = False
        self.executor.shutdown(wait=wait)


# ============================================================================
# Ejemplos de tareas pesadas
# ============================================================================

def heavy_computation(n: int = 1000000) -> int:
    """
    Tarea pesada: cálculo de números primos.
    
    Args:
        n: Límite superior para buscar primos
        
    Returns:
        Número de primos encontrados
    """
    count = 0
    for i in range(2, n):
        is_prime = True
        for j in range(2, int(i ** 0.5) + 1):
            if i % j == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count


def simulate_download(url: str, size_mb: float = 10) -> Dict[str, Any]:
    """
    Simula una descarga de datos.
    
    Args:
        url: URL a descargar
        size_mb: Tamaño simulado en MB
        
    Returns:
        Diccionario con resultado
    """
    # Simular latencia de red
    time.sleep(size_mb * 0.1)  # 0.1s por MB
    
    # Simular datos descargados
    data = {
        "url": url,
        "size_mb": size_mb,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }
    
    return data


def process_telemetry_batch(telemetry_data: List[Dict]) -> Dict[str, Any]:
    """
    Procesa un lote de datos de telemetría.
    
    Args:
        telemetry_data: Lista de datos de telemetría
        
    Returns:
        Estadísticas del procesamiento
    """
    if not telemetry_data:
        return {"processed": 0, "errors": 0}
    
    # Simular procesamiento pesado
    time.sleep(0.5)
    
    # Calcular estadísticas
    speeds = [d.get('speed', 0) for d in telemetry_data]
    temps = [d.get('temperature', 0) for d in telemetry_data]
    
    return {
        "processed": len(telemetry_data),
        "avg_speed": sum(speeds) / len(speeds) if speeds else 0,
        "avg_temp": sum(temps) / len(temps) if temps else 0,
        "max_speed": max(speeds) if speeds else 0,
        "min_temp": min(temps) if temps else 0
    }