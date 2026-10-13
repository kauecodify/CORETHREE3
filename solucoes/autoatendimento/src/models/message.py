"""
CORETHREE3 - Autoatendimento Inteligente
Modelo de Mensagem (Message)
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class MessageType(str, Enum):
    """Tipo de mensagem"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    QUICK_REPLY = "quick_reply"
    BUTTON = "button"
    CAROUSEL = "carousel"
    CARD = "card"
    TEMPLATE = "template"


class MessageStatus(str, Enum):
    """Status da mensagem"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    DELETED = "deleted"


class MessageDirection(str, Enum):
    """Direcao da mensagem"""
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class MessageMetadata(BaseModel):
    """Metadados da mensagem"""
    
    # Informacoes de processamento
    processed_at: Optional[datetime] = Field(None, description="Data de processamento")
    processing_time: Optional[float] = Field(None, description="Tempo de processamento (ms)")
    
    # Informacoes de NLP
    intent: Optional[str] = Field(None, description="Intencao detectada")
    intent_confidence: Optional[float] = Field(None, description="Confianca da intencao")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Entidades extraidas")
    sentiment: Optional[str] = Field(None, description="Sentimento detectado")
    sentiment_score: Optional[float] = Field(None, description="Score de sentimento")
    
    # Informacoes de resposta
    response_intent: Optional[str] = Field(None, description="Intencao da resposta")
    response_slots: Dict[str, Any] = Field(default_factory=dict, description="Slots preenchidos na resposta")
    
    # Tags
    tags: List[str] = Field(default_factory=list, description="Tags")
    
    # Custom fields
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Campos customizados")


class Message(BaseModel):
    """Modelo de mensagem"""
    
    # Identificacao
    id: str = Field(..., description="ID unico da mensagem")
    conversation_id: str = Field(..., description="ID da conversa")
    session_id: str = Field(..., description="ID da sessao")
    
    # Conteudo
    type: MessageType = Field(..., description="Tipo da mensagem")
    content: Any = Field(..., description="Conteudo da mensagem")
    
    # Direcao
    direction: MessageDirection = Field(..., description="Direcao da mensagem")
    
    # Remetente
    sender_id: str = Field(..., description="ID do remetente")
    sender_name: Optional[str] = Field(None, description="Nome do remetente")
    sender_type: str = Field(..., description="Tipo do remetente (user, bot, system)")
    
    # Status
    status: MessageStatus = Field(MessageStatus.PENDING, description="Status da mensagem")
    
    # Metadados
    metadata: MessageMetadata = Field(default_factory=MessageMetadata, description="Metadados")
    
    # Controle
    is_deleted: bool = Field(False, description="Mensagem deletada")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    sent_at: Optional[datetime] = Field(None, description="Data de envio")
    delivered_at: Optional[datetime] = Field(None, description="Data de entrega")
    read_at: Optional[datetime] = Field(None, description="Data de leitura")
    
    @validator('content')
    def validate_content(cls, v, values):
        """Validar conteudo"""
        if values.get('type') == MessageType.TEXT and not isinstance(v, str):
            raise ValueError("Conteudo de mensagem de texto deve ser string")
        if values.get('type') == MessageType.IMAGE and not isinstance(v, (str, dict)):
            raise ValueError("Conteudo de mensagem de imagem deve ser string (URL) ou dict")
        return v
    
    @validator('sender_type')
    def validate_sender_type(cls, v):
        """Validar tipo do remetente"""
        valid_types = ["user", "bot", "system"]
        if v not in valid_types:
            raise ValueError(f"Tipo do remetente deve ser um de: {valid_types}")
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "msg-1",
                    "conversation_id": "conv-1",
                    "session_id": "session-1",
                    "type": "text",
                    "content": "Ola, gostaria de saber o status do meu pedido 12345",
                    "direction": "incoming",
                    "sender_id": "user-1",
                    "sender_name": "Joao Silva",
                    "sender_type": "user",
                    "metadata": {
                        "intent": "StatusPedido",
                        "intent_confidence": 0.95,
                        "entities": {"numeroPedido": "12345"}
                    }
                },
                {
                    "id": "msg-2",
                    "conversation_id": "conv-1",
                    "session_id": "session-1",
                    "type": "text",
                    "content": "Vou verificar o status do seu pedido 12345.",
                    "direction": "outgoing",
                    "sender_id": "bot-1",
                    "sender_name": "CORETHREE3 Bot",
                    "sender_type": "bot",
                    "metadata": {
                        "response_intent": "StatusPedido",
                        "response_slots": {"numeroPedido": "12345"}
                    }
                }
            ]
        }
    
    def mark_as_sent(self) -> None:
        """Marcar como enviada"""
        self.status = MessageStatus.SENT
        self.sent_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_delivered(self) -> None:
        """Marcar como entregue"""
        self.status = MessageStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_read(self) -> None:
        """Marcar como lida"""
        self.status = MessageStatus.READ
        self.read_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_failed(self) -> None:
        """Marcar como falhada"""
        self.status = MessageStatus.FAILED
        self.updated_at = datetime.utcnow()
    
    def mark_as_deleted(self) -> None:
        """Marcar como deletada"""
        self.is_deleted = True
        self.status = MessageStatus.DELETED
        self.updated_at = datetime.utcnow()


class TextMessage(Message):
    """Mensagem de texto"""
    
    # Conteudo especifico para texto
    text: str = Field(..., description="Texto da mensagem")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "msg-1",
                    "conversation_id": "conv-1",
                    "session_id": "session-1",
                    "type": "text",
                    "content": "Ola, tudo bem?",
                    "text": "Ola, tudo bem?",
                    "direction": "incoming",
                    "sender_id": "user-1",
                    "sender_type": "user"
                }
            ]
        }
    
    @validator('content', pre=True, always=True)
    def set_content(cls, v, values):
        """Definir conteudo automaticamente"""
        return values.get('text', v)


class QuickReplyOption(BaseModel):
    """Opcao de resposta rapida"""
    
    # Texto da opcao
    text: str = Field(..., description="Texto da opcao")
    
    # Valor da opcao
    value: str = Field(..., description="Valor da opcao")
    
    # Acao associada
    action: Optional[str] = Field(None, description="Acao associada")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class QuickReplyMessage(Message):
    """Mensagem com opcoes de resposta rapida"""
    
    # Texto principal
    text: str = Field(..., description="Texto principal")
    
    # Opcoes de resposta
    options: List[QuickReplyOption] = Field(..., description="Opcoes de resposta")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "msg-1",
                    "conversation_id": "conv-1",
                    "session_id": "session-1",
                    "type": "quick_reply",
                    "content": {
                        "text": "Como posso te ajudar?",
                        "options": [
                            {"text": "Status de pedido", "value": "StatusPedido"},
                            {"text": "Agendar servico", "value": "AgendarServico"},
                            {"text": "Falar com humano", "value": "FalarComHumano"}
                        ]
                    },
                    "text": "Como posso te ajudar?",
                    "options": [
                        {"text": "Status de pedido", "value": "StatusPedido"},
                        {"text": "Agendar servico", "value": "AgendarServico"},
                        {"text": "Falar com humano", "value": "FalarComHumano"}
                    ],
                    "direction": "outgoing",
                    "sender_id": "bot-1",
                    "sender_type": "bot"
                }
            ]
        }
    
    @validator('content', pre=True, always=True)
    def set_content(cls, v, values):
        """Definir conteudo automaticamente"""
        return {
            "text": values.get('text'),
            "options": values.get('options', [])
        }


class ButtonAction(BaseModel):
    """Acao de botao"""
    
    # Tipo de acao
    type: str = Field(..., description="Tipo de acao (url, postback, phone)")
    
    # Valor da acao
    value: str = Field(..., description="Valor da acao")
    
    # Texto do botao
    title: str = Field(..., description="Texto do botao")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class ButtonMessage(Message):
    """Mensagem com botoes"""
    
    # Texto principal
    text: str = Field(..., description="Texto principal")
    
    # Botoes
    buttons: List[ButtonAction] = Field(..., description="Botoes")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "msg-1",
                    "conversation_id": "conv-1",
                    "session_id": "session-1",
                    "type": "button",
                    "content": {
                        "text": "Escolha uma opcao:",
                        "buttons": [
                            {"type": "postback", "value": "StatusPedido", "title": "Status de Pedido"},
                            {"type": "postback", "value": "AgendarServico", "title": "Agendar Servico"}
                        ]
                    },
                    "text": "Escolha uma opcao:",
                    "buttons": [
                        {"type": "postback", "value": "StatusPedido", "title": "Status de Pedido"},
                        {"type": "postback", "value": "AgendarServico", "title": "Agendar Servico"}
                    ],
                    "direction": "outgoing",
                    "sender_id": "bot-1",
                    "sender_type": "bot"
                }
            ]
        }
    
    @validator('content', pre=True, always=True)
    def set_content(cls, v, values):
        """Definir conteudo automaticamente"""
        return {
            "text": values.get('text'),
            "buttons": values.get('buttons', [])
        }
