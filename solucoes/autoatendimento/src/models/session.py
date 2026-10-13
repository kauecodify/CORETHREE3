"""
CORETHREE3 - Autoatendimento Inteligente
Modelo de Sessao (Session)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class Session(BaseModel):
    """Modelo de sessao"""
    
    # Identificacao
    id: str = Field(..., description="ID unico da sessao")
    user_id: Optional[str] = Field(None, description="ID do usuario")
    
    # Informacoes da sessao
    session_token: str = Field(..., description="Token da sessao")
    
    # Estado
    state: Dict[str, Any] = Field(default_factory=dict, description="Estado da sessao")
    
    # Contexto
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto da sessao")
    
    # Historico
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Historico da sessao")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Controle
    is_active: bool = Field(True, description="Sessao ativa")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    expires_at: datetime = Field(..., description="Data de expiracao")
    
    # Contadores
    request_count: int = Field(0, description="Numero de requisicoes")
    message_count: int = Field(0, description="Numero de mensagens")
    
    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        """Validar data de expiracao"""
        if v <= values.get('created_at', datetime.utcnow()):
            raise ValueError("Data de expiracao deve ser maior que a data de criacao")
        return v
    
    @validator('request_count', 'message_count')
    def validate_counts(cls, v):
        """Validar contadores"""
        if v < 0:
            raise ValueError("Contador nao pode ser negativo")
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "session-1",
                    "user_id": "user-1",
                    "session_token": "token-123",
                    "state": {
                        "current_intent": "StatusPedido",
                        "filled_slots": {"numeroPedido": None}
                    },
                    "context": {
                        "customer_id": "customer-1",
                        "preferences": {"language": "pt-BR"}
                    },
                    "expires_at": "2026-12-13T14:30:00Z"
                }
            ]
        }
    
    def is_expired(self) -> bool:
        """Verificar se a sessao expirou"""
        return datetime.utcnow() > self.expires_at
    
    def add_to_history(self, entry: Dict[str, Any]) -> None:
        """Adicionar entrada ao historico"""
        self.history.append(entry)
        self.updated_at = datetime.utcnow()
    
    def increment_request_count(self) -> None:
        """Incrementar contador de requisicoes"""
        self.request_count += 1
        self.updated_at = datetime.utcnow()
    
    def increment_message_count(self) -> None:
        """Incrementar contador de mensagens"""
        self.message_count += 1
        self.updated_at = datetime.utcnow()
    
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Atualizar estado"""
        self.state.update(new_state)
        self.updated_at = datetime.utcnow()
    
    def update_context(self, new_context: Dict[str, Any]) -> None:
        """Atualizar contexto"""
        self.context.update(new_context)
        self.updated_at = datetime.utcnow()


class SessionManagerConfig(BaseModel):
    """Configuracoes do gerenciador de sessoes"""
    
    # TTL da sessao
    session_ttl: int = Field(1800, description="TTL da sessao em segundos (30 minutos)")
    
    # Limite de sessoes por usuario
    max_sessions_per_user: int = Field(5, description="Maximo de sessoes por usuario")
    
    # Limite de requisicoes por sessao
    max_requests_per_session: int = Field(1000, description="Maximo de requisicoes por sessao")
    
    # Limite de mensagens por sessao
    max_messages_per_session: int = Field(500, description="Maximo de mensagens por sessao")
    
    # Configuracoes de limpeza
    cleanup_interval: int = Field(300, description="Intervalo de limpeza em segundos (5 minutos)")
    cleanup_batch_size: int = Field(100, description="Tamanho do lote de limpeza")
    
    # Configuracoes de armazenamento
    storage_backend: str = Field("dynamodb", description="Backend de armazenamento (dynamodb, redis)")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
