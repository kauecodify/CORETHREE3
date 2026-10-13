"""
CORETHREE3 - Autoatendimento Inteligente
Modelo de Usuario (User)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class UserProfile(BaseModel):
    """Perfil do usuario"""
    
    # Informacoes basicas
    first_name: Optional[str] = Field(None, description="Primeiro nome")
    last_name: Optional[str] = Field(None, description="Ultimo nome")
    full_name: Optional[str] = Field(None, description="Nome completo")
    
    # Contato
    email: Optional[str] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Telefone")
    
    # Localizacao
    address: Optional[str] = Field(None, description="Endereco")
    city: Optional[str] = Field(None, description="Cidade")
    state: Optional[str] = Field(None, description="Estado")
    country: Optional[str] = Field(None, description="Pais")
    zip_code: Optional[str] = Field(None, description="CEP")
    
    # Preferencias
    language: str = Field("pt-BR", description="Idioma")
    timezone: str = Field("America/Sao_Paulo", description="Fuso horario")
    
    # Dados demograficos
    birth_date: Optional[datetime] = Field(None, description="Data de nascimento")
    gender: Optional[str] = Field(None, description="Genero")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class UserPreferences(BaseModel):
    """Preferencias do usuario"""
    
    # Preferencias de comunicacao
    preferred_channel: Optional[str] = Field(None, description="Canal preferido")
    preferred_time: Optional[str] = Field(None, description="Horario preferido")
    
    # Preferencias de notificacao
    email_notifications: bool = Field(True, description="Notificacoes por email")
    sms_notifications: bool = Field(True, description="Notificacoes por SMS")
    push_notifications: bool = Field(True, description="Notificacoes push")
    
    # Preferencias de privacidade
    data_sharing: bool = Field(True, description="Compartilhamento de dados")
    analytics_opt_out: bool = Field(False, description="Opt-out de analiticos")
    
    # Preferencias de IA
    ai_assistant: bool = Field(True, description="Assistente de IA")
    ai_recommendations: bool = Field(True, description="Recomendacoes de IA")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class UserActivity(BaseModel):
    """Atividade do usuario"""
    
    # Contadores
    total_sessions: int = Field(0, description="Total de sessoes")
    total_messages: int = Field(0, description="Total de mensagens")
    total_conversations: int = Field(0, description="Total de conversas")
    
    # Ultimas atividades
    last_session_at: Optional[datetime] = Field(None, description="Ultima sessao")
    last_message_at: Optional[datetime] = Field(None, description="Ultima mensagem")
    last_conversation_at: Optional[datetime] = Field(None, description="Ultima conversa")
    
    # Metricas
    avg_session_duration: Optional[float] = Field(None, description="Duracao media de sessao (segundos)")
    avg_messages_per_session: Optional[float] = Field(None, description="Mensagens media por sessao")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class User(BaseModel):
    """Modelo de usuario"""
    
    # Identificacao
    id: str = Field(..., description="ID unico do usuario")
    
    # Autenticacao
    username: str = Field(..., description="Nome de usuario")
    password_hash: Optional[str] = Field(None, description="Hash da senha")
    
    # Perfil
    profile: UserProfile = Field(default_factory=UserProfile, description="Perfil do usuario")
    
    # Preferencias
    preferences: UserPreferences = Field(default_factory=UserPreferences, description="Preferencias do usuario")
    
    # Atividade
    activity: UserActivity = Field(default_factory=UserActivity, description="Atividade do usuario")
    
    # Status
    is_active: bool = Field(True, description="Usuario ativo")
    is_verified: bool = Field(False, description="Usuario verificado")
    is_admin: bool = Field(False, description="Usuario administrador")
    
    # Controle
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    last_login_at: Optional[datetime] = Field(None, description="Ultimo login")
    
    # Seguranca
    failed_login_attempts: int = Field(0, description="Tentativas de login falhas")
    locked_at: Optional[datetime] = Field(None, description="Data de bloqueio")
    lock_reason: Optional[str] = Field(None, description="Motivo do bloqueio")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    @validator('failed_login_attempts')
    def validate_failed_attempts(cls, v):
        """Validar tentativas de login falhas"""
        if v < 0:
            raise ValueError("Tentativas de login falhas nao podem ser negativas")
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "user-1",
                    "username": "joao.silva",
                    "profile": {
                        "first_name": "Joao",
                        "last_name": "Silva",
                        "email": "joao@exemplo.com",
                        "phone": "+5511999999999",
                        "language": "pt-BR"
                    },
                    "preferences": {
                        "preferred_channel": "whatsapp",
                        "email_notifications": True,
                        "ai_assistant": True
                    },
                    "is_active": True,
                    "is_verified": True
                }
            ]
        }
    
    def get_full_name(self) -> str:
        """Obter nome completo"""
        return self.profile.full_name or f"{self.profile.first_name or ''} {self.profile.last_name or ''}".strip()
    
    def lock(self, reason: str = "") -> None:
        """Bloquear usuario"""
        self.is_active = False
        self.locked_at = datetime.utcnow()
        self.lock_reason = reason
        self.updated_at = datetime.utcnow()
    
    def unlock(self) -> None:
        """Desbloquear usuario"""
        self.is_active = True
        self.locked_at = None
        self.lock_reason = None
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def increment_failed_login(self) -> None:
        """Incrementar tentativas de login falhas"""
        self.failed_login_attempts += 1
        self.updated_at = datetime.utcnow()
    
    def reset_failed_login(self) -> None:
        """Resetar tentativas de login falhas"""
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def update_last_login(self) -> None:
        """Atualizar ultimo login"""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class UserAuthToken(BaseModel):
    """Token de autenticacao do usuario"""
    
    # Token
    token: str = Field(..., description="Token JWT")
    
    # Tipo
    token_type: str = Field("Bearer", description="Tipo do token")
    
    # Expiracao
    expires_in: int = Field(3600, description="Tempo de expiracao (segundos)")
    expires_at: datetime = Field(..., description="Data de expiracao")
    
    # Refresh token
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    refresh_expires_in: Optional[int] = Field(None, description="Tempo de expiracao do refresh (segundos)")
    refresh_expires_at: Optional[datetime] = Field(None, description="Data de expiracao do refresh")
    
    # Usuario
    user_id: str = Field(..., description="ID do usuario")
    username: str = Field(..., description="Nome de usuario")
    
    # Permissoes
    permissions: List[str] = Field(default_factory=list, description="Permissoes")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        """Validar data de expiracao"""
        if v <= datetime.utcnow():
            raise ValueError("Token ja expirou")
        return v


class UserRole(BaseModel):
    """Papel do usuario"""
    
    # Identificacao
    id: str = Field(..., description="ID do papel")
    name: str = Field(..., description="Nome do papel")
    description: Optional[str] = Field(None, description="Descricao do papel")
    
    # Permissoes
    permissions: List[str] = Field(default_factory=list, description="Permissoes")
    
    # Hierarquia
    level: int = Field(0, description="Nivel do papel")
    parent_id: Optional[str] = Field(None, description="ID do papel pai")
    
    # Controle
    is_active: bool = Field(True, description="Papel ativo")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
