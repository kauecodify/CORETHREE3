"""
CORETHREE3 - Pedidos Sem Fronteiras
Modelo de Estoque

Define a estrutura de dados para controle de estoque do sistema.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Inventory(BaseModel):
    """
    Modelo de Estoque
    
    Representa o controle de estoque de um produto no sistema Pedidos Sem Fronteiras.
    """
    
    # Identificacao
    id: str = Field(..., description="Identificador unico do registro de estoque")
    product_id: str = Field(..., description="ID do produto")
    product_name: Optional[str] = Field(None, description="Nome do produto")
    
    # Localizacao
    warehouse_id: str = Field(..., description="ID do armazem")
    warehouse_name: Optional[str] = Field(None, description="Nome do armazem")
    location: Optional[str] = Field(None, description="Localizacao no armazem")
    
    # Quantidades
    quantity: int = Field(0, description="Quantidade disponivel")
    reserved_quantity: int = Field(0, description="Quantidade reservada")
    available_quantity: int = Field(0, description="Quantidade disponivel para venda")
    
    # Niveis de estoque
    minimum_level: int = Field(0, description="Nivel minimo de estoque")
    maximum_level: int = Field(0, description="Nivel maximo de estoque")
    reorder_point: int = Field(0, description="Ponto de reabastecimento")
    reorder_quantity: int = Field(0, description="Quantidade para reabastecimento")
    
    # Status
    status: str = Field("in_stock", description="Status do estoque")
    
    # Custos
    unit_cost: Optional[float] = Field(None, description="Custo unitario")
    total_cost: Optional[float] = Field(None, description="Custo total")
    
    # Datas
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    last_received: Optional[datetime] = Field(None, description="Data do ultimo recebimento")
    last_issued: Optional[datetime] = Field(None, description="Data da ultima saida")
    next_expected_delivery: Optional[datetime] = Field(None, description="Data da proxima entrega esperada")
    
    # Movimentacoes
    movements: List[Dict] = Field(default_factory=list, description="Historico de movimentacoes")
    
    # Metadados
    tags: List[str] = Field(default_factory=list, description="Tags do estoque")
    notes: Optional[str] = Field(None, description="Notas adicionais")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "inv-001",
                "product_id": "prod-001",
                "product_name": "Motor Eletrico 55kW",
                "warehouse_id": "wh-001",
                "warehouse_name": "Armazem Central",
                "location": "A-12-03",
                "quantity": 50,
                "reserved_quantity": 10,
                "available_quantity": 40,
                "minimum_level": 10,
                "maximum_level": 100,
                "reorder_point": 20,
                "reorder_quantity": 30,
                "status": "in_stock",
                "unit_cost": 10000.0,
                "total_cost": 500000.0,
                "last_updated": "2024-01-15T12:00:00Z",
                "last_received": "2024-01-10T08:00:00Z",
                "last_issued": "2024-01-14T10:00:00Z",
                "next_expected_delivery": "2024-02-01T00:00:00Z",
                "movements": [
                    {
                        "type": "receipt",
                        "quantity": 30,
                        "date": "2024-01-10T08:00:00Z",
                        "reference": "PO-001",
                        "notes": "Recebimento do fornecedor"
                    },
                    {
                        "type": "issue",
                        "quantity": 5,
                        "date": "2024-01-14T10:00:00Z",
                        "reference": "order-001",
                        "notes": "Saida para pedido"
                    }
                ],
                "tags": ["critical", "high-value"],
                "notes": "Produto com alta rotacao"
            }
        }
    
    def calculate_available_quantity(self) -> int:
        """Calcula a quantidade disponivel"""
        self.available_quantity = self.quantity - self.reserved_quantity
        return self.available_quantity
    
    def is_below_minimum(self) -> bool:
        """Verifica se o estoque esta abaixo do nivel minimo"""
        return self.quantity < self.minimum_level
    
    def is_below_reorder_point(self) -> bool:
        """Verifica se o estoque esta abaixo do ponto de reabastecimento"""
        return self.quantity <= self.reorder_point
    
    def needs_reorder(self) -> bool:
        """Verifica se e necessario reabastecer"""
        return self.is_below_reorder_point() and self.next_expected_delivery is None
    
    def get_reorder_quantity(self) -> int:
        """Obtem a quantidade para reabastecimento"""
        if self.needs_reorder():
            return self.reorder_quantity
        return 0
    
    def adjust_quantity(self, quantity: int, movement_type: str, reference: Optional[str] = None, notes: Optional[str] = None) -> None:
        """Ajusta a quantidade do estoque"""
        old_quantity = self.quantity
        
        if movement_type == "receipt":
            self.quantity += quantity
        elif movement_type == "issue":
            self.quantity -= quantity
            if self.quantity < 0:
                self.quantity = 0
        
        # Adicionar ao historico
        self.movements.append({
            "type": movement_type,
            "quantity": quantity,
            "date": datetime.utcnow().isoformat(),
            "reference": reference,
            "notes": notes,
            "old_quantity": old_quantity,
            "new_quantity": self.quantity
        })
        
        self.last_updated = datetime.utcnow()
        
        if movement_type == "receipt":
            self.last_received = datetime.utcnow()
        elif movement_type == "issue":
            self.last_issued = datetime.utcnow()
        
        # Recalcular quantidade disponivel
        self.calculate_available_quantity()
    
    def reserve_quantity(self, quantity: int, reference: Optional[str] = None) -> bool:
        """Reserva uma quantidade do estoque"""
        if quantity > self.available_quantity:
            return False
        
        self.reserved_quantity += quantity
        self.calculate_available_quantity()
        
        # Adicionar ao historico
        self.movements.append({
            "type": "reservation",
            "quantity": quantity,
            "date": datetime.utcnow().isoformat(),
            "reference": reference,
            "notes": "Quantidade reservada",
            "old_reserved": self.reserved_quantity - quantity,
            "new_reserved": self.reserved_quantity
        })
        
        self.last_updated = datetime.utcnow()
        return True
    
    def release_quantity(self, quantity: int, reference: Optional[str] = None) -> bool:
        """Libera uma quantidade reservada"""
        if quantity > self.reserved_quantity:
            return False
        
        self.reserved_quantity -= quantity
        self.calculate_available_quantity()
        
        # Adicionar ao historico
        self.movements.append({
            "type": "release",
            "quantity": quantity,
            "date": datetime.utcnow().isoformat(),
            "reference": reference,
            "notes": "Quantidade liberada",
            "old_reserved": self.reserved_quantity + quantity,
            "new_reserved": self.reserved_quantity
        })
        
        self.last_updated = datetime.utcnow()
        return True
    
    def get_status(self) -> str:
        """Obtem o status do estoque"""
        if self.quantity == 0:
            return "out_of_stock"
        elif self.is_below_minimum():
            return "low_stock"
        elif self.is_below_reorder_point():
            return "reorder_needed"
        else:
            return "in_stock"
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Inventory':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
