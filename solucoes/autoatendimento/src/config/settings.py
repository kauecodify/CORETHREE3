"""
CORETHREE3 - Autoatendimento Inteligente
Configuracoes Gerais do Modulo
"""

import os
from typing import Dict, Any


class Settings:
    """Configuracoes gerais do modulo de autoatendimento"""
    
    # Ambiente
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Versao
    VERSION: str = "1.0.0"
    
    # Nome do modulo
    MODULE_NAME: str = "autoatendimento"
    
    # Regiao AWS
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Prefixo para recursos AWS
    RESOURCE_PREFIX: str = f"corethree3-{MODULE_NAME}"
    
    # Configuracoes de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuracoes de rate limiting
    RATE_LIMIT: int = 1000  # Requests por minuto
    RATE_LIMIT_BURST: int = 200
    
    # Configuracoes de timeout
    REQUEST_TIMEOUT: int = 30  # Segundos
    LEX_TIMEOUT: int = 10  # Segundos
    BEDROCK_TIMEOUT: int = 15  # Segundos
    
    # Configuracoes de retry
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 0.5  # Segundos
    
    # Configuracoes de cache
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL: int = 300  # Segundos
    
    # Configuracoes de seguranca
    SECRET_KEY: str = os.getenv("SECRET_KEY", "corethree3-secret-key-change-me")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "corethree3-jwt-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # Configuracoes de API
    API_TITLE: str = "CORETHREE3 Autoatendimento API"
    API_DESCRIPTION: str = "API para autoatendimento inteligente com IA/ML"
    API_VERSION: str = VERSION
    
    # Configuracoes de CORS
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://corethree3.com",
        "https://*.corethree3.com",
    ]
    
    # Configuracoes de paginacao
    DEFAULT_PAGE: int = 1
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Configuracoes de validacao
    MAX_INPUT_LENGTH: int = 10000  # Caracteres
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Obter configuracao por chave"""
        return getattr(cls, key, default)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Converter configuracoes para dicionario"""
        return {k: v for k, v in cls.__dict__.items() 
                if not k.startswith("__") and not callable(v)}


# Instancia das configuracoes
settings = Settings()
