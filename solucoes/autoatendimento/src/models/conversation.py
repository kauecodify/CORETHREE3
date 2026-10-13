"""
CORETHREE3 - Autoatendimento Inteligente
Modelo de Conversa (Conversation)
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ConversationStatus(str, Enum):
    """Status da conversa"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"
    ABANDONED = "abandoned"


class ConversationChannel(str, Enum):
    """Canal da conversa"""
    WEB = "web"
    MOBILE = "mobile"
    WHATSAPP = "whatsapp"
    FACEBOOK = "facebook"
    TELEGRAM = "telegram"
    EMAIL = "email"
    PHONE = "phone"


class ConversationMetadata(BaseModel):
    """Metadados da conversa"""
    
    # Informacoes do cliente
    customer_id: Optional[str] = Field(None, description="ID do cliente")
    customer_name: Optional[str] = Field(None, description="Nome do cliente")
    customer_email: Optional[str] = Field(None, description="Email do cliente")
    customer_phone: Optional[str] = Field(None, description="Telefone do cliente")
    
    # Informacoes do dispositivo
    device_id: Optional[str] = Field(None, description="ID do dispositivo")
    device_type: Optional[str] = Field(None, description="Tipo do dispositivo")
    user_agent: Optional[str] = Field(None, description="User Agent")
    ip_address: Optional[str] = Field(None, description="Endereco IP")
    
    # Informacoes de localizacao
    country: Optional[str] = Field(None, description="Pais")
    state: Optional[str] = Field(None, description="Estado")
    city: Optional[str] = Field(None, description="Cidade")
    
    # Tags
    tags: List[str] = Field(default_factory=list, description="Tags")
    
    # Custom fields
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Campos customizados")


class Conversation(BaseModel):
    """Modelo de conversa"""
    
    # Identificacao
    id: str = Field(..., description="ID unico da conversa")
    session_id: str = Field(..., description="ID da sessao")
    
    # Canal
    channel: ConversationChannel = Field(..., description="Canal da conversa")
    
    # Status
    status: ConversationStatus = Field(ConversationStatus.OPEN, description="Status da conversa")
    
    # Participantes
    participants: List[str] = Field(default_factory=list, description="Participantes")
    
    # Mensagens (nao inclusas aqui, veja ConversationWithMessages)
    message_count: int = Field(0, description="Numero de mensagens")
    
    # Intencao atual
    current_intent: Optional[str] = Field(None, description="Intencao atual")
    
    # Slots preenchidos
    filled_slots: Dict[str, Any] = Field(default_factory=dict, description="Slots preenchidos")
    
    # Metadados
    metadata: ConversationMetadata = Field(default_factory=ConversationMetadata, description="Metadados")
    
    # Controle
    is_active: bool = Field(True, description="Conversa ativa")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    started_at: Optional[datetime] = Field(None, description="Data de inicio")
    ended_at: Optional[datetime] = Field(None, description="Data de termino")
    
    # Performance
    first_response_time: Optional[float] = Field(None, description="Tempo da primeira resposta (segundos)")
    average_response_time: Optional[float] = Field(None, description="Tempo medio de resposta (segundos)")
    resolution_time: Optional[float] = Field(None, description="Tempo de resolucao (segundos)")
    
    # Satisfacao
    satisfaction_score: Optional[int] = Field(None, description="Nota de satisfacao (1-5)")
    feedback: Optional[str] = Field(None, description="Feedback do cliente")
    
    @validator('participants')
    def validate_participants(cls, v):
        """Validar participantes"""
        if not v:
            raise ValueError("Conversa deve ter pelo menos um participante")
        return v
    
    @validator('message_count')
    def validate_message_count(cls, v):
        """Validar numero de mensagens"""
        if v < 0:
            raise ValueError("Numero de mensagens nao pode ser negativo")
        return v
    
    @validator('satisfaction_score')
    def validate_satisfaction_score(cls, v):
        """Validar nota de satisfacao"""
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Nota de satisfacao deve estar entre 1 e 5")
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "conv-1",
                    "session_id": "session-1",
                    "channel": "web",
                    "status": "open",
                    "participants": ["user-1", "bot-1"],
                    "message_count": 5,
                    "current_intent": "StatusPedido",
                    "filled_slots": {
                        "numeroPedido": "12345"
                    },
                    "metadata": {
                        "customer_id": "customer-1",
                        "device_type": "desktop",
                        "tags": ["suporte", "pedido"]
                    }
                }
            ]
        }


class ConversationWithMessages(Conversation):
    """Modelo de conversa com mensagens"""
    
    # Mensagens
    messages: List[Any] = Field(default_factory=list, description="Mensagens da conversa")
    
    @validator('messages')
    def validate_messages(cls, v, values):
        """Validar mensagens"""
        if len(v) != values.get('message_count', 0):
            raise ValueError("Numero de mensagens nao corresponde ao message_count")
        return v


class ConversationSummary(BaseModel):
    """Resumo de conversa"""
    
    # Identificacao
    conversation_id: str = Field(..., description="ID da conversa")
    
    # Resumo
    summary: str = Field(..., description="Resumo da conversa")
    
    # Intencoes
    intents: List[str] = Field(default_factory=list, description="Intencoes detectadas")
    
    # Slots
    slots: Dict[str, List[Any]] = Field(default_factory=dict, description="Slots extraidos")
    
    # Sentimentos
    sentiment: Optional[str] = Field(None, description="Sentimento predominante")
    sentiment_score: Optional[float] = Field(None, description="Score de sentimento (-1 a 1)")
    
    # Topicos
    topics: List[str] = Field(default_factory=list, description="Topicos discutidos")
    
    # Acoes
    actions: List[str] = Field(default_factory=list, description="Acoes realizadas")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Controle
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")


class ConversationAnalytics(BaseModel):
    """Analise de conversas"""
    
    # Periodo
    start_date: datetime = Field(..., description="Data de inicio")
    end_date: datetime = Field(..., description="Data de fim")
    
    # Metricas
    total_conversations: int = Field(0, description="Total de conversas")
    resolved_conversations: int = Field(0, description="Conversas resolvidas")
    escalated_conversations: int = Field(0, description="Conversas escaladas")
    abandoned_conversations: int = Field(0, description="Conversas abandonadas")
    
    # Tempo
    avg_first_response_time: Optional[float] = Field(None, description="Tempo medio da primeira resposta (segundos)")
    avg_resolution_time: Optional[float] = Field(None, description="Tempo medio de resolucao (segundos)")
    
    # Satisfacao
    avg_satisfaction_score: Optional[float] = Field(None, description="Nota media de satisfacao")
    satisfaction_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribuicao de notas")
    
    # Intencoes
    intent_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribuicao de intencoes")
    
    # Canais
    channel_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribuicao de canais")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
