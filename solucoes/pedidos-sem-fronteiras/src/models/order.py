"""
CORETHREE3 - Pedidos Sem Fronteiras
Modelo de Pedido

Define a estrutura de dados para pedidos do sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class OrderStatus(str, Enum):
    """Status do pedido"""
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    IN_PRODUCTION = "in_production"
    READY_TO_SHIP = "ready_to_ship"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"


class OrderPriority(str, Enum):
    """Prioridade do pedido"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OrderItem(BaseModel):
    """Item de um pedido"""
    product_id: str = Field(..., description="ID do produto")
    product_name: Optional[str] = Field(None, description="Nome do produto")
    quantity: int = Field(..., description="Quantidade")
    unit_price: float = Field(..., description="Preco unitario")
    total_price: float = Field(..., description="Preco total do item")
    
    # Informacoes adicionais
    specifications: Optional[Dict] = Field(None, description="Especificacoes do produto")
    
    # Status de producao
    production_status: Optional[str] = Field(None, description="Status de producao do item")
    machine_id: Optional[str] = Field(None, description="ID da maquina responsavel")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod-001",
                "product_name": "Motor Eletrico 55kW",
                "quantity": 10,
                "unit_price": 15000.0,
                "total_price": 150000.0,
                "specifications": {
                    "power": "55kW",
                    "voltage": "440V",
                    "type": "AC"
                },
                "production_status": "completed",
                "machine_id": "machine-001"
            }
        }


class Order(BaseModel):
    """
    Modelo de Pedido
    
    Representa um pedido no sistema Pedidos Sem Fronteiras.
    """
    
    id: str = Field(..., description="Identificador unico do pedido")
    
    # Informacoes basicas
    customer_id: str = Field(..., description="ID do cliente")
    order_number: str = Field(..., description="Numero do pedido")
    
    # Status e prioridade
    status: OrderStatus = Field(OrderStatus.DRAFT, description="Status do pedido")
    priority: OrderPriority = Field(OrderPriority.MEDIUM, description="Prioridade do pedido")
    
    # Itens do pedido
    items: List[OrderItem] = Field(default_factory=list, description="Itens do pedido")
    
    # Datas
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    confirmed_at: Optional[datetime] = Field(None, description="Data de confirmacao")
    processing_started_at: Optional[datetime] = Field(None, description="Data de inicio do processamento")
    production_started_at: Optional[datetime] = Field(None, description="Data de inicio da producao")
    ready_to_ship_at: Optional[datetime] = Field(None, description="Data de pronto para envio")
    shipped_at: Optional[datetime] = Field(None, description="Data de envio")
    delivered_at: Optional[datetime] = Field(None, description="Data de entrega")
    cancelled_at: Optional[datetime] = Field(None, description="Data de cancelamento")
    
    # Datas estimadas
    estimated_confirmation_date: Optional[datetime] = Field(None, description="Data estimada de confirmacao")
    estimated_processing_date: Optional[datetime] = Field(None, description="Data estimada de processamento")
    estimated_production_date: Optional[datetime] = Field(None, description="Data estimada de producao")
    estimated_shipment_date: Optional[datetime] = Field(None, description="Data estimada de envio")
    estimated_delivery_date: Optional[datetime] = Field(None, description="Data estimada de entrega")
    
    # Valores
    subtotal: float = Field(0.0, description="Subtotal")
    tax: float = Field(0.0, description="Imposto")
    shipping_cost: float = Field(0.0, description="Custo de envio")
    discount: float = Field(0.0, description="Desconto")
    total: float = Field(0.0, description="Total")
    
    # Pagamento
    payment_method: Optional[str] = Field(None, description="Metodo de pagamento")
    payment_status: Optional[str] = Field(None, description="Status do pagamento")
    payment_reference: Optional[str] = Field(None, description="Referencia do pagamento")
    
    # Envio
    shipment_id: Optional[str] = Field(None, description="ID do envio")
    tracking_number: Optional[str] = Field(None, description="Numero de rastreamento")
    carrier: Optional[str] = Field(None, description="Transportadora")
    
    # Enderecos
    billing_address: Optional[Dict] = Field(None, description="Endereco de cobranca")
    shipping_address: Optional[Dict] = Field(None, description="Endereco de entrega")
    
    # Contatos
    customer_email: Optional[str] = Field(None, description="Email do cliente")
    customer_phone: Optional[str] = Field(None, description="Telefone do cliente")
    
    # Notificacoes
    notifications: List[Dict] = Field(default_factory=list, description="Historico de notificacoes")
    
    # Historico
    history: List[Dict] = Field(default_factory=list, description="Historico de alteracoes")
    
    # Integracao com DNA de Maquinas
    machine_ids: List[str] = Field(default_factory=list, description="IDs das maquinas envolvidas")
    production_status: Optional[str] = Field(None, description="Status geral de producao")
    
    # Metadados
    tags: List[str] = Field(default_factory=list, description="Tags do pedido")
    notes: Optional[str] = Field(None, description="Notas adicionais")
    
    # Atualizacoes
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    updated_by: Optional[str] = Field(None, description="Usuario que atualizou")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "order-001",
                "customer_id": "cust-001",
                "order_number": "ORD-2024-001",
                "status": "confirmed",
                "priority": "high",
                "items": [
                    {
                        "product_id": "prod-001",
                        "product_name": "Motor Eletrico 55kW",
                        "quantity": 10,
                        "unit_price": 15000.0,
                        "total_price": 150000.0
                    },
                    {
                        "product_id": "prod-002",
                        "product_name": "Bomba Hidraulica",
                        "quantity": 5,
                        "unit_price": 8000.0,
                        "total_price": 40000.0
                    }
                ],
                "created_at": "2024-01-15T10:00:00Z",
                "confirmed_at": "2024-01-15T10:30:00Z",
                "processing_started_at": "2024-01-15T11:00:00Z",
                "estimated_delivery_date": "2024-02-01T00:00:00Z",
                "subtotal": 190000.0,
                "tax": 34200.0,
                "shipping_cost": 5000.0,
                "discount": 5000.0,
                "total": 224200.0,
                "payment_method": "credit_card",
                "payment_status": "paid",
                "payment_reference": "payment-001",
                "shipment_id": "ship-001",
                "tracking_number": "BR123456789",
                "carrier": "Transportadora ABC",
                "shipping_address": {
                    "street": "Rua das Industrias, 123",
                    "city": "Sao Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "BR"
                },
                "billing_address": {
                    "street": "Rua das Industrias, 123",
                    "city": "Sao Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "BR"
                },
                "customer_email": "cliente@empresa.com",
                "customer_phone": "+55 11 99999-9999",
                "machine_ids": ["machine-001", "machine-002"],
                "production_status": "in_progress",
                "tags": ["urgent", "industrial"],
                "notes": "Pedido prioritario para cliente VIP",
                "updated_at": "2024-01-15T12:00:00Z",
                "updated_by": "system"
            }
        }
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in OrderStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in OrderStatus]}')
            return OrderStatus(v)
        return v
    
    @validator('priority', pre=True)
    def validate_priority(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [p.value for p in OrderPriority]:
                raise ValueError(f'Prioridade invalida: {v}. Prioridades validas: {[p.value for p in OrderPriority]}')
            return OrderPriority(v)
        return v
    
    def calculate_totals(self) -> None:
        """Calcula os totais do pedido"""
        self.subtotal = sum(item.total_price for item in self.items)
        self.total = self.subtotal + self.tax + self.shipping_cost - self.discount
    
    def is_paid(self) -> bool:
        """Verifica se o pedido esta pago"""
        return self.payment_status == "paid"
    
    def is_completed(self) -> bool:
        """Verifica se o pedido esta concluido"""
        return self.status in [OrderStatus.DELIVERED, OrderStatus.RETURNED, OrderStatus.REFUNDED]
    
    def is_cancelled(self) -> bool:
        """Verifica se o pedido esta cancelado"""
        return self.status == OrderStatus.CANCELLED
    
    def is_in_production(self) -> bool:
        """Verifica se o pedido esta em producao"""
        return self.status in [OrderStatus.IN_PRODUCTION, OrderStatus.PROCESSING]
    
    def get_estimated_time_remaining(self) -> Optional[int]:
        """Calcula o tempo estimado restante em dias"""
        if self.estimated_delivery_date is None:
            return None
        
        now = datetime.utcnow()
        delta = self.estimated_delivery_date - now
        return max(0, int(delta.total_seconds() / (24 * 3600)))
    
    def add_item(self, item: OrderItem) -> None:
        """Adiciona um item ao pedido"""
        self.items.append(item)
        self.calculate_totals()
    
    def remove_item(self, product_id: str) -> bool:
        """Remove um item do pedido"""
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                self.items.pop(i)
                self.calculate_totals()
                return True
        return False
    
    def add_history(self, action: str, user: Optional[str] = None, notes: Optional[str] = None) -> None:
        """Adiciona uma entrada ao historico"""
        self.history.append({
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
            "notes": notes,
            "status": self.status.value
        })
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Order':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
