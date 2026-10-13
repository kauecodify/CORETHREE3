"""
CORETHREE3 - Pedidos Sem Fronteiras
Modelo de Envio

Define a estrutura de dados para envios do sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class ShipmentStatus(str, Enum):
    """Status do envio"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY_FOR_PICKUP = "ready_for_pickup"
    IN_TRANSIT = "in_transit"
    AT_HUB = "at_hub"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class ShipmentType(str, Enum):
    """Tipo de envio"""
    STANDARD = "standard"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    FREIGHT = "freight"
    INTERNATIONAL = "international"
    PICKUP = "pickup"


class Waypoint(BaseModel):
    """Ponto de passagem na rota"""
    
    id: str = Field(..., description="Identificador unico do waypoint")
    
    # Localizacao
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    
    # Endereco
    address: Optional[Dict] = Field(None, description="Endereco")
    
    # Tipo
    type: str = Field(..., description="Tipo do waypoint (origin, destination, hub, etc.)")
    
    # Status
    status: str = Field("pending", description="Status do waypoint")
    
    # Timestamp
    estimated_arrival: Optional[datetime] = Field(None, description="Data estimada de chegada")
    actual_arrival: Optional[datetime] = Field(None, description="Data real de chegada")
    
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
                "notes": "Armazem principal"
            }
        }


class Shipment(BaseModel):
    """
    Modelo de Envio
    
    Representa um envio no sistema Pedidos Sem Fronteiras.
    """
    
    id: str = Field(..., description="Identificador unico do envio")
    
    # Relacionamentos
    order_id: str = Field(..., description="ID do pedido associado")
    customer_id: Optional[str] = Field(None, description="ID do cliente")
    
    # Status
    status: ShipmentStatus = Field(ShipmentStatus.PENDING, description="Status do envio")
    
    # Tipo
    shipment_type: ShipmentType = Field(ShipmentType.STANDARD, description="Tipo do envio")
    
    # Transportadora
    carrier: str = Field(..., description="Transportadora")
    carrier_service: Optional[str] = Field(None, description="Servico da transportadora")
    
    # Rastreamento
    tracking_number: Optional[str] = Field(None, description="Numero de rastreamento")
    carrier_tracking_url: Optional[str] = Field(None, description="URL de rastreamento da transportadora")
    
    # Datas
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    processed_at: Optional[datetime] = Field(None, description="Data de processamento")
    picked_up_at: Optional[datetime] = Field(None, description="Data de coleta")
    in_transit_at: Optional[datetime] = Field(None, description="Data de inicio do transito")
    delivered_at: Optional[datetime] = Field(None, description="Data de entrega")
    
    # Datas estimadas
    estimated_pickup_date: Optional[datetime] = Field(None, description="Data estimada de coleta")
    estimated_delivery_date: Optional[datetime] = Field(None, description="Data estimada de entrega")
    
    # Localizacao
    origin: Optional[Dict] = Field(None, description="Local de origem")
    destination: Optional[Dict] = Field(None, description="Local de destino")
    current_location: Optional[Dict] = Field(None, description="Localizacao atual")
    
    # Rota
    route: Optional[List[Waypoint]] = Field(None, description="Rota do envio")
    current_waypoint_index: int = Field(0, description="Indice do waypoint atual")
    
    # Itens
    items: List[Dict] = Field(default_factory=list, description="Itens do envio")
    
    # Dimensoes e peso
    total_weight: float = Field(0.0, description="Peso total em kg")
    total_volume: float = Field(0.0, description="Volume total em m3")
    dimensions: Optional[Dict] = Field(None, description="Dimensoes totais")
    
    # Custos
    shipping_cost: float = Field(0.0, description="Custo de envio")
    insurance_cost: float = Field(0.0, description="Custo de seguro")
    handling_cost: float = Field(0.0, description="Custo de manuseio")
    total_cost: float = Field(0.0, description="Custo total")
    
    # Documentos
    shipping_label_url: Optional[str] = Field(None, description="URL do etiqueta de envio")
    invoice_url: Optional[str] = Field(None, description="URL da nota fiscal")
    packing_slip_url: Optional[str] = Field(None, description="URL do romaneio")
    
    # Assinaturas
    signature_required: bool = Field(False, description="Assinatura requerida")
    signature_url: Optional[str] = Field(None, description="URL da assinatura")
    signed_by: Optional[str] = Field(None, description="Quem assinou")
    signed_at: Optional[datetime] = Field(None, description="Data da assinatura")
    
    # Notificacoes
    notifications: List[Dict] = Field(default_factory=list, description="Historico de notificacoes")
    
    # Historico
    history: List[Dict] = Field(default_factory=list, description="Historico de alteracoes")
    
    # Metadados
    tags: List[str] = Field(default_factory=list, description="Tags do envio")
    notes: Optional[str] = Field(None, description="Notas adicionais")
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    updated_by: Optional[str] = Field(None, description="Usuario que atualizou")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ship-001",
                "order_id": "order-001",
                "customer_id": "cust-001",
                "status": "in_transit",
                "shipment_type": "express",
                "carrier": "Transportadora ABC",
                "carrier_service": "Express 24h",
                "tracking_number": "BR123456789",
                "carrier_tracking_url": "https://transportadora.com/track?number=BR123456789",
                "created_at": "2024-01-15T10:00:00Z",
                "processed_at": "2024-01-15T11:00:00Z",
                "picked_up_at": "2024-01-15T12:00:00Z",
                "in_transit_at": "2024-01-15T13:00:00Z",
                "estimated_delivery_date": "2024-01-16T10:00:00Z",
                "origin": {
                    "street": "Rua das Industrias, 123",
                    "city": "Sao Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "BR"
                },
                "destination": {
                    "street": "Rua das Entregas, 456",
                    "city": "Rio de Janeiro",
                    "state": "RJ",
                    "zip_code": "20040-000",
                    "country": "BR"
                },
                "current_location": {
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "city": "Sao Paulo",
                    "state": "SP"
                },
                "route": [
                    {
                        "id": "wp-001",
                        "latitude": -23.5505,
                        "longitude": -46.6333,
                        "type": "origin",
                        "status": "completed"
                    },
                    {
                        "id": "wp-002",
                        "latitude": -22.9068,
                        "longitude": -43.1729,
                        "type": "hub",
                        "status": "in_transit"
                    },
                    {
                        "id": "wp-003",
                        "latitude": -22.9068,
                        "longitude": -43.1729,
                        "type": "destination",
                        "status": "pending"
                    }
                ],
                "current_waypoint_index": 1,
                "items": [
                    {
                        "product_id": "prod-001",
                        "quantity": 10,
                        "weight": 250.0,
                        "volume": 0.576
                    }
                ],
                "total_weight": 2500.0,
                "total_volume": 5.76,
                "dimensions": {
                    "length": 2.4,
                    "width": 1.6,
                    "height": 1.2
                },
                "shipping_cost": 1500.0,
                "insurance_cost": 250.0,
                "handling_cost": 100.0,
                "total_cost": 1850.0,
                "shipping_label_url": "https://example.com/labels/ship-001.pdf",
                "invoice_url": "https://example.com/invoices/ship-001.pdf",
                "packing_slip_url": "https://example.com/packing-slips/ship-001.pdf",
                "signature_required": True,
                "tags": ["urgent", "industrial"],
                "notes": "Entrega prioritaria",
                "updated_at": "2024-01-15T14:00:00Z",
                "updated_by": "system"
            }
        }
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in ShipmentStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in ShipmentStatus]}')
            return ShipmentStatus(v)
        return v
    
    @validator('shipment_type', pre=True)
    def validate_shipment_type(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [st.value for st in ShipmentType]:
                raise ValueError(f'Tipo de envio invalido: {v}. Tipos validos: {[st.value for st in ShipmentType]}')
            return ShipmentType(v)
        return v
    
    def calculate_totals(self) -> None:
        """Calcula os totais do envio"""
        self.total_cost = self.shipping_cost + self.insurance_cost + self.handling_cost
    
    def is_delivered(self) -> bool:
        """Verifica se o envio foi entregue"""
        return self.status == ShipmentStatus.DELIVERED
    
    def is_in_transit(self) -> bool:
        """Verifica se o envio esta em transito"""
        return self.status in [ShipmentStatus.IN_TRANSIT, ShipmentStatus.AT_HUB, ShipmentStatus.OUT_FOR_DELIVERY]
    
    def get_estimated_time_remaining(self) -> Optional[int]:
        """Calcula o tempo estimado restante em horas"""
        if self.estimated_delivery_date is None:
            return None
        
        now = datetime.utcnow()
        delta = self.estimated_delivery_date - now
        return max(0, int(delta.total_seconds() / 3600))
    
    def get_current_waypoint(self) -> Optional[Waypoint]:
        """Obtem o waypoint atual"""
        if self.route is None or self.current_waypoint_index >= len(self.route):
            return None
        return self.route[self.current_waypoint_index]
    
    def get_next_waypoint(self) -> Optional[Waypoint]:
        """Obtem o proximo waypoint"""
        if self.route is None or self.current_waypoint_index >= len(self.route) - 1:
            return None
        return self.route[self.current_waypoint_index + 1]
    
    def advance_to_next_waypoint(self) -> bool:
        """Avança para o proximo waypoint"""
        if self.route is None or self.current_waypoint_index >= len(self.route) - 1:
            return False
        
        current_waypoint = self.get_current_waypoint()
        if current_waypoint:
            current_waypoint.status = "completed"
            current_waypoint.actual_arrival = datetime.utcnow()
        
        self.current_waypoint_index += 1
        
        next_waypoint = self.get_next_waypoint()
        if next_waypoint:
            next_waypoint.status = "in_transit"
        
        return True
    
    def add_history(self, action: str, user: Optional[str] = None, notes: Optional[str] = None) -> None:
        """Adiciona uma entrada ao historico"""
        self.history.append({
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
            "notes": notes,
            "status": self.status.value,
            "location": self.current_location
        })
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Shipment':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
