"""
CORETHREE3 - Pedidos Sem Fronteiras
Modelo de Cliente

Define a estrutura de dados para clientes do sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class CustomerType(str, Enum):
    """Tipo de cliente"""
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    DISTRIBUTOR = "distributor"
    RESALE = "resale"
    GOVERNMENT = "government"


class Customer(BaseModel):
    """
    Modelo de Cliente
    
    Representa um cliente no sistema Pedidos Sem Fronteiras.
    """
    
    id: str = Field(..., description="Identificador unico do cliente")
    
    # Informacoes basicas
    name: str = Field(..., description="Nome do cliente")
    customer_type: CustomerType = Field(CustomerType.INDIVIDUAL, description="Tipo do cliente")
    
    # Contatos
    email: Optional[str] = Field(None, description="Email do cliente")
    phone: Optional[str] = Field(None, description="Telefone do cliente")
    secondary_phone: Optional[str] = Field(None, description="Telefone secundario")
    
    # Enderecos
    addresses: List[Dict] = Field(default_factory=list, description="Lista de enderecos")
    billing_address: Optional[Dict] = Field(None, description="Endereco de cobranca padrao")
    shipping_address: Optional[Dict] = Field(None, description="Endereco de entrega padrao")
    
    # Informacoes fiscais
    tax_id: Optional[str] = Field(None, description="CPF/CNPJ do cliente")
    tax_exempt: bool = Field(False, description="Isento de impostos")
    
    # Informacoes financeiras
    credit_limit: Optional[float] = Field(None, description="Limite de credito")
    credit_available: Optional[float] = Field(None, description="Credito disponivel")
    payment_terms: Optional[str] = Field(None, description="Condicoes de pagamento")
    
    # Status
    status: str = Field("active", description="Status do cliente")
    verified: bool = Field(False, description="Cliente verificado")
    
    # Preferencias
    preferred_shipping_method: Optional[str] = Field(None, description="Metodo de envio preferido")
    preferred_carrier: Optional[str] = Field(None, description="Transportadora preferida")
    
    # Historico
    total_orders: int = Field(0, description="Total de pedidos")
    total_spent: float = Field(0.0, description="Total gasto")
    first_order_date: Optional[datetime] = Field(None, description="Data do primeiro pedido")
    last_order_date: Optional[datetime] = Field(None, description="Data do ultimo pedido")
    
    # Metadados
    tags: List[str] = Field(default_factory=list, description="Tags do cliente")
    notes: Optional[str] = Field(None, description="Notas adicionais")
    
    # Integracao
    erp_id: Optional[str] = Field(None, description="ID no sistema ERP")
    crm_id: Optional[str] = Field(None, description="ID no sistema CRM")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "cust-001",
                "name": "Industria XYZ Ltda",
                "customer_type": "corporate",
                "email": "compras@industriaxyz.com",
                "phone": "+55 11 99999-9999",
                "secondary_phone": "+55 11 88888-8888",
                "addresses": [
                    {
                        "type": "billing",
                        "street": "Rua das Industrias, 123",
                        "city": "Sao Paulo",
                        "state": "SP",
                        "zip_code": "01234-567",
                        "country": "BR",
                        "is_default": True
                    },
                    {
                        "type": "shipping",
                        "street": "Rua das Entregas, 456",
                        "city": "Sao Paulo",
                        "state": "SP",
                        "zip_code": "01234-567",
                        "country": "BR",
                        "is_default": True
                    }
                ],
                "billing_address": {
                    "street": "Rua das Industrias, 123",
                    "city": "Sao Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "BR"
                },
                "shipping_address": {
                    "street": "Rua das Entregas, 456",
                    "city": "Sao Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "BR"
                },
                "tax_id": "12.345.678/0001-23",
                "tax_exempt": False,
                "credit_limit": 500000.0,
                "credit_available": 450000.0,
                "payment_terms": "30 days",
                "status": "active",
                "verified": True,
                "preferred_shipping_method": "express",
                "preferred_carrier": "Transportadora ABC",
                "total_orders": 45,
                "total_spent": 1250000.0,
                "first_order_date": "2023-01-15T00:00:00Z",
                "last_order_date": "2024-01-15T00:00:00Z",
                "tags": ["industrial", "vip"],
                "notes": "Cliente prioritario",
                "erp_id": "ERP-001",
                "crm_id": "CRM-001",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2024-01-15T12:00:00Z"
            }
        }
    
    @validator('customer_type', pre=True)
    def validate_customer_type(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [ct.value for ct in CustomerType]:
                raise ValueError(f'Tipo de cliente invalido: {v}. Tipos validos: {[ct.value for ct in CustomerType]}')
            return CustomerType(v)
        return v
    
    def get_default_address(self, address_type: str = "shipping") -> Optional[Dict]:
        """Obtem o endereco padrao do tipo especificado"""
        for address in self.addresses:
            if address.get("type") == address_type and address.get("is_default", False):
                return address
        return None
    
    def add_address(self, address: Dict) -> None:
        """Adiciona um endereco"""
        self.addresses.append(address)
    
    def remove_address(self, address_id: str) -> bool:
        """Remove um endereco"""
        for i, address in enumerate(self.addresses):
            if address.get("id") == address_id:
                self.addresses.pop(i)
                return True
        return False
    
    def update_credit(self, amount: float) -> None:
        """Atualiza o credito disponivel"""
        if self.credit_available is not None:
            self.credit_available += amount
    
    def can_place_order(self, order_total: float) -> bool:
        """Verifica se o cliente pode fazer um pedido"""
        if self.status != "active":
            return False
        if self.credit_limit is not None:
            if self.credit_available is not None:
                return order_total <= self.credit_available
            return order_total <= self.credit_limit
        return True
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Customer':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
