"""
CORETHREE3 - DNA de Maquinas
Modelo de Predicao

Define a estrutura de dados para predicoes de manutencao preditiva.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class PredictionType(str, Enum):
    """Tipo de predicao"""
    ANOMALY_DETECTION = "anomaly_detection"
    FAILURE_PREDICTION = "failure_prediction"
    REMAINING_USEFUL_LIFE = "remaining_useful_life"
    MAINTENANCE_OPTIMIZATION = "maintenance_optimization"
    ENERGY_CONSUMPTION = "energy_consumption"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class PredictionStatus(str, Enum):
    """Status da predicao"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class Prediction(BaseModel):
    """
    Modelo de Predicao
    
    Representa uma predicao gerada pelo sistema de manutencao preditiva.
    """
    
    id: str = Field(..., description="Identificador unico da predicao")
    
    # Classificacao
    prediction_type: PredictionType = Field(..., description="Tipo da predicao")
    status: PredictionStatus = Field(PredictionStatus.PENDING, description="Status da predicao")
    
    # Relacionamentos
    device_id: Optional[str] = Field(None, description="ID do dispositivo")
    machine_id: Optional[str] = Field(None, description="ID da maquina")
    sensor_ids: List[str] = Field(default_factory=list, description="IDs dos sensores usados")
    
    # Dados de predicao
    prediction_timestamp: datetime = Field(..., description="Timestamp da predicao")
    predicted_value: Optional[float] = Field(None, description="Valor previsto")
    predicted_unit: Optional[str] = Field(None, description="Unidade do valor previsto")
    
    # Predicao de falha
    predicted_failure_date: Optional[datetime] = Field(None, description="Data prevista de falha")
    failure_probability: float = Field(0.0, description="Probabilidade de falha (0-1)")
    confidence: float = Field(0.0, description="Confianca da predicao (0-1)")
    
    # Predicao de vida util
    remaining_useful_life: Optional[float] = Field(None, description="Vida util restante em dias")
   rul_confidence: Optional[float] = Field(None, description="Confianca da predicao de RUL (0-1)")
    
    # Predicao de anomalia
    is_anomaly: bool = Field(False, description="Indica se foi detectada uma anomalia")
    anomaly_score: Optional[float] = Field(None, description="Score de anomalia")
    anomaly_type: Optional[str] = Field(None, description="Tipo de anomalia")
    
    # Detalhes do modelo
    model_name: str = Field("", description="Nome do modelo usado")
    model_version: str = Field("", description="Versao do modelo")
    model_accuracy: Optional[float] = Field(None, description="Acuracia do modelo (0-1)")
    
    # Features usadas
    features: List[str] = Field(default_factory=list, description="Lista de features usadas")
    feature_values: Dict[str, float] = Field(default_factory=dict, description="Valores das features")
    
    # Interpretacao
    interpretation: Optional[str] = Field(None, description="Interpretacao da predicao")
    recommended_actions: List[str] = Field(default_factory=list, description="Acoes recomendadas")
    
    # Validacao
    validated_by: Optional[str] = Field(None, description="Usuario que validou a predicao")
    validated_at: Optional[datetime] = Field(None, description="Timestamp da validacao")
    validation_notes: Optional[str] = Field(None, description="Notas de validacao")
    
    # Metadados
    source: str = Field("system", description="Fonte da predicao (system, manual)")
    tags: List[str] = Field(default_factory=list, description="Tags da predicao")
    
    # Erros
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    error_details: Optional[Dict] = Field(None, description="Detalhes do erro")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prediction-001",
                "prediction_type": "failure_prediction",
                "status": "completed",
                "device_id": "device-001",
                "machine_id": "machine-001",
                "sensor_ids": ["sensor-001", "sensor-002", "sensor-003"],
                "prediction_timestamp": "2024-07-15T12:00:00Z",
                "predicted_failure_date": "2024-08-15T00:00:00Z",
                "failure_probability": 0.75,
                "confidence": 0.92,
                "remaining_useful_life": 30.5,
                "is_anomaly": False,
                "model_name": "RandomCutForest-FailurePrediction",
                "model_version": "2.1.0",
                "model_accuracy": 0.95,
                "features": ["vibration_rms", "temperature", "current", "operating_hours"],
                "feature_values": {
                    "vibration_rms": 2.5,
                    "temperature": 85.0,
                    "current": 85.0,
                    "operating_hours": 25000.0
                },
                "interpretation": "Alta probabilidade de falha nos rolamentos do motor nos proximos 30 dias",
                "recommended_actions": [
                    "Agendar manutencao preventiva",
                    "Verificar nivel de lubrificacao",
                    "Inspecionar rolamentos"
                ],
                "source": "system",
                "tags": ["failure", "bearing", "motor"],
                "created_at": "2024-07-15T12:00:00Z",
                "updated_at": "2024-07-15T12:00:00Z"
            }
        }
    
    @validator('prediction_type', pre=True)
    def validate_prediction_type(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [pt.value for pt in PredictionType]:
                raise ValueError(f'Tipo de predicao invalido: {v}. Tipos validos: {[pt.value for pt in PredictionType]}')
            return PredictionType(v)
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in PredictionStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in PredictionStatus]}')
            return PredictionStatus(v)
        return v
    
    def is_reliable(self) -> bool:
        """Verifica se a predicao e confiavel"""
        return self.confidence >= 0.8
    
    def is_critical(self) -> bool:
        """Verifica se a predicao e critica"""
        return self.failure_probability >= 0.7 or self.is_anomaly
    
    def get_days_until_failure(self) -> Optional[float]:
        """Calcula os dias ate a falha prevista"""
        if self.predicted_failure_date is None:
            return None
        
        now = datetime.utcnow()
        delta = self.predicted_failure_date - now
        return delta.total_seconds() / (24 * 3600)
    
    def get_urgency(self) -> str:
        """Determina a urgencia da predicao"""
        days = self.get_days_until_failure()
        
        if days is None:
            if self.is_anomaly:
                return "HIGH"
            return "MEDIUM"
        
        if days <= 7:
            return "CRITICAL"
        elif days <= 30:
            return "HIGH"
        elif days <= 90:
            return "MEDIUM"
        else:
            return "LOW"
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Prediction':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
