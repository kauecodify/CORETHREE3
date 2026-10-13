"""
CORETHREE3 - DNA de Maquinas
Modelo de Sensor

Define a estrutura de dados para sensores que monitoram maquinas industriais.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class SensorType(str, Enum):
    """Tipos de sensores suportados"""
    VIBRATION = "vibration"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    CURRENT = "current"
    VOLTAGE = "voltage"
    HUMIDITY = "humidity"
    ROTATION = "rotation"
    ACCELERATION = "acceleration"
    SOUND = "sound"
    IMAGE = "image"


class SensorStatus(str, Enum):
    """Status do sensor"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CALIBRATING = "calibrating"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class SensorCalibration(BaseModel):
    """Informacoes de calibracao do sensor"""
    last_calibration: Optional[datetime] = Field(None, description="Data da ultima calibracao")
    next_calibration: Optional[datetime] = Field(None, description="Data da proxima calibracao")
    calibration_certificate: Optional[str] = Field(None, description="Numero do certificado de calibracao")
    calibration_technician: Optional[str] = Field(None, description="Tecnico responsavel pela calibracao")
    calibration_notes: Optional[str] = Field(None, description="Notas da calibracao")
    
    # Parametros de calibracao
    offset: Optional[float] = Field(None, description="Offset de calibracao")
    gain: Optional[float] = Field(None, description="Ganho de calibracao")
    scale_factor: Optional[float] = Field(None, description="Fator de escala")
    
    # Validacao de calibracao
    is_calibrated: bool = Field(False, description="Indica se o sensor esta calibrado")
    calibration_accuracy: Optional[float] = Field(None, description="Precisao da calibracao em percentual")


class Sensor(BaseModel):
    """
    Modelo de Sensor
    
    Representa um sensor que monitora uma maquina industrial.
    """
    
    id: str = Field(..., description="Identificador unico do sensor")
    name: str = Field(..., description="Nome do sensor")
    sensor_type: SensorType = Field(..., description="Tipo do sensor")
    status: SensorStatus = Field(SensorStatus.INACTIVE, description="Status do sensor")
    
    # Relacionamentos
    device_id: Optional[str] = Field(None, description="ID do dispositivo associado")
    machine_id: Optional[str] = Field(None, description="ID da maquina associada")
    
    # Especificacoes
    manufacturer: Optional[str] = Field(None, description="Fabricante do sensor")
    model: Optional[str] = Field(None, description="Modelo do sensor")
    serial_number: Optional[str] = Field(None, description="Numero de serie do sensor")
    
    # Unidades de medicao
    units: List[str] = Field(default_factory=list, description="Unidades de medicao suportadas")
    primary_unit: str = Field("", description="Unidade primaria de medicao")
    
    # Configuracoes de amostragem
    sampling_rate: int = Field(10, description="Taxa de amostragem em Hz")
    batch_interval: int = Field(60, description="Intervalo de batch em segundos")
    
    # Faixas de operacao
    min_value: Optional[float] = Field(None, description="Valor minimo possivel")
    max_value: Optional[float] = Field(None, description="Valor maximo possivel")
    
    # Thresholds de alerta
    threshold_critical: Optional[float] = Field(None, description="Threshold critico")
    threshold_high: Optional[float] = Field(None, description="Threshold alto")
    threshold_medium: Optional[float] = Field(None, description="Threshold medio")
    threshold_low: Optional[float] = Field(None, description="Threshold baixo")
    
    # Precisao
    accuracy: Optional[float] = Field(None, description="Precisao do sensor em percentual")
    resolution: Optional[float] = Field(None, description="Resolucao do sensor")
    
    # Calibracao
    calibration: SensorCalibration = Field(default_factory=SensorCalibration, description="Informacoes de calibracao")
    
    # Localizacao
    location: Optional[str] = Field(None, description="Localizacao fisica do sensor")
    axis: Optional[str] = Field(None, description="Eixo de medicao (x, y, z)")
    
    # Conectividade
    interface_type: Optional[str] = Field(None, description="Tipo de interface (analogico, digital, I2C, SPI, etc.)")
    connection_status: bool = Field(False, description="Status da conexao")
    
    # Monitoramento
    last_reading: Optional[datetime] = Field(None, description="Timestamp da ultima leitura")
    last_calibration_check: Optional[datetime] = Field(None, description="Timestamp da ultima verificacao de calibracao")
    
    # Metricas de performance
    total_readings: int = Field(0, description="Total de leituras")
    failed_readings: int = Field(0, description="Total de leituras com falha")
    last_value: Optional[float] = Field(None, description="Ultimo valor lido")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "sensor-001",
                "name": "Sensor de Vibracao - Eixo X",
                "sensor_type": "vibration",
                "status": "active",
                "device_id": "device-001",
                "machine_id": "machine-001",
                "manufacturer": "PCB Piezotronics",
                "model": "ICP 356A01",
                "serial_number": "SN-VIB-001",
                "units": ["g", "m/s2"],
                "primary_unit": "g",
                "sampling_rate": 100,
                "batch_interval": 1,
                "min_value": -10.0,
                "max_value": 10.0,
                "threshold_critical": 8.0,
                "threshold_high": 5.0,
                "threshold_medium": 3.0,
                "threshold_low": 1.0,
                "accuracy": 1.0,
                "resolution": 0.001,
                "calibration": {
                    "last_calibration": "2024-06-01T00:00:00Z",
                    "next_calibration": "2025-06-01T00:00:00Z",
                    "calibration_certificate": "CAL-2024-001",
                    "calibration_technician": "Joao Silva",
                    "is_calibrated": True,
                    "calibration_accuracy": 99.5
                },
                "location": "Motor Principal - Lado Esquerdo",
                "axis": "x",
                "interface_type": "I2C",
                "connection_status": True,
                "last_reading": "2024-07-15T12:00:00Z",
                "total_readings": 150000,
                "failed_readings": 5,
                "last_value": 0.5,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-07-15T12:00:00Z"
            }
        }
    
    @validator('sensor_type', pre=True)
    def validate_sensor_type(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [st.value for st in SensorType]:
                raise ValueError(f'Tipo de sensor invalido: {v}. Tipos validos: {[st.value for st in SensorType]}')
            return SensorType(v)
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in SensorStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in SensorStatus]}')
            return SensorStatus(v)
        return v
    
    @validator('units')
    def validate_units(cls, v):
        if v is None:
            return []
        return list(set(v))  # Remover duplicados
    
    def is_active(self) -> bool:
        """Verifica se o sensor esta ativo"""
        return self.status == SensorStatus.ACTIVE and self.connection_status
    
    def is_calibrated(self) -> bool:
        """Verifica se o sensor esta calibrado"""
        return self.calibration.is_calibrated
    
    def needs_calibration(self) -> bool:
        """Verifica se o sensor precisa de calibracao"""
        if self.calibration.next_calibration is None:
            return True
        return datetime.utcnow() > self.calibration.next_calibration
    
    def get_health_status(self) -> str:
        """Determina o status de saude do sensor"""
        if not self.is_active():
            return "INACTIVE"
        elif self.needs_calibration():
            return "NEEDS_CALIBRATION"
        elif self.failed_readings > self.total_readings * 0.1:  # Mais de 10% de falhas
            return "DEGRADED"
        else:
            return "HEALTHY"
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Sensor':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
