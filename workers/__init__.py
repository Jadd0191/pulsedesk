"""
Workers - Tareas en segundo plano para PulseDesk RAD.
"""

from .executor import TaskExecutor, heavy_computation, simulate_download, process_telemetry_batch

__all__ = [
    'TaskExecutor',
    'heavy_computation',
    'simulate_download',
    'process_telemetry_batch',
]