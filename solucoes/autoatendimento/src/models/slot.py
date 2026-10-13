"""
CORETHREE3 - Autoatendimento Inteligente
Modelo de Slot (Parametro)
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class SlotType(str, Enum):
    """Tipos de slot"""
    # Tipos padrao do Amazon Lex
    AMAZON_NUMBER = "AMAZON.NUMBER"
    AMAZON_DATE = "AMAZON.DATE"
    AMAZON_TIME = "AMAZON.TIME"
    AMAZON_TEXT = "AMAZON.TEXT"
    AMAZON_ALPHA_NUMERIC = "AMAZON.AlphaNumeric"
    AMAZON_EMAIL = "AMAZON.Email"
    AMAZON_PHONE_NUMBER = "AMAZON.PhoneNumber"
    AMAZON_CPFCNPJ = "AMAZON.CPFCNPJ"
    AMAZON_CEP = "AMAZON.CEP"
    
    # Tipos customizados
    CUSTOM = "CUSTOM"
    CATEGORY = "CATEGORY"
    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"


class SlotValidationRule(BaseModel):
    """Regra de validacao de slot"""
    
    # Tipo de validacao
    type: str = Field(..., description="Tipo de validacao")
    
    # Valor ou expressao
    value: Optional[Any] = Field(None, description="Valor ou expressao")
    
    # Mensagem de erro
    error_message: str = Field(..., description="Mensagem de erro")


class Slot(BaseModel):
    """Modelo de slot (parametro) para NLP"""
    
    # Identificacao
    id: str = Field(..., description="ID unico do slot")
    name: str = Field(..., description="Nome do slot")
    type: SlotType = Field(SlotType.AMAZON_TEXT, description="Tipo do slot")
    
    # Descricao
    description: Optional[str] = Field(None, description="Descricao do slot")
    
    # Configuracoes
    is_required: bool = Field(False, description="Slot obrigatorio")
    is_multivalued: bool = Field(False, description="Slot com multiplos valores")
    
    # Valores possiveis (para enumeracoes)
    enumeration_values: List[str] = Field(default_factory=list, description="Valores possiveis")
    
    # Regras de validacao
    validation_rules: List[SlotValidationRule] = Field(default_factory=list, description="Regras de validacao")
    
    # Prompt para solicitacao
    prompt: Optional[str] = Field(None, description="Prompt para solicitacao")
    
    # Exemplo
    example: Optional[str] = Field(None, description="Exemplo de valor")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Controle
    is_active: bool = Field(True, description="Slot ativo")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    
    @validator('enumeration_values')
    def validate_enumeration_values(cls, v, values):
        """Validar valores de enumeracao"""
        if values.get('type') in [SlotType.CATEGORY, SlotType.PRODUCT, SlotType.SERVICE] and not v:
            raise ValueError("Slots de categoria, produto ou servico devem ter valores de enumeracao")
        return v
    
    @validator('validation_rules')
    def validate_validation_rules(cls, v):
        """Validar regras de validacao"""
        for rule in v:
            if not isinstance(rule, dict):
                raise ValueError("Regra de validacao deve ser um dicionario")
            if 'type' not in rule:
                raise ValueError("Regra de validacao deve ter tipo")
            if 'error_message' not in rule:
                raise ValueError("Regra de validacao deve ter mensagem de erro")
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "slot-1",
                    "name": "numeroPedido",
                    "type": "AMAZON.NUMBER",
                    "description": "Numero do pedido",
                    "is_required": True,
                    "validation_rules": [
                        {
                            "type": "min",
                            "value": 1,
                            "error_message": "Numero do pedido deve ser maior que 0"
                        },
                        {
                            "type": "max",
                            "value": 999999,
                            "error_message": "Numero do pedido deve ser menor que 999999"
                        }
                    ]
                },
                {
                    "id": "slot-2",
                    "name": "tipoServico",
                    "type": "CATEGORY",
                    "description": "Tipo de servico",
                    "is_required": True,
                    "enumeration_values": ["manutencao", "suporte", "consulta", "reclamacao"],
                    "prompt": "Qual tipo de servico voce precisa?"
                }
            ]
        }
    
    def to_lex_format(self) -> Dict[str, Any]:
        """Converter para formato do Amazon Lex"""
        return {
            "name": self.name,
            "slotType": self.type.value,
            "description": self.description,
            "isRequired": self.is_required,
            "isMultivalued": self.is_multivalued,
            "enumerationValues": self.enumeration_values if self.enumeration_values else None,
        }


class SlotExtractionResult(BaseModel):
    """Resultado da extracao de slot"""
    
    # Slot extraido
    slot: str = Field(..., description="Nome do slot")
    value: Any = Field(..., description="Valor extraido")
    
    # Confianca
    confidence: float = Field(..., description="Confianca da extracao (0-1)")
    
    # Posicao no texto
    start_index: int = Field(..., description="Indice de inicio no texto")
    end_index: int = Field(..., description="Indice de fim no texto")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validar confianca"""
        if not 0 <= v <= 1:
            raise ValueError("Confianca deve estar entre 0 e 1")
        return v


class SlotFiller(BaseModel):
    """Preenchedor de slots"""
    
    # Estrategia de preenchimento
    strategy: str = Field(..., description="Estrategia de preenchimento")
    
    # Configuracoes
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuracoes")
    
    # Desempenho
    success_rate: Optional[float] = Field(None, description="Taxa de sucesso")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
