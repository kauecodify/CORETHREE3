"""
CORETHREE3 - DNA de Maquinas
Configuracoes Gerais do Modulo
"""

import os
from typing import Dict, Any, List


class Settings:
    """Configuracoes gerais do modulo DNA de Maquinas"""
    
    # Ambiente
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Versao
    VERSION: str = "1.0.0"
    
    # Nome do modulo
    MODULE_NAME: str = "dna-maquina"
    
    # Regiao AWS
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Prefixo para recursos AWS
    RESOURCE_PREFIX: str = f"corethree3-{MODULE_NAME}"
    
    # Configuracoes de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuracoes de rate limiting
    RATE_LIMIT: int = 10000  # Requests por minuto (IoT envia muitos dados)
    RATE_LIMIT_BURST: int = 5000
    
    # Configuracoes de timeout
    REQUEST_TIMEOUT: int = 10  # Segundos
    IOT_TIMEOUT: int = 5  # Segundos
    SAGEMAKER_TIMEOUT: int = 60  # Segundos
    TIMESTREAM_TIMEOUT: int = 30  # Segundos
    
    # Configuracoes de retry
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 0.5  # Segundos
    
    # Configuracoes de cache
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL: int = 300  # Segundos
    
    # Configuracoes de seguranca
    SECRET_KEY: str = os.getenv("SECRET_KEY", "corethree3-dna-maquina-secret-key-change-me")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "corethree3-dna-maquina-jwt-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # Configuracoes de API
    API_TITLE: str = "CORETHREE3 DNA de Maquinas API"
    API_DESCRIPTION: str = "API para monitoramento inteligente de maquinas com IoT e ML"
    API_VERSION: str = VERSION
    
    # Configuracoes de CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://corethree3.com",
        "https://*.corethree3.com",
    ]
    
    # Configuracoes de paginacao
    DEFAULT_PAGE: int = 1
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 500
    
    # Configuracoes de validacao
    MAX_INPUT_LENGTH: int = 10000  # Caracteres
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Configuracoes de monitoramento
    MONITOR_INTERVAL: int = 60  # Segundos entre coleta de dados
    MONITOR_BATCH_SIZE: int = 1000  # Numero de leituras por lote
    
    # Configuracoes de alertas
    ALERT_THRESHOLD_CRITICAL: float = 0.95  # 95% de confianca para alerta critico
    ALERT_THRESHOLD_HIGH: float = 0.85  # 85% para alerta alto
    ALERT_THRESHOLD_MEDIUM: float = 0.70  # 70% para alerta medio
    
    # Configuracoes de manutencao preditiva
    PREDICTION_HORIZON: int = 14  # Dias para previsao
    PREDICTION_CONFIDENCE_THRESHOLD: float = 0.85  # Limiar de confianca
    PREDICTION_MIN_SAMPLES: int = 100  # Minimo de amostras para previsao
    
    # Configuracoes de sensores
    SENSOR_SAMPLING_RATE: int = 10  # Hz (10 leituras por segundo)
    SENSOR_BATCH_INTERVAL: int = 60  # Segundos entre envios
    SENSOR_MAX_RETRIES: int = 3
    
    # Configuracoes de dispositivos
    DEVICE_HEARTBEAT_INTERVAL: int = 300  # Segundos (5 minutos)
    DEVICE_OFFLINE_THRESHOLD: int = 600  # Segundos (10 minutos sem heartbeat)
    
    # Configuracoes de RUL (Remaining Useful Life)
    RUL_PREDICTION_ENABLED: bool = True
    RUL_MINIMUM: int = 1  # Dias minimos para previsao
    RUL_MAXIMUM: int = 365  # Dias maximos para previsao
    
    # Configuracoes de analise
    ANALYSIS_WINDOW: int = 30  # Dias para analise historica
    ANALYSIS_BATCH_SIZE: int = 10000  # Tamanho do lote de analise
    
    # Configuracoes de exportacao
    EXPORT_FORMATS: List[str] = ["csv", "json", "parquet"]
    EXPORT_MAX_ROWS: int = 1000000
    
    # Configuracoes de visualizacao
    DASHBOARD_REFRESH_INTERVAL: int = 30  # Segundos
    DASHBOARD_MAX_POINTS: int = 10000  # Pontos maximos por grafico
    
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
