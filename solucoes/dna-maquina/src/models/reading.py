"""
CORETHREE3 - DNA de Maquinas
Modelo de Leitura de Sensor

Define a estrutura de dados para leituras de sensores.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class ReadingQuality(str, Enum):
    """Qualidade da leitura"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"


class ReadingMetadata(BaseModel):
    """Metadados da leitura"""
    sensor_id: str = Field(..., description="ID do sensor")
    device_id: Optional[str] = Field(None, description="ID do dispositivo")
    machine_id: Optional[str] = Field(None, description="ID da maquina")
    
    # Informacoes de timestamp
    timestamp: datetime = Field(..., description="Timestamp da leitura")
    received_at: Optional[datetime] = Field(None, description="Timestamp de recebimento")
    processed_at: Optional[datetime] = Field(None, description="Timestamp de processamento")
    
    # Informacoes de localizacao
    location: Optional[str] = Field(None, description="Localizacao da leitura")
    axis: Optional[str] = Field(None, description="Eixo da leitura (x, y, z)")
    
    # Informacoes de qualidade
    quality: ReadingQuality = Field(ReadingQuality.GOOD, description="Qualidade da leitura")
    confidence: Optional[float] = Field(None, description="Confianca da leitura (0-1)")
    
    # Informacoes de processamento
    batch_id: Optional[str] = Field(None, description="ID do batch")
    sequence_number: int = Field(0, description="Numero de sequencia no batch")
    
    # Informacoes de calibracao
    is_calibrated: bool = Field(True, description="Indica se a leitura foi calibrada")
    calibration_factor: Optional[float] = Field(None, description="Fator de calibracao aplicado")


class Reading(BaseModel):
    """
    Modelo de Leitura de Sensor
    
    Representa uma leitura individual de um sensor.
    """
    
    id: str = Field(..., description="Identificador unico da leitura")
    
    # Valor principal
    value: float = Field(..., description="Valor da leitura")
    unit: str = Field("", description="Unidade de medicao")
    
    # Metadados
    metadata: ReadingMetadata = Field(..., description="Metadados da leitura")
    
    # Valores adicionais (para sensores complexos)
    additional_values: Dict[str, float] = Field(default_factory=dict, description="Valores adicionais")
    
    # Valores estatisticos (para sensores de vibracao, etc.)
    rms: Optional[float] = Field(None, description="Valor RMS")
    peak: Optional[float] = Field(None, description="Valor de pico")
    frequency: Optional[float] = Field(None, description="Frequencia")
    
    # Valores de threshold
    threshold_violated: Optional[str] = Field(None, description="Threshold violado (critical, high, medium, low)")
    threshold_value: Optional[float] = Field(None, description="Valor do threshold violado")
    
    # Processamento
    is_processed: bool = Field(False, description="Indica se a leitura foi processada")
    is_anomaly: bool = Field(False, description="Indica se a leitura e uma anomalia")
    anomaly_score: Optional[float] = Field(None, description="Score de anomalia")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "reading-001",
                "value": 2.5,
                "unit": "g",
                "metadata": {
                    "sensor_id": "sensor-001",
                    "device_id": "device-001",
                    "machine_id": "machine-001",
                    "timestamp": "2024-07-15T12:00:00.123Z",
                    "received_at": "2024-07-15T12:00:00.456Z",
                    "processed_at": "2024-07-15T12:00:00.789Z",
                    "location": "Motor Principal - Eixo X",
                    "axis": "x",
                    "quality": "excellent",
                    "confidence": 0.99,
                    "batch_id": "batch-001",
                    "sequence_number": 1,
                    "is_calibrated": True,
                    "calibration_factor": 1.0
                },
                "additional_values": {
                    "rms": 1.8,
                    "peak": 3.2,
                    "frequency": 50.0
                },
                "rms": 1.8,
                "peak": 3.2,
                "frequency": 50.0,
                "is_processed": True,
                "is_anomaly": False,
                "anomaly_score": 0.05,
                "created_at": "2024-07-15T12:00:00.123Z"
            }
        }
    
    @validator('quality', pre=True)
    def validate_quality(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [q.value for q in ReadingQuality]:
                raise ValueError(f'Qualidade invalida: {v}. Qualidades validas: {[q.value for q in ReadingQuality]}')
            return ReadingQuality(v)
        return v
    
    def is_valid(self) -> bool:
        """Verifica se a leitura e valida"""
        return self.metadata.quality != ReadingQuality.INVALID
    
    def is_critical(self) -> bool:
        """Verifica se a leitura e critica"""
        return self.threshold_violated == "critical"
    
    def get_latency(self) -> float:
        """Calcula a latencia em milissegundos"""
        if self.metadata.received_at is None or self.metadata.timestamp is None:
            return 0.0
        
        delta = self.metadata.received_at - self.metadata.timestamp
        return delta.total_seconds() * 1000
    
    def get_processing_time(self) -> float:
        """Calcula o tempo de processamento em milissegundos"""
        if self.metadata.processed_at is None or self.metadata.received_at is None:
            return 0.0
        
        delta = self.metadata.processed_at - self.metadata.received_at
        return delta.total_seconds() * 1000
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Reading':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()


class ReadingBatch(BaseModel):
    """
    Modelo de Batch de Leituras
    
    Representa um conjunto de leituras de um ou mais sensores.
    """
    
    id: str = Field(..., description="Identificador unico do batch")
    device_id: str = Field(..., description="ID do dispositivo")
    machine_id: Optional[str] = Field(None, description="ID da maquina")
    
    # Leituras
    readings: List[Reading] = Field(default_factory=list, description="Lista de leituras")
    
    # Metadados
    timestamp: datetime = Field(..., description="Timestamp do batch")
    received_at: Optional[datetime] = Field(None, description="Timestamp de recebimento")
    processed_at: Optional[datetime] = Field(None, description="Timestamp de processamento")
    
    # Informacoes de compressao
    is_compressed: bool = Field(False, description="Indica se o batch esta comprimido")
    compression_ratio: Optional[float] = Field(None, description="Taxa de compressao")
    original_size: Optional[int] = Field(None, description="Tamanho original em bytes")
    compressed_size: Optional[int] = Field(None, description="Tamanho comprimido em bytes")
    
    # Processamento
    is_processed: bool = Field(False, description="Indica se o batch foi processado")
    processing_errors: List[str] = Field(default_factory=list, description="Lista de erros de processamento")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "batch-001",
                "device_id": "device-001",
                "machine_id": "machine-001",
                "readings": [
                    {
                        "id": "reading-001",
                        "value": 2.5,
                        "unit": "g",
                        "metadata": {
                            "sensor_id": "sensor-001",
                            "device_id": "device-001",
                            "machine_id": "machine-001",
                            "timestamp": "2024-07-15T12:00:00.123Z",
                            "quality": "excellent",
                            "batch_id": "batch-001",
                            "sequence_number": 1
                        }
                    },
                    {
                        "id": "reading-002",
                        "value": 85.5,
                        "unit": "C",
                        "metadata": {
                            "sensor_id": "sensor-002",
                            "device_id": "device-001",
                            "machine_id": "machine-001",
                            "timestamp": "2024-07-15T12:00:00.123Z",
                            "quality": "good",
                            "batch_id": "batch-001",
                            "sequence_number": 2
                        }
                    }
                ],
                "timestamp": "2024-07-15T12:00:00Z",
                "received_at": "2024-07-15T12:00:01Z",
                "is_compressed": True,
                "compression_ratio": 0.75,
                "original_size": 1024,
                "compressed_size": 768,
                "is_processed": True,
                "created_at": "2024-07-15T12:00:00Z"
            }
        }
    
    def get_reading_count(self) -> int:
        """Retorna a quantidade de leituras"""
        return len(self.readings)
    
    def get_sensor_ids(self) -> List[str]:
        """Retorna os IDs dos sensores no batch"""
        return list(set([r.metadata.sensor_id for r in self.readings]))
    
    def get_latency(self) -> float:
        """Calcula a latencia media em milissegundos"""
        if not self.readings:
            return 0.0
        
        total = 0.0
        count = 0
        for reading in self.readings:
            latency = reading.get_latency()
            if latency > 0:
                total += latency
                count += 1
        
        if count == 0:
            return 0.0
        return total / count
    
    def has_errors(self) -> bool:
        """Verifica se o batch tem erros"""
        return len(self.processing_errors) > 0
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReadingBatch':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
