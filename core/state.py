"""
Store de estado centralizado para PulseDesk RAD.

Mantiene el estado consistente del sistema y notifica cambios mediante eventos.
Es thread-safe para acceso desde múltiples hilos.
"""

import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from core.events import (
    SystemState,
    SourceStatus,
    TelemetryReceived,
    AlertRaised
)


@dataclass
class VehicleState:
    """Estado de un vehículo."""
    vehicle_id: str
    speed: float = 0.0
    temperature: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    engine_status: bool = False
    fuel_level: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class AlertState:
    """Estado de una alerta."""
    alert_id: str
    severity: str
    vehicle_id: str
    message: str
    category: str
    timestamp: datetime
    acknowledged: bool = False
    cleared: bool = False


@dataclass
class SourceState:
    """Estado de una fuente de datos."""
    name: str
    status: SourceStatus
    last_event: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None


class StateStore:
    """
    Almacén de estado centralizado y thread-safe.
    
    Mantiene el estado de:
    - Vehículos (telemetría)
    - Alertas
    - Fuentes de datos
    - Sistema
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Estado del sistema
        self.system_state: SystemState = SystemState.INITIALIZING
        self.start_time: Optional[datetime] = None
        self.uptime: float = 0.0
        
        # Estado de vehículos
        self.vehicles: Dict[str, VehicleState] = {}
        
        # Estado de alertas
        self.alerts: List[AlertState] = []
        self.max_alerts: int = 100
        
        # Estado de fuentes
        self.sources: Dict[str, SourceState] = {}
        
        # Callbacks para notificaciones
        self._callbacks: List[Callable] = []
    
    # ========================================================================
    # Métodos públicos (thread-safe)
    # ========================================================================
    
    def add_callback(self, callback: Callable) -> None:
        """
        Añade un callback para notificaciones de cambios de estado.
        
        Args:
            callback: Función que recibe (event_type, data)
        """
        with self._lock:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable) -> None:
        """Elimina un callback."""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def _notify(self, event_type: str, data: Any) -> None:
        """Notifica a todos los callbacks."""
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback(event_type, data)
                except Exception as e:
                    print(f"[StateStore] Callback error: {e}")
    
    # ========================================================================
    # Estado del sistema
    # ========================================================================
    
    def set_system_state(self, state: SystemState, reason: Optional[str] = None) -> None:
        """
        Actualiza el estado del sistema.
        
        Args:
            state: Nuevo estado
            reason: Razón del cambio
        """
        with self._lock:
            old_state = self.system_state
            if old_state != state:
                self.system_state = state
                self._notify("system_state", {
                    "old": old_state,
                    "new": state,
                    "reason": reason
                })
    
    def get_system_state(self) -> SystemState:
        """Retorna el estado actual del sistema."""
        with self._lock:
            return self.system_state
    
    def set_uptime(self, uptime: float) -> None:
        """Actualiza el uptime del sistema."""
        with self._lock:
            self.uptime = uptime
            self._notify("uptime", uptime)
    
    # ========================================================================
    # Estado de vehículos
    # ========================================================================
    
    def update_vehicle(self, event: TelemetryReceived) -> None:
        """
        Actualiza el estado de un vehículo con datos de telemetría.
        
        Args:
            event: Evento de telemetría
        """
        with self._lock:
            vehicle_id = event.vehicle_id
            
            if vehicle_id not in self.vehicles:
                self.vehicles[vehicle_id] = VehicleState(vehicle_id=vehicle_id)
            
            vehicle = self.vehicles[vehicle_id]
            vehicle.speed = event.speed
            vehicle.temperature = event.temperature
            vehicle.latitude = event.latitude
            vehicle.longitude = event.longitude
            vehicle.engine_status = event.engine_status
            vehicle.fuel_level = event.fuel_level
            vehicle.last_update = event.timestamp_data
            
            self._notify("vehicle_update", vehicle)
    
    def get_vehicle(self, vehicle_id: str) -> Optional[VehicleState]:
        """Retorna el estado de un vehículo."""
        with self._lock:
            return self.vehicles.get(vehicle_id)
    
    def get_all_vehicles(self) -> List[VehicleState]:
        """Retorna todos los vehículos."""
        with self._lock:
            return list(self.vehicles.values())
    
    def get_vehicle_count(self) -> int:
        """Retorna el número de vehículos."""
        with self._lock:
            return len(self.vehicles)
    
    # ========================================================================
    # Estado de alertas
    # ========================================================================
    
    def add_alert(self, event: AlertRaised) -> None:
        """
        Añade una alerta al estado.
        
        Args:
            event: Evento de alerta
        """
        with self._lock:
            alert = AlertState(
                alert_id=event.alert_id,
                severity=event.severity.value,
                vehicle_id=event.vehicle_id,
                message=event.message,
                category=event.category,
                timestamp=event.timestamp_data
            )
            
            self.alerts.insert(0, alert)  # Más reciente primero
            
            # Limitar número de alertas
            if len(self.alerts) > self.max_alerts:
                self.alerts = self.alerts[:self.max_alerts]
            
            self._notify("alert_added", alert)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Marca una alerta como reconocida.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            True si se encontró la alerta, False en caso contrario
        """
        with self._lock:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    self._notify("alert_acknowledged", alert)
                    return True
            return False
    
    def clear_alert(self, alert_id: str) -> bool:
        """
        Marca una alerta como resuelta.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            True si se encontró la alerta, False en caso contrario
        """
        with self._lock:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.cleared = True
                    self._notify("alert_cleared", alert)
                    return True
            return False
    
    def get_alerts(self, limit: Optional[int] = None) -> List[AlertState]:
        """Retorna las alertas activas."""
        with self._lock:
            active = [a for a in self.alerts if not a.cleared]
            if limit:
                return active[:limit]
            return active
    
    def get_alert_count(self) -> int:
        """Retorna el número de alertas activas."""
        with self._lock:
            return len([a for a in self.alerts if not a.cleared])
    
    # ========================================================================
    # Estado de fuentes
    # ========================================================================
    
    def update_source(self, name: str, status: SourceStatus, 
                      error: Optional[str] = None) -> None:
        """
        Actualiza el estado de una fuente.
        
        Args:
            name: Nombre de la fuente
            status: Nuevo estado
            error: Mensaje de error (opcional)
        """
        with self._lock:
            if name not in self.sources:
                self.sources[name] = SourceState(name=name, status=status)
            
            source = self.sources[name]
            source.status = status
            source.last_event = datetime.now()
            
            if error:
                source.error_count += 1
                source.last_error = error
            
            self._notify("source_update", source)
    
    def get_source_status(self, name: str) -> Optional[SourceState]:
        """Retorna el estado de una fuente."""
        with self._lock:
            return self.sources.get(name)
    
    def get_all_sources(self) -> List[SourceState]:
        """Retorna todas las fuentes."""
        with self._lock:
            return list(self.sources.values())
    
    # ========================================================================
    # Métodos de utilidad
    # ========================================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen del estado del sistema."""
        with self._lock:
            return {
                "system_state": self.system_state.value,
                "uptime": self.uptime,
                "vehicles": len(self.vehicles),
                "alerts": self.get_alert_count(),
                "sources": len(self.sources),
                "start_time": self.start_time.isoformat() if self.start_time else None
            }
    
    def clear(self) -> None:
        """Limpia todo el estado."""
        with self._lock:
            self.vehicles.clear()
            self.alerts.clear()
            self.sources.clear()
            self.system_state = SystemState.INITIALIZING
            self.uptime = 0.0