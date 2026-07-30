"""
Fuente de datos de telemetría desde archivo.

Simula la lectura de un archivo de telemetría que crece en tiempo real.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import AsyncIterator, Optional, List, Dict, Any
from pathlib import Path

from core.sources.base import Source
from core.events import (
    TelemetryReceived,
    TelemetryBatchReceived,
    SourceStarted,
    SourceStopped,
    SourceFailed,
    SystemHealthCheck
)


class TelemetryFileSource(Source):
    """
    Fuente que simula datos de telemetría desde un archivo.
    
    Genera datos aleatorios para vehículos simulando un archivo en crecimiento.
    """
    
    def __init__(
        self, 
        name: str = "TelemetryFile",
        interval: float = 0.5,
        vehicles: int = 5,
        batch_size: int = 3
    ):
        super().__init__(name)
        self.interval = interval
        self.vehicles = vehicles
        self.batch_size = batch_size
        self._task: Optional[asyncio.Task] = None
        self._start_time: Optional[datetime] = None
        self._vehicle_data: Dict[str, Dict] = {}
        self._count = 0
        
        # Inicializar vehículos
        self._init_vehicles()
    
    def _init_vehicles(self):
        """Inicializa los datos de los vehículos."""
        for i in range(1, self.vehicles + 1):
            vehicle_id = f"V-{i:03d}"
            self._vehicle_data[vehicle_id] = {
                'speed': random.uniform(20, 100),
                'temperature': random.uniform(60, 95),
                'latitude': 19.4 + random.uniform(-0.1, 0.1),
                'longitude': -99.1 + random.uniform(-0.1, 0.1),
                'engine_status': random.choice([True, True, True, False]),
                'fuel_level': random.uniform(10, 95)
            }
    
    def _generate_telemetry(self, vehicle_id: str) -> Dict[str, Any]:
        """
        Genera datos de telemetría para un vehículo.
        
        Args:
            vehicle_id: ID del vehículo
            
        Returns:
            Diccionario con datos de telemetría
        """
        data = self._vehicle_data.get(vehicle_id, {})
        
        # Actualizar valores con variaciones aleatorias
        speed = data.get('speed', 50) + random.uniform(-5, 5)
        speed = max(0, min(150, speed))
        
        temperature = data.get('temperature', 75) + random.uniform(-2, 2)
        temperature = max(50, min(110, temperature))
        
        latitude = data.get('latitude', 19.4) + random.uniform(-0.005, 0.005)
        longitude = data.get('longitude', -99.1) + random.uniform(-0.005, 0.005)
        
        engine_status = data.get('engine_status', True)
        # 1% de probabilidad de falla de motor
        if random.random() < 0.01:
            engine_status = False
        
        fuel_level = data.get('fuel_level', 50) - random.uniform(0, 0.5)
        fuel_level = max(0, min(100, fuel_level))
        
        # Guardar para próxima iteración
        self._vehicle_data[vehicle_id] = {
            'speed': speed,
            'temperature': temperature,
            'latitude': latitude,
            'longitude': longitude,
            'engine_status': engine_status,
            'fuel_level': fuel_level
        }
        
        return {
            'vehicle_id': vehicle_id,
            'speed': speed,
            'temperature': temperature,
            'latitude': latitude,
            'longitude': longitude,
            'engine_status': engine_status,
            'fuel_level': fuel_level,
            'timestamp_data': datetime.now()
        }
    
    async def start(self) -> None:
        """Inicia la fuente de telemetría."""
        self._running = True
        self._start_time = datetime.now()
        self._count = 0
        print(f"[{self.name}] Source started with {self.vehicles} vehicles")
    
    async def stop(self) -> None:
        """Detiene la fuente de telemetría."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print(f"[{self.name}] Source stopped")
    
    async def __aiter__(self) -> AsyncIterator[TelemetryReceived]:
        """Genera eventos de telemetría periódicos."""
        try:
            async for event in self._telemetry_loop():
                yield event
        except asyncio.CancelledError:
            print(f"[{self.name}] Telemetry loop cancelled")
            raise
    
    async def _telemetry_loop(self) -> AsyncIterator[TelemetryReceived]:
        """Bucle interno que genera los datos de telemetría."""
        vehicles_list = list(self._vehicle_data.keys())
        
        while self._running:
            try:
                await asyncio.sleep(self.interval)
                
                self._count += 1
                batch = []
                
                # Generar datos para un subconjunto de vehículos
                selected = random.sample(
                    vehicles_list, 
                    min(self.batch_size, len(vehicles_list))
                )
                
                for vehicle_id in selected:
                    data = self._generate_telemetry(vehicle_id)
                    
                    # Crear evento de telemetría
                    event = TelemetryReceived(
                        vehicle_id=data['vehicle_id'],
                        speed=data['speed'],
                        temperature=data['temperature'],
                        latitude=data['latitude'],
                        longitude=data['longitude'],
                        engine_status=data['engine_status'],
                        fuel_level=data['fuel_level'],
                        timestamp_data=data['timestamp_data']
                    )
                    
                    batch.append(event)
                    yield event
                
                # Log cada 10 eventos
                if self._count % 10 == 0:
                    print(f"[{self.name}] Generated {self._count} telemetry events")
                    
            except asyncio.CancelledError:
                print(f"[{self.name}] Telemetry interrupted")
                break
            except Exception as e:
                print(f"[{self.name}] Telemetry error: {e}")
                yield SourceFailed(
                    source_name=self.name,
                    error_message=str(e),
                    retry_count=0,
                    is_critical=False
                )
                await asyncio.sleep(self.interval * 2)