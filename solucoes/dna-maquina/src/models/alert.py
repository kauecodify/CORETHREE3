"""
CORETHREE3 - DNA de Maquinas
Modelo de Alerta

Define a estrutura de dados para alertas gerados pelo sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class AlertSeverity(str, Enum):
    """Severidade do alerta"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(str, Enum):
    """Tipo de alerta"""
    VIBRATION = "vibration"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    CURRENT = "current"
    VOLTAGE = "voltage"
    HUMIDITY = "humidity"
    ANOMALY = "anomaly"
    PREDICTION = "prediction"
    DEVICE_OFFLINE = "device_offline"
    SENSOR_FAILURE = "sensor_failure"
    CALIBRATION_DUE = "calibration_due"
    MAINTENANCE_DUE = "maintenance_due"
    THRESHOLD_VIOLATION = "threshold_violation"
    SYSTEM_ERROR = "system_error"


class AlertStatus(str, Enum):
    """Status do alerta"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


class Alert(BaseModel):
    """
    Modelo de Alerta
    
    Representa um alerta gerado pelo sistema DNA de Maquinas.
    """
    
    id: str = Field(..., description="Identificador unico do alerta")
    
    # Classificacao
    severity: AlertSeverity = Field(AlertSeverity.MEDIUM, description="Severidade do alerta")
    alert_type: AlertType = Field(..., description="Tipo do alerta")
    status: AlertStatus = Field(AlertStatus.ACTIVE, description="Status do alerta")
    
    # Titulo e descricao
    title: str = Field(..., description="Titulo do alerta")
    description: str = Field(..., description="Descricao do alerta")
    
    # Relacionamentos
    device_id: Optional[str] = Field(None, description="ID do dispositivo")
    machine_id: Optional[str] = Field(None, description="ID da maquina")
    sensor_id: Optional[str] = Field(None, description="ID do sensor")
    reading_id: Optional[str] = Field(None, description="ID da leitura que gerou o alerta")
    
    # Dados do alerta
    value: Optional[float] = Field(None, description="Valor que gerou o alerta")
    unit: Optional[str] = Field(None, description="Unidade do valor")
    threshold: Optional[float] = Field(None, description="Threshold violado")
    threshold_type: Optional[str] = Field(None, description="Tipo do threshold (critical, high, medium, low)")
    
    # Predicao (para alertas de predicao)
    predicted_failure_date: Optional[datetime] = Field(None, description="Data prevista de falha")
    failure_probability: Optional[float] = Field(None, description="Probabilidade de falha (0-1)")
    remaining_useful_life: Optional[float] = Field(None, description="Vida util restante em dias")
    
    # Anomalia (para alertas de anomalia)
    anomaly_score: Optional[float] = Field(None, description="Score de anomalia")
    anomaly_type: Optional[str] = Field(None, description="Tipo de anomalia")
    
    # Temporizacao
    triggered_at: datetime = Field(..., description="Timestamp de disparo")
    acknowledged_at: Optional[datetime] = Field(None, description="Timestamp de reconhecimento")
    acknowledged_by: Optional[str] = Field(None, description="Usuario que reconheceu")
    resolved_at: Optional[datetime] = Field(None, description="Timestamp de resolucao")
    resolved_by: Optional[str] = Field(None, description="Usuario que resolveu")
    closed_at: Optional[datetime] = Field(None, description="Timestamp de fechamento")
    closed_by: Optional[str] = Field(None, description="Usuario que fechou")
    
    # SLA
    sla_response_time: Optional[int] = Field(None, description="Tempo de resposta SLA em minutos")
    sla_resolution_time: Optional[int] = Field(None, description="Tempo de resolucao SLA em minutos")
    
    # Acoes
    recommended_actions: List[str] = Field(default_factory=list, description="Acoes recomendadas")
    actions_taken: List[str] = Field(default_factory=list, description="Acoes tomadas")
    
    # Notificacoes
    notification_channels: List[str] = Field(default_factory=list, description="Canais de notificacao (email, sms, slack, etc.)")
    notified_users: List[str] = Field(default_factory=list, description="Usuarios notificados")
    
    # Metadados
    source: str = Field("system", description="Fonte do alerta (system, manual, external)")
    tags: List[str] = Field(default_factory=list, description="Tags do alerta")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert-001",
                "severity": "critical",
                "alert_type": "vibration",
                "status": "active",
                "title": "Vibracao critica detectada no Motor Principal",
                "description": "Sensor de vibracao do eixo X ultrapassou o threshold critico de 8.0g com valor de 8.5g",
                "device_id": "device-001",
                "machine_id": "machine-001",
                "sensor_id": "sensor-001",
                "reading_id": "reading-001",
                "value": 8.5,
                "unit": "g",
                "threshold": 8.0,
                "threshold_type": "critical",
                "triggered_at": "2024-07-15T12:00:00Z",
                "recommended_actions": [
                    "Verificar fixacao do motor",
                    "Inspecionar rolamentos",
                    "Avaliar balanceamento do eixo"
                ],
                "notification_channels": ["email", "sms"],
                "notified_users": ["joao@empresa.com", "maria@empresa.com"],
                "sla_response_time": 15,
                "sla_resolution_time": 120,
                "source": "system",
                "tags": ["vibration", "critical", "motor"],
                "created_at": "2024-07-15T12:00:00Z",
                "updated_at": "2024-07-15T12:00:00Z"
            }
        }
    
    @validator('severity', pre=True)
    def validate_severity(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in AlertSeverity]:
                raise ValueError(f'Severidade invalida: {v}. Severidades validas: {[s.value for s in AlertSeverity]}')
            return AlertSeverity(v)
        return v
    
    @validator('alert_type', pre=True)
    def validate_alert_type(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [at.value for at in AlertType]:
                raise ValueError(f'Tipo de alerta invalido: {v}. Tipos validos: {[at.value for at in AlertType]}')
            return AlertType(v)
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in AlertStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in AlertStatus]}')
            return AlertStatus(v)
        return v
    
    def is_active(self) -> bool:
        """Verifica se o alerta esta ativo"""
        return self.status == AlertStatus.ACTIVE
    
    def is_critical(self) -> bool:
        """Verifica se o alerta e critico"""
        return self.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]
    
    def get_age(self) -> float:
        """Calcula a idade do alerta em minutos"""
        now = datetime.utcnow()
        delta = now - self.triggered_at
        return delta.total_seconds() / 60
    
    def get_response_time(self) -> Optional[float]:
        """Calcula o tempo de resposta em minutos"""
        if self.acknowledged_at is None:
            return None
        
        delta = self.acknowledged_at - self.triggered_at
        return delta.total_seconds() / 60
    
    def get_resolution_time(self) -> Optional[float]:
        """Calcula o tempo de resolucao em minutos"""
        if self.resolved_at is None:
            return None
        
        delta = self.resolved_at - self.triggered_at
        return delta.total_seconds() / 60
    
    def is_sla_violated(self) -> bool:
        """Verifica se o SLA foi violado"""
        response_time = self.get_response_time()
        if response_time is None:
            return False
        
        if self.sla_response_time is None:
            return False
        
        return response_time > self.sla_response_time
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
