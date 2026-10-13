"""
CORETHREE3 - Autoatendimento Inteligente
Modelo de Resposta (Response)
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ResponseType(str, Enum):
    """Tipos de resposta"""
    TEXT = "text"
    QUICK_REPLY = "quick_reply"
    BUTTON = "button"
    CAROUSEL = "carousel"
    CARD = "card"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEMPLATE = "template"
    ACTION = "action"
    MULTI = "multi"


class ResponseStatus(str, Enum):
    """Status da resposta"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResponseAction(BaseModel):
    """Acao a ser executada como resposta"""
    
    # Tipo de acao
    type: str = Field(..., description="Tipo de acao (api_call, database, notification, etc.)")
    
    # Dados da acao
    data: Dict[str, Any] = Field(default_factory=dict, description="Dados da acao")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class Response(BaseModel):
    """Modelo de resposta"""
    
    # Identificacao
    id: str = Field(..., description="ID unico da resposta")
    request_id: str = Field(..., description="ID da requisicao")
    conversation_id: Optional[str] = Field(None, description="ID da conversa")
    message_id: Optional[str] = Field(None, description="ID da mensagem")
    
    # Tipo
    type: ResponseType = Field(..., description="Tipo da resposta")
    
    # Conteudo
    content: Any = Field(..., description="Conteudo da resposta")
    
    # Status
    status: ResponseStatus = Field(ResponseStatus.PENDING, description="Status da resposta")
    
    # Intencao
    intent: Optional[str] = Field(None, description="Intencao associada")
    
    # Slots
    slots: Dict[str, Any] = Field(default_factory=dict, description="Slots preenchidos")
    
    # Acoes
    actions: List[ResponseAction] = Field(default_factory=list, description="Acoes a serem executadas")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Controle
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    completed_at: Optional[datetime] = Field(None, description="Data de conclusao")
    
    # Performance
    generation_time: Optional[float] = Field(None, description="Tempo de geracao (ms)")
    confidence: Optional[float] = Field(None, description="Confianca da resposta")
    
    # Erros
    error: Optional[str] = Field(None, description="Erro (se houver)")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detalhes do erro")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validar confianca"""
        if v is not None and not 0 <= v <= 1:
            raise ValueError("Confianca deve estar entre 0 e 1")
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "response-1",
                    "request_id": "request-1",
                    "conversation_id": "conv-1",
                    "type": "text",
                    "content": "Vou verificar o status do seu pedido 12345.",
                    "intent": "StatusPedido",
                    "slots": {"numeroPedido": "12345"},
                    "status": "completed",
                    "generation_time": 150,
                    "confidence": 0.95
                }
            ]
        }
    
    def mark_as_generating(self) -> None:
        """Marcar como gerando"""
        self.status = ResponseStatus.GENERATING
        self.updated_at = datetime.utcnow()
    
    def mark_as_completed(self) -> None:
        """Marcar como concluida"""
        self.status = ResponseStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_failed(self, error: str, error_details: Dict[str, Any] = None) -> None:
        """Marcar como falhada"""
        self.status = ResponseStatus.FAILED
        self.error = error
        self.error_details = error_details
        self.updated_at = datetime.utcnow()
    
    def mark_as_cancelled(self) -> None:
        """Marcar como cancelada"""
        self.status = ResponseStatus.CANCELLED
        self.updated_at = datetime.utcnow()


class TextResponse(Response):
    """Resposta de texto"""
    
    # Texte
    text: str = Field(..., description="Texto da resposta")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "response-1",
                    "request_id": "request-1",
                    "type": "text",
                    "content": "Ola! Como posso te ajudar hoje?",
                    "text": "Ola! Como posso te ajudar hoje?",
                    "status": "completed"
                }
            ]
        }
    
    @validator('content', pre=True, always=True)
    def set_content(cls, v, values):
        """Definir conteudo automaticamente"""
        return values.get('text', v)


class QuickReplyOption(BaseModel):
    """Opcao de resposta rapida"""
    
    # Texto
    text: str = Field(..., description="Texto da opcao")
    
    # Valor
    value: str = Field(..., description="Valor da opcao")
    
    # Acao
    action: Optional[str] = Field(None, description="Acao associada")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class QuickReplyResponse(Response):
    """Resposta com opcoes de resposta rapida"""
    
    # Texto principal
    text: str = Field(..., description="Texto principal")
    
    # Opcoes
    options: List[QuickReplyOption] = Field(default_factory=list, description="Opcoes de resposta")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "response-1",
                    "request_id": "request-1",
                    "type": "quick_reply",
                    "content": {
                        "text": "Como posso te ajudar?",
                        "options": [
                            {"text": "Status de pedido", "value": "StatusPedido"},
                            {"text": "Agendar servico", "value": "AgendarServico"}
                        ]
                    },
                    "text": "Como posso te ajudar?",
                    "options": [
                        {"text": "Status de pedido", "value": "StatusPedido"},
                        {"text": "Agendar servico", "value": "AgendarServico"}
                    ],
                    "status": "completed"
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
    
    # Tipo
    type: str = Field(..., description="Tipo de acao (postback, url, phone)")
    
    # Texto
    title: str = Field(..., description="Texto do botao")
    
    # Valor/URL
    value: str = Field(..., description="Valor ou URL")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class ButtonResponse(Response):
    """Resposta com botoes"""
    
    # Texto principal
    text: str = Field(..., description="Texto principal")
    
    # Botoes
    buttons: List[ButtonAction] = Field(default_factory=list, description="Botoes")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "response-1",
                    "request_id": "request-1",
                    "type": "button",
                    "content": {
                        "text": "Escolha uma opcao:",
                        "buttons": [
                            {"type": "postback", "title": "Status de Pedido", "value": "StatusPedido"},
                            {"type": "postback", "title": "Agendar Servico", "value": "AgendarServico"}
                        ]
                    },
                    "text": "Escolha uma opcao:",
                    "buttons": [
                        {"type": "postback", "title": "Status de Pedido", "value": "StatusPedido"},
                        {"type": "postback", "title": "Agendar Servico", "value": "AgendarServico"}
                    ],
                    "status": "completed"
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


class CardItem(BaseModel):
    """Item de card"""
    
    # Titulo
    title: str = Field(..., description="Titulo do item")
    
    # Descricao
    description: Optional[str] = Field(None, description="Descricao do item")
    
    # Imagem
    image_url: Optional[str] = Field(None, description="URL da imagem")
    
    # Acoes
    actions: List[ButtonAction] = Field(default_factory=list, description="Acoes do item")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class CarouselResponse(Response):
    """Resposta em carousel"""
    
    # Itens
    items: List[CardItem] = Field(default_factory=list, description="Itens do carousel")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "response-1",
                    "request_id": "request-1",
                    "type": "carousel",
                    "content": {
                        "items": [
                            {
                                "title": "Produto 1",
                                "description": "Descricao do produto 1",
                                "image_url": "https://exemplo.com/produto1.jpg",
                                "actions": [
                                    {"type": "postback", "title": "Comprar", "value": "Comprar_1"}
                                ]
                            },
                            {
                                "title": "Produto 2",
                                "description": "Descricao do produto 2",
                                "image_url": "https://exemplo.com/produto2.jpg",
                                "actions": [
                                    {"type": "postback", "title": "Comprar", "value": "Comprar_2"}
                                ]
                            }
                        ]
                    },
                    "items": [
                        {
                            "title": "Produto 1",
                            "description": "Descricao do produto 1",
                            "image_url": "https://exemplo.com/produto1.jpg",
                            "actions": [
                                {"type": "postback", "title": "Comprar", "value": "Comprar_1"}
                            ]
                        }
                    ],
                    "status": "completed"
                }
            ]
        }
    
    @validator('content', pre=True, always=True)
    def set_content(cls, v, values):
        """Definir conteudo automaticamente"""
        return {"items": values.get('items', [])}


class MultiResponse(Response):
    """Resposta com multiplos tipos"""
    
    # Respostas
    responses: List[Response] = Field(default_factory=list, description="Respostas")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "response-1",
                    "request_id": "request-1",
                    "type": "multi",
                    "content": [
                        {
                            "type": "text",
                            "content": "Aqui estao os resultados:",
                            "status": "completed"
                        },
                        {
                            "type": "carousel",
                            "content": {
                                "items": [
                                    {"title": "Resultado 1", "description": "Descricao 1"},
                                    {"title": "Resultado 2", "description": "Descricao 2"}
                                ]
                            },
                            "status": "completed"
                        }
                    ],
                    "responses": [
                        {
                            "type": "text",
                            "content": "Aqui estao os resultados:",
                            "status": "completed"
                        },
                        {
                            "type": "carousel",
                            "content": {
                                "items": [
                                    {"title": "Resultado 1", "description": "Descricao 1"},
                                    {"title": "Resultado 2", "description": "Descricao 2"}
                                ]
                            },
                            "status": "completed"
                        }
                    ],
                    "status": "completed"
                }
            ]
        }
    
    @validator('content', pre=True, always=True)
    def set_content(cls, v, values):
        """Definir conteudo automaticamente"""
        return values.get('responses', [])


class ResponseGeneratorConfig(BaseModel):
    """Configuracoes do gerador de respostas"""
    
    # Modelo
    model_id: str = Field(..., description="ID do modelo de IA")
    
    # Configuracoes do modelo
    model_config: Dict[str, Any] = Field(default_factory=dict, description="Configuracoes do modelo")
    
    # Prompt
    system_prompt: str = Field(..., description="Prompt do sistema")
    user_prompt_template: str = Field(..., description="Template do prompt do usuario")
    
    # Contexto
    context_window: int = Field(5, description="Janela de contexto")
    max_context_length: int = Field(4000, description="Tamanho maximo do contexto")
    
    # Resposta
    max_response_length: int = Field(2000, description="Tamanho maximo da resposta")
    temperature: float = Field(0.7, description="Temperatura do modelo")
    top_p: float = Field(0.9, description="Top P")
    top_k: int = Field(250, description="Top K")
    
    # Validacao
    confidence_threshold: float = Field(0.7, description="Limiar de confianca")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    @validator('temperature', 'top_p')
    def validate_probs(cls, v):
        """Validar probabilidades"""
        if not 0 <= v <= 1:
            raise ValueError("Temperatura e Top P devem estar entre 0 e 1")
        return v
    
    @validator('confidence_threshold')
    def validate_threshold(cls, v):
        """Validar limiar de confianca"""
        if not 0 <= v <= 1:
            raise ValueError("Limiar de confianca deve estar entre 0 e 1")
        return v
