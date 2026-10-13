"""
CORETHREE3 - Pedidos Sem Fronteiras
Modelo de Endereco

Define a estrutura de dados para enderecos do sistema.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class Address(BaseModel):
    """
    Modelo de Endereco
    
    Representa um endereco no sistema Pedidos Sem Fronteiras.
    """
    
    # Identificacao
    id: Optional[str] = Field(None, description="Identificador unico do endereco")
    type: Optional[str] = Field(None, description="Tipo do endereco (billing, shipping, etc.)")
    
    # Endereco
    street: str = Field(..., description="Rua/Logradouro")
    number: Optional[str] = Field(None, description="Numero")
    complement: Optional[str] = Field(None, description="Complemento")
    neighborhood: Optional[str] = Field(None, description="Bairro")
    city: str = Field(..., description="Cidade")
    state: str = Field(..., description="Estado/Provincia")
    zip_code: str = Field(..., description="CEP/Codigo Postal")
    country: str = Field(..., description="Pais")
    
    # Localizacao GPS
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    
    # Contato
    contact_name: Optional[str] = Field(None, description="Nome do contato")
    contact_phone: Optional[str] = Field(None, description="Telefone do contato")
    contact_email: Optional[str] = Field(None, description="Email do contato")
    
    # Informacoes adicionais
    is_default: bool = Field(False, description="Endereco padrao")
    notes: Optional[str] = Field(None, description="Notas adicionais")
    
    # Metadados
    tags: Optional[list] = Field(None, description="Tags do endereco")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "addr-001",
                "type": "shipping",
                "street": "Rua das Industrias",
                "number": "123",
                "complement": "Galpao A",
                "neighborhood": "Distrito Industrial",
                "city": "Sao Paulo",
                "state": "SP",
                "zip_code": "01234-567",
                "country": "BR",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "contact_name": "Joao Silva",
                "contact_phone": "+55 11 99999-9999",
                "contact_email": "joao@empresa.com",
                "is_default": True,
                "notes": "Entrada principal do galpao",
                "tags": ["industrial", "main"]
            }
        }
    
    def get_full_address(self) -> str:
        """Retorna o endereco completo formatado"""
        parts = [
            self.street,
            self.number,
            self.complement,
            self.neighborhood,
            self.city,
            self.state,
            self.zip_code,
            self.country
        ]
        return ", ".join(filter(None, parts))
    
    def get_short_address(self) -> str:
        """Retorna o endereco resumido"""
        parts = [
            self.street,
            self.number,
            self.city,
            self.state,
            self.zip_code,
            self.country
        ]
        return ", ".join(filter(None, parts))
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Address':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
