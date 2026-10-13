"""
CORETHREE3 - Pedidos Sem Fronteiras
Modelo de Rota

Define a estrutura de dados para rotas de entrega do sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class RouteStatus(str, Enum):
    """Status da rota"""
    PLANNED = "planned"
    OPTIMIZED = "optimized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Waypoint(BaseModel):
    """
    Modelo de Ponto de Passagem
    
    Representa um ponto de passagem em uma rota de entrega.
    """
    
    id: str = Field(..., description="Identificador unico do waypoint")
    
    # Localizacao
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    
    # Endereco
    address: Optional[Dict] = Field(None, description="Endereco")
    
    # Tipo do waypoint
    type: str = Field(..., description="Tipo do waypoint (origin, destination, hub, etc.)")
    
    # Status
    status: str = Field("pending", description="Status do waypoint")
    
    # Timing
    estimated_arrival: Optional[datetime] = Field(None, description="Data estimada de chegada")
    actual_arrival: Optional[datetime] = Field(None, description="Data real de chegada")
    estimated_departure: Optional[datetime] = Field(None, description="Data estimada de saida")
    actual_departure: Optional[datetime] = Field(None, description="Data real de saida")
    
    # Dados do pedido
    order_id: Optional[str] = Field(None, description="ID do pedido associado")
    shipment_id: Optional[str] = Field(None, description="ID do envio associado")
    
    # Tempo de parada
    estimated_stop_time: Optional[int] = Field(None, description="Tempo de parada estimado em minutos")
    actual_stop_time: Optional[int] = Field(None, description="Tempo de parada real em minutos")
    
    # Metadados
    notes: Optional[str] = Field(None, description="Notas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "wp-001",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "address": {
                    "street": "Rua das Industrias, 123",
                    "city": "Sao Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "BR"
                },
                "type": "origin",
                "status": "completed",
                "estimated_arrival": "2024-01-15T08:00:00Z",
                "actual_arrival": "2024-01-15T08:05:00Z",
                "estimated_departure": "2024-01-15T08:30:00Z",
                "actual_departure": "2024-01-15T08:35:00Z",
                "order_id": "order-001",
                "shipment_id": "ship-001",
                "estimated_stop_time": 30,
                "actual_stop_time": 35,
                "notes": "Armazem principal"
            }
        }


class Route(BaseModel):
    """
    Modelo de Rota
    
    Representa uma rota de entrega no sistema Pedidos Sem Fronteiras.
    """
    
    id: str = Field(..., description="Identificador unico da rota")
    
    # Informacoes basicas
    name: str = Field(..., description="Nome da rota")
    route_number: str = Field(..., description="Numero da rota")
    
    # Status
    status: RouteStatus = Field(RouteStatus.PLANNED, description="Status da rota")
    
    # Veiculo e motorista
    vehicle_id: Optional[str] = Field(None, description="ID do veiculo")
    vehicle_type: Optional[str] = Field(None, description="Tipo do veiculo")
    driver_id: Optional[str] = Field(None, description="ID do motorista")
    driver_name: Optional[str] = Field(None, description="Nome do motorista")
    
    # Waypoints
    waypoints: List[Waypoint] = Field(default_factory=list, description="Lista de waypoints")
    current_waypoint_index: int = Field(0, description="Indice do waypoint atual")
    
    # Timing
    start_time: Optional[datetime] = Field(None, description="Hora de inicio")
    end_time: Optional[datetime] = Field(None, description="Hora de termino")
    estimated_duration: Optional[int] = Field(None, description="Duracao estimada em minutos")
    actual_duration: Optional[int] = Field(None, description="Duracao real em minutos")
    
    # Datas
    date: datetime = Field(default_factory=datetime.utcnow, description="Data da rota")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    
    # Distancias
    total_distance: float = Field(0.0, description="Distancia total em km")
    estimated_distance: float = Field(0.0, description="Distancia estimada em km")
    
    # Custos
    fuel_cost: Optional[float] = Field(None, description="Custo de combustivel")
    toll_cost: Optional[float] = Field(None, description="Custo de pedagio")
    driver_cost: Optional[float] = Field(None, description="Custo do motorista")
    total_cost: Optional[float] = Field(None, description="Custo total")
    
    # Capacidade
    max_weight: Optional[float] = Field(None, description="Peso maximo em kg")
    max_volume: Optional[float] = Field(None, description="Volume maximo em m3")
    current_weight: float = Field(0.0, description="Peso atual em kg")
    current_volume: float = Field(0.0, description="Volume atual em m3")
    
    # Metricas
    efficiency_score: Optional[float] = Field(None, description="Score de eficiencia")
    
    # Metadados
    tags: List[str] = Field(default_factory=list, description="Tags da rota")
    notes: Optional[str] = Field(None, description="Notas adicionais")
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    updated_by: Optional[str] = Field(None, description="Usuario que atualizou")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "route-001",
                "name": "Rota Sao Paulo - Rio",
                "route_number": "RT-2024-001",
                "status": "in_progress",
                "vehicle_id": "veh-001",
                "vehicle_type": "truck",
                "driver_id": "drv-001",
                "driver_name": "Joao Silva",
                "waypoints": [
                    {
                        "id": "wp-001",
                        "latitude": -23.5505,
                        "longitude": -46.6333,
                        "type": "origin",
                        "status": "completed",
                        "address": {
                            "street": "Rua das Industrias, 123",
                            "city": "Sao Paulo",
                            "state": "SP",
                            "zip_code": "01234-567",
                            "country": "BR"
                        },
                        "estimated_arrival": "2024-01-15T08:00:00Z",
                        "actual_arrival": "2024-01-15T08:05:00Z",
                        "estimated_departure": "2024-01-15T08:30:00Z",
                        "actual_departure": "2024-01-15T08:35:00Z",
                        "order_id": None,
                        "shipment_id": None
                    },
                    {
                        "id": "wp-002",
                        "latitude": -22.9068,
                        "longitude": -43.1729,
                        "type": "destination",
                        "status": "in_progress",
                        "address": {
                            "street": "Rua das Entregas, 456",
                            "city": "Rio de Janeiro",
                            "state": "RJ",
                            "zip_code": "20040-000",
                            "country": "BR"
                        },
                        "estimated_arrival": "2024-01-15T14:00:00Z",
                        "order_id": "order-001",
                        "shipment_id": "ship-001",
                        "estimated_stop_time": 30
                    }
                ],
                "current_waypoint_index": 1,
                "start_time": "2024-01-15T08:00:00Z",
                "end_time": "2024-01-15T15:00:00Z",
                "estimated_duration": 420,
                "date": "2024-01-15T00:00:00Z",
                "total_distance": 430.5,
                "estimated_distance": 450.0,
                "fuel_cost": 500.0,
                "toll_cost": 150.0,
                "driver_cost": 800.0,
                "total_cost": 1450.0,
                "max_weight": 10000.0,
                "max_volume": 50.0,
                "current_weight": 2500.0,
                "current_volume": 5.76,
                "efficiency_score": 0.92,
                "tags": ["long-haul", "priority"],
                "notes": "Rota prioritaria para cliente VIP",
                "updated_at": "2024-01-15T14:00:00Z",
                "updated_by": "system"
            }
        }
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in RouteStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in RouteStatus]}')
            return RouteStatus(v)
        return v
    
    def calculate_totals(self) -> None:
        """Calcula os totais da rota"""
        self.total_cost = (self.fuel_cost or 0) + (self.toll_cost or 0) + (self.driver_cost or 0)
        
        # Calcular distancia total
        if len(self.waypoints) > 1:
            total_distance = 0.0
            for i in range(len(self.waypoints) - 1):
                wp1 = self.waypoints[i]
                wp2 = self.waypoints[i + 1]
                # Calcular distancia entre waypoints (simplificado)
                distance = self._calculate_distance(
                    (wp1.latitude, wp1.longitude),
                    (wp2.latitude, wp2.longitude)
                )
                total_distance += distance
            self.total_distance = total_distance
    
    def _calculate_distance(self, point1: tuple, point2: tuple) -> float:
        """Calcula distancia entre dois pontos (simplificado)"""
        # Implementacao simplificada - usar Haversine para precisao real
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        # Distancia euclidiana (para demonstracao)
        return ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111.32  # Aprox. 111 km por grau
    
    def get_current_waypoint(self) -> Optional[Waypoint]:
        """Obtem o waypoint atual"""
        if self.current_waypoint_index >= len(self.waypoints):
            return None
        return self.waypoints[self.current_waypoint_index]
    
    def get_next_waypoint(self) -> Optional[Waypoint]:
        """Obtem o proximo waypoint"""
        if self.current_waypoint_index >= len(self.waypoints) - 1:
            return None
        return self.waypoints[self.current_waypoint_index + 1]
    
    def advance_to_next_waypoint(self) -> bool:
        """Avança para o proximo waypoint"""
        if self.current_waypoint_index >= len(self.waypoints) - 1:
            return False
        
        current_waypoint = self.get_current_waypoint()
        if current_waypoint:
            current_waypoint.status = "completed"
            current_waypoint.actual_departure = datetime.utcnow()
        
        self.current_waypoint_index += 1
        
        next_waypoint = self.get_next_waypoint()
        if next_waypoint:
            next_waypoint.status = "in_progress"
            next_waypoint.estimated_arrival = datetime.utcnow()
        
        # Verificar se a rota foi concluida
        if self.current_waypoint_index >= len(self.waypoints):
            self.status = RouteStatus.COMPLETED
            self.end_time = datetime.utcnow()
            self.actual_duration = int((self.end_time - self.start_time).total_seconds() / 60)
        
        return True
    
    def add_waypoint(self, waypoint: Waypoint) -> None:
        """Adiciona um waypoint a rota"""
        self.waypoints.append(waypoint)
        self.calculate_totals()
    
    def remove_waypoint(self, waypoint_id: str) -> bool:
        """Remove um waypoint da rota"""
        for i, waypoint in enumerate(self.waypoints):
            if waypoint.id == waypoint_id:
                self.waypoints.pop(i)
                self.calculate_totals()
                return True
        return False
    
    def is_completed(self) -> bool:
        """Verifica se a rota esta concluida"""
        return self.status == RouteStatus.COMPLETED
    
    def is_in_progress(self) -> bool:
        """Verifica se a rota esta em andamento"""
        return self.status == RouteStatus.IN_PROGRESS
    
    def get_progress(self) -> float:
        """Calcula o progresso da rota em percentual"""
        if not self.waypoints:
            return 0.0
        
        completed = sum(1 for wp in self.waypoints if wp.status == "completed")
        return (completed / len(self.waypoints)) * 100
    
    def get_remaining_distance(self) -> float:
        """Calcula a distancia restante"""
        if self.current_waypoint_index >= len(self.waypoints):
            return 0.0
        
        remaining_distance = 0.0
        for i in range(self.current_waypoint_index, len(self.waypoints) - 1):
            wp1 = self.waypoints[i]
            wp2 = self.waypoints[i + 1]
            remaining_distance += self._calculate_distance(
                (wp1.latitude, wp1.longitude),
                (wp2.latitude, wp2.longitude)
            )
        
        return remaining_distance
    
    def get_estimated_time_remaining(self) -> Optional[int]:
        """Calcula o tempo estimado restante em minutos"""
        if self.current_waypoint_index >= len(self.waypoints):
            return 0
        
        remaining_distance = self.get_remaining_distance()
        
        # Velocidade media (simplificada)
        if self.actual_duration and self.total_distance:
            speed_km_per_min = self.total_distance / (self.actual_duration or 1)
        else:
            speed_km_per_min = 0.8  # 48 km/h
        
        if speed_km_per_min == 0:
            return None
        
        return int(remaining_distance / speed_km_per_min)
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Route':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
