"""
CORETHREE3 - DNA de Maquinas
Modelo de Dispositivo IoT

Define a estrutura de dados para dispositivos IoT que monitoram maquinas industriais.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class DeviceType(str, Enum):
    """Tipos de dispositivos IoT suportados"""
    MOTOR = "motor"
    BOMB = "bomb"
    COMPRESSOR = "compressor"
    FORNO = "forno"
    CALDEIRA = "caldeira"
    GERADOR = "gerador"
    TORNO = "torno"
    FRESADORA = "fresadora"
    INJETORA = "injetora"
    GENERIC = "generic"


class DeviceStatus(str, Enum):
    """Status do dispositivo IoT"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    DECOMMISSIONED = "decommissioned"


class DeviceMetadata(BaseModel):
    """Metadados do dispositivo"""
    manufacturer: str = Field(..., description="Fabricante do dispositivo")
    model: str = Field(..., description="Modelo do dispositivo")
    serial_number: str = Field(..., description="Numero de serie do dispositivo")
    firmware_version: str = Field("1.0.0", description="Versao do firmware")
    hardware_version: str = Field("1.0", description="Versao do hardware")
    location: Optional[str] = Field(None, description="Localizacao fisica do dispositivo")
    installation_date: Optional[datetime] = Field(None, description="Data de instalacao")
    last_calibration: Optional[datetime] = Field(None, description="Data da ultima calibracao")
    next_calibration: Optional[datetime] = Field(None, description="Data da proxima calibracao")


class Device(BaseModel):
    """
    Modelo de Dispositivo IoT
    
    Representa um dispositivo IoT que monitora uma ou mais maquinas industriais.
    """
    
    id: str = Field(..., description="Identificador unico do dispositivo")
    name: str = Field(..., description="Nome do dispositivo")
    device_type: DeviceType = Field(..., description="Tipo do dispositivo")
    status: DeviceStatus = Field(DeviceStatus.OFFLINE, description="Status do dispositivo")
    
    # Relacionamentos
    machine_id: Optional[str] = Field(None, description="ID da maquina monitorada")
    parent_device_id: Optional[str] = Field(None, description="ID do dispositivo pai (para hierarquias)")
    child_device_ids: List[str] = Field(default_factory=list, description="IDs dos dispositivos filhos")
    
    # Metadados
    metadata: DeviceMetadata = Field(..., description="Metadados do dispositivo")
    
    # Configuracoes
    sampling_rate: int = Field(10, description="Taxa de amostragem em Hz")
    batch_interval: int = Field(60, description="Intervalo de batch em segundos")
    
    # Sensores associados
    sensor_ids: List[str] = Field(default_factory=list, description="IDs dos sensores associados")
    critical_sensors: List[str] = Field(default_factory=list, description="IDs dos sensores criticos")
    
    # Conectividade
    iot_thing_name: str = Field(..., description="Nome da Thing no AWS IoT Core")
    iot_thing_arn: Optional[str] = Field(None, description="ARN da Thing no AWS IoT Core")
    iot_certificate_id: Optional[str] = Field(None, description="ID do certificado IoT")
    iot_endpoint: Optional[str] = Field(None, description="Endpoint do IoT Core")
    
    # Monitoramento
    last_heartbeat: Optional[datetime] = Field(None, description="Timestamp do ultimo heartbeat")
    last_data_received: Optional[datetime] = Field(None, description="Timestamp dos ultimos dados recebidos")
    last_connection: Optional[datetime] = Field(None, description="Timestamp da ultima conexao")
    connection_duration: Optional[float] = Field(None, description="Duracao da ultima conexao em segundos")
    
    # Metricas de performance
    messages_sent: int = Field(0, description="Total de mensagens enviadas")
    messages_received: int = Field(0, description="Total de mensagens recebidas")
    bytes_sent: int = Field(0, description="Total de bytes enviados")
    bytes_received: int = Field(0, description="Total de bytes recebidos")
    errors: int = Field(0, description="Total de erros")
    
    # Localizacao GPS (opcional)
    gps_latitude: Optional[float] = Field(None, description="Latitude GPS")
    gps_longitude: Optional[float] = Field(None, description="Longitude GPS")
    gps_altitude: Optional[float] = Field(None, description="Altitude GPS")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    
    # Configuracoes de seguranca
    encryption_enabled: bool = Field(True, description="Criptografia habilitada")
    authentication_required: bool = Field(True, description="Autenticacao requerida")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "device-001",
                "name": "Motor Principal - Linha 1",
                "device_type": "motor",
                "status": "online",
                "machine_id": "machine-001",
                "metadata": {
                    "manufacturer": "Siemens",
                    "model": "SIMOTICS GP",
                    "serial_number": "SN12345678",
                    "firmware_version": "2.1.0",
                    "hardware_version": "1.0",
                    "location": "Linha de Producao A",
                    "installation_date": "2024-01-15T00:00:00Z",
                    "last_calibration": "2024-06-01T00:00:00Z",
                    "next_calibration": "2025-06-01T00:00:00Z"
                },
                "sampling_rate": 100,
                "batch_interval": 1,
                "sensor_ids": ["sensor-001", "sensor-002", "sensor-003"],
                "critical_sensors": ["sensor-001", "sensor-002"],
                "iot_thing_name": "dna-maquina-device-001",
                "last_heartbeat": "2024-07-15T12:00:00Z",
                "last_data_received": "2024-07-15T12:00:00Z",
                "messages_sent": 150000,
                "messages_received": 145000,
                "errors": 5,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-07-15T12:00:00Z"
            }
        }
    
    @validator('device_type', pre=True)
    def validate_device_type(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [dt.value for dt in DeviceType]:
                raise ValueError(f'Tipo de dispositivo invalido: {v}. Tipos validos: {[dt.value for dt in DeviceType]}')
            return DeviceType(v)
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in DeviceStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in DeviceStatus]}')
            return DeviceStatus(v)
        return v
    
    @validator('sensor_ids', 'critical_sensors')
    def validate_sensor_ids(cls, v):
        if v is None:
            return []
        return list(set(v))  # Remover duplicados
    
    def is_online(self) -> bool:
        """Verifica se o dispositivo esta online"""
        return self.status == DeviceStatus.ONLINE
    
    def is_critical(self) -> bool:
        """Verifica se o dispositivo tem status critico"""
        return self.status == DeviceStatus.ERROR
    
    def get_uptime(self) -> float:
        """Calcula o uptime do dispositivo em segundos"""
        if self.last_connection is None:
            return 0.0
        
        now = datetime.utcnow()
        if self.status == DeviceStatus.ONLINE:
            return (now - self.last_connection).total_seconds()
        else:
            return self.connection_duration or 0.0
    
    def get_error_rate(self) -> float:
        """Calcula a taxa de erros"""
        total = self.messages_sent + self.messages_received
        if total == 0:
            return 0.0
        return self.errors / total
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Device':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
