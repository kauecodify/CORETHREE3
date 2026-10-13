"""
CORETHREE3 - Pedidos Sem Fronteiras
Modelo de Produto

Define a estrutura de dados para produtos do sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class ProductCategory(str, Enum):
    """Categoria do produto"""
    MACHINERY = "machinery"
    ELECTRICAL = "electrical"
    HYDRAULIC = "hydraulic"
    PNEUMATIC = "pneumatic"
    MECHANICAL = "mechanical"
    ELECTRONIC = "electronic"
    AUTOMATION = "automation"
    TOOLS = "tools"
    CONSUMABLES = "consumables"
    OTHER = "other"


class ProductStatus(str, Enum):
    """Status do produto"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    BACKORDER = "backorder"
    PREORDER = "preorder"


class Product(BaseModel):
    """
    Modelo de Produto
    
    Representa um produto no sistema Pedidos Sem Fronteiras.
    """
    
    id: str = Field(..., description="Identificador unico do produto")
    
    # Informacoes basicas
    name: str = Field(..., description="Nome do produto")
    description: Optional[str] = Field(None, description="Descricao do produto")
    category: ProductCategory = Field(ProductCategory.MACHINERY, description="Categoria do produto")
    
    # Codigo e identificacao
    sku: str = Field(..., description="SKU do produto")
    barcode: Optional[str] = Field(None, description="Codigo de barras")
    manufacturer_part_number: Optional[str] = Field(None, description="Numero de pecas do fabricante")
    
    # Fabricante
    manufacturer: Optional[str] = Field(None, description="Fabricante do produto")
    brand: Optional[str] = Field(None, description="Marca do produto")
    
    # Status
    status: ProductStatus = Field(ProductStatus.ACTIVE, description="Status do produto")
    
    # Precos
    base_price: float = Field(..., description="Preco base")
    sale_price: Optional[float] = Field(None, description="Preco de venda")
    cost_price: Optional[float] = Field(None, description="Preco de custo")
    
    # Unidades
    unit_of_measure: str = Field("unit", description="Unidade de medida")
    weight: Optional[float] = Field(None, description="Peso em kg")
    dimensions: Optional[Dict] = Field(None, description="Dimensoes (length, width, height)")
    volume: Optional[float] = Field(None, description="Volume em m3")
    
    # Estoque
    stock_quantity: int = Field(0, description="Quantidade em estoque")
    minimum_stock_level: int = Field(0, description="Nivel minimo de estoque")
    reorder_point: int = Field(0, description="Ponto de reabastecimento")
    reorder_quantity: int = Field(0, description="Quantidade de reabastecimento")
    
    # Localizacao
    warehouse_id: Optional[str] = Field(None, description="ID do armazem")
    location: Optional[str] = Field(None, description="Localizacao no armazem")
    
    # Especificacoes tecnicas
    specifications: Optional[Dict] = Field(None, description="Especificacoes tecnicas")
    
    # Integracao com DNA de Maquinas
    machine_compatibility: List[str] = Field(default_factory=list, description="Maquinas compatveis")
    production_time: Optional[int] = Field(None, description="Tempo de producao em horas")
    required_machines: List[str] = Field(default_factory=list, description="Maquinas necessarias para producao")
    
    # Imagens e documentos
    images: List[str] = Field(default_factory=list, description="URLs de imagens")
    documents: List[str] = Field(default_factory=list, description="URLs de documentos")
    
    # Metadados
    tags: List[str] = Field(default_factory=list, description="Tags do produto")
    
    # Integracao
    erp_id: Optional[str] = Field(None, description="ID no sistema ERP")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod-001",
                "name": "Motor Eletrico Trifasico 55kW",
                "description": "Motor eletrico trifasico de alta eficiencia para aplicacoes industriais",
                "category": "electrical",
                "sku": "MOT-55KW-TRI-001",
                "barcode": "123456789012",
                "manufacturer_part_number": "ME-55KW-4P",
                "manufacturer": "Siemens",
                "brand": "Siemens",
                "status": "active",
                "base_price": 15000.0,
                "sale_price": 14500.0,
                "cost_price": 10000.0,
                "unit_of_measure": "unit",
                "weight": 250.0,
                "dimensions": {
                    "length": 1.2,
                    "width": 0.8,
                    "height": 0.6
                },
                "volume": 0.576,
                "stock_quantity": 50,
                "minimum_stock_level": 10,
                "reorder_point": 20,
                "reorder_quantity": 30,
                "warehouse_id": "wh-001",
                "location": "A-12-03",
                "specifications": {
                    "power": "55kW",
                    "voltage": "440V",
                    "frequency": "60Hz",
                    "current": "85A",
                    "rpm": "1750",
                    "efficiency": "92%",
                    "protection_class": "IP55",
                    "cooling_method": "IC411"
                },
                "machine_compatibility": ["machine-001", "machine-002"],
                "production_time": 8,
                "required_machines": ["machine-001"],
                "images": [
                    "https://example.com/images/motor-55kw.jpg",
                    "https://example.com/images/motor-55kw-diagram.png"
                ],
                "documents": [
                    "https://example.com/docs/motor-55kw-manual.pdf",
                    "https://example.com/docs/motor-55kw-specs.pdf"
                ],
                "tags": ["motor", "electric", "industrial", "high-efficiency"],
                "erp_id": "ERP-PROD-001",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2024-01-15T12:00:00Z"
            }
        }
    
    @validator('category', pre=True)
    def validate_category(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [c.value for c in ProductCategory]:
                raise ValueError(f'Categoria invalida: {v}. Categorias validas: {[c.value for c in ProductCategory]}')
            return ProductCategory(v)
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in ProductStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in ProductStatus]}')
            return ProductStatus(v)
        return v
    
    def is_in_stock(self) -> bool:
        """Verifica se o produto esta em estoque"""
        return self.stock_quantity > 0
    
    def is_below_reorder_point(self) -> bool:
        """Verifica se o estoque esta abaixo do ponto de reabastecimento"""
        return self.stock_quantity < self.reorder_point
    
    def needs_reorder(self) -> bool:
        """Verifica se e necessario reabastecer"""
        return self.stock_quantity <= self.reorder_point
    
    def get_reorder_quantity(self) -> int:
        """Obtem a quantidade para reabastecimento"""
        if self.stock_quantity < self.reorder_point:
            return self.reorder_quantity
        return 0
    
    def adjust_stock(self, quantity: int, operation: str = "add") -> None:
        """Ajusta o estoque"""
        if operation == "add":
            self.stock_quantity += quantity
        elif operation == "subtract":
            self.stock_quantity -= quantity
            if self.stock_quantity < 0:
                self.stock_quantity = 0
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Product':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
