"""
CORETHREE3 - Autoatendimento Inteligente
Modelo de Intencao (Intent)
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class IntentType(str, Enum):
    """Tipos de intencao"""
    CUSTOM = "custom"
    BUILTIN = "builtin"
    FALLBACK = "fallback"


class Intent(BaseModel):
    """Modelo de intencao para NLP"""
    
    # Identificacao
    id: str = Field(..., description="ID unico da intencao")
    name: str = Field(..., description="Nome da intencao")
    type: IntentType = Field(IntentType.CUSTOM, description="Tipo da intencao")
    
    # Descricao
    description: Optional[str] = Field(None, description="Descricao da intencao")
    
    # Amostras de treino
    samples: List[str] = Field(default_factory=list, description="Amostras de treino")
    
    # Slots (parametros)
    slots: Dict[str, Any] = Field(default_factory=dict, description="Slots da intencao")
    
    # Configuracoes de NLP
    nlp_config: Dict[str, Any] = Field(default_factory=dict, description="Configuracoes de NLP")
    
    # Fulfilment
    fulfillment: Optional[str] = Field(None, description="Lambda de fulfillment")
    
    # Respostas
    responses: List[str] = Field(default_factory=list, description="Respostas padrao")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Controle
    is_active: bool = Field(True, description="Intencao ativa")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    version: int = Field(1, description="Versao da intencao")
    
    @validator('samples')
    def validate_samples(cls, v):
        """Validar amostras"""
        if not v:
            raise ValueError("Amostras nao podem ser vazias")
        if len(v) < 3:
            raise ValueError("Pelo menos 3 amostras sao necessarias")
        return v
    
    @validator('slots')
    def validate_slots(cls, v):
        """Validar slots"""
        for slot_name, slot_config in v.items():
            if not isinstance(slot_config, dict):
                raise ValueError(f"Slot {slot_name} deve ser um dicionario")
            if 'type' not in slot_config:
                raise ValueError(f"Slot {slot_name} deve ter tipo")
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "intent-1",
                    "name": "StatusPedido",
                    "type": "custom",
                    "description": "Consultar status de pedido",
                    "samples": [
                        "Onde esta meu pedido?",
                        "Qual o status do meu pedido?",
                        "Meu pedido ainda nao chegou"
                    ],
                    "slots": {
                        "numeroPedido": {
                            "type": "AMAZON.NUMBER",
                            "description": "Numero do pedido",
                            "required": True
                        }
                    },
                    "fulfillment": "arn:aws:lambda:us-east-1:123456789012:function:StatusPedido",
                    "responses": ["Vou verificar o status do seu pedido."]
                }
            ]
        }
    
    def to_lex_format(self) -> Dict[str, Any]:
        """Converter para formato do Amazon Lex"""
        return {
            "name": self.name,
            "description": self.description,
            "sampleUtterances": self.samples,
            "slots": [
                {
                    "name": slot_name,
                    "slotType": slot_config.get("type"),
                    "description": slot_config.get("description"),
                    "isRequired": slot_config.get("required", False),
                }
                for slot_name, slot_config in self.slots.items()
            ] if self.slots else [],
            "fulfillmentActivity": {
                "type": "CodeHook"
            } if self.fulfillment else None,
        }
    
    def to_bedrock_format(self) -> Dict[str, Any]:
        """Converter para formato de prompt do Bedrock"""
        return {
            "intent": self.name,
            "description": self.description,
            "examples": self.samples,
            "parameters": list(self.slots.keys()),
        }


class IntentDetectionResult(BaseModel):
    """Resultado da deteccao de intencao"""
    
    # Intencao detectada
    intent: str = Field(..., description="Nome da intencao detectada")
    intent_id: str = Field(..., description="ID da intencao")
    
    # Confianca
    confidence: float = Field(..., description="Confianca da deteccao (0-1)")
    
    # Slots extraidos
    slots: Dict[str, Any] = Field(default_factory=dict, description="Slots extraidos")
    
    # Alternativas
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Intencoes alternativas")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validar confianca"""
        if not 0 <= v <= 1:
            raise ValueError("Confianca deve estar entre 0 e 1")
        return v


class IntentClassifier(BaseModel):
    """Classificador de intencoes"""
    
    # Modelos
    model_id: str = Field(..., description="ID do modelo de classificacao")
    model_type: str = Field(..., description="Tipo do modelo")
    
    # Configuracoes
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuracoes do modelo")
    
    # Desempenho
    accuracy: Optional[float] = Field(None, description="Acuracia do modelo")
    precision: Optional[float] = Field(None, description="Precisao do modelo")
    recall: Optional[float] = Field(None, description="Recall do modelo")
    f1_score: Optional[float] = Field(None, description="F1 Score do modelo")
    
    # Metadados
    trained_at: Optional[datetime] = Field(None, description="Data de treinamento")
    version: str = Field(..., description="Versao do modelo")
