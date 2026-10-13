"""
CORETHREE3 - DNA de Maquinas
Modelo de Maquina Industrial

Define a estrutura de dados para maquinas industriais monitoradas pelo sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class MachineType(str, Enum):
    """Tipos de maquinas industriais"""
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


class MachineStatus(str, Enum):
    """Status da maquina"""
    OPERATIONAL = "operational"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    STOPPED = "stopped"
    ERROR = "error"
    WARNING = "warning"


class MachineSpecs(BaseModel):
    """Especificacoes tecnicas da maquina"""
    power_rating: Optional[float] = Field(None, description="Potencia nominal em kW")
    voltage_rating: Optional[float] = Field(None, description="Tensao nominal em V")
    current_rating: Optional[float] = Field(None, description="Corrente nominal em A")
    frequency_rating: Optional[float] = Field(None, description="Frequencia nominal em Hz")
    rpm_rating: Optional[float] = Field(None, description="RPM nominal")
    pressure_rating: Optional[float] = Field(None, description="Pressao nominal em bar")
    temperature_rating: Optional[float] = Field(None, description="Temperatura nominal em C")
    weight: Optional[float] = Field(None, description="Peso em kg")
    dimensions: Optional[str] = Field(None, description="Dimensoes (LxWxH)")
    efficiency: Optional[float] = Field(None, description="Eficiencia em percentual")
    
    # Especificacoes do fabricante
    manufacturer: Optional[str] = Field(None, description="Fabricante")
    model: Optional[str] = Field(None, description="Modelo")
    year: Optional[int] = Field(None, description="Ano de fabricacao")
    
    # Especificacoes de operacao
    max_operating_temperature: Optional[float] = Field(None, description="Temperatura maxima de operacao em C")
    max_operating_pressure: Optional[float] = Field(None, description="Pressao maxima de operacao em bar")
    max_rpm: Optional[float] = Field(None, description="RPM maxima")
    
    # Especificacoes de manutencao
    mtbf: Optional[float] = Field(None, description="Mean Time Between Failures em horas")
    mttr: Optional[float] = Field(None, description="Mean Time To Repair em horas")
    expected_lifetime: Optional[float] = Field(None, description="Vida util esperada em anos")


class Machine(BaseModel):
    """
    Modelo de Maquina Industrial
    
    Representa uma maquina industrial monitorada pelo sistema DNA de Maquinas.
    """
    
    id: str = Field(..., description="Identificador unico da maquina")
    name: str = Field(..., description="Nome da maquina")
    machine_type: MachineType = Field(..., description="Tipo da maquina")
    status: MachineStatus = Field(MachineStatus.STOPPED, description="Status da maquina")
    
    # Relacionamentos
    device_ids: List[str] = Field(default_factory=list, description="IDs dos dispositivos associados")
    parent_machine_id: Optional[str] = Field(None, description="ID da maquina pai (para linhas de producao)")
    child_machine_ids: List[str] = Field(default_factory=list, description="IDs das maquinas filhas")
    production_line_id: Optional[str] = Field(None, description="ID da linha de producao")
    facility_id: Optional[str] = Field(None, description="ID da instalao/fabrica")
    
    # Especificacoes
    specs: MachineSpecs = Field(default_factory=MachineSpecs, description="Especificacoes tecnicas")
    
    # Localizacao
    location: Optional[str] = Field(None, description="Localizacao fisica da maquina")
    gps_latitude: Optional[float] = Field(None, description="Latitude GPS")
    gps_longitude: Optional[float] = Field(None, description="Longitude GPS")
    gps_altitude: Optional[float] = Field(None, description="Altitude GPS")
    
    # Cronograma
    installation_date: Optional[datetime] = Field(None, description="Data de instalacao")
    commissioning_date: Optional[datetime] = Field(None, description="Data de comissionamento")
    last_maintenance: Optional[datetime] = Field(None, description="Data da ultima manutencao")
    next_maintenance: Optional[datetime] = Field(None, description="Data da proxima manutencao")
    
    # Operacao
    last_operation_start: Optional[datetime] = Field(None, description="Timestamp do inicio da ultima operacao")
    last_operation_end: Optional[datetime] = Field(None, description="Timestamp do fim da ultima operacao")
    total_operating_hours: float = Field(0.0, description="Total de horas em operacao")
    total_cycles: int = Field(0, description="Total de ciclos de operacao")
    
    # Monitoramento
    last_health_check: Optional[datetime] = Field(None, description="Timestamp da ultima verificacao de saúde")
    health_score: float = Field(100.0, description="Score de saúde (0-100)")
    
    # Alertas
    active_alerts: List[str] = Field(default_factory=list, description="IDs dos alertas ativos")
    total_alerts: int = Field(0, description="Total de alertas gerados")
    critical_alerts: int = Field(0, description="Total de alertas criticos")
    
    # Predicoes
    last_prediction: Optional[datetime] = Field(None, description="Timestamp da ultima predicao")
    predicted_failure_date: Optional[datetime] = Field(None, description="Data prevista de falha")
    remaining_useful_life: Optional[float] = Field(None, description="Vida util restante em dias")
    failure_probability: float = Field(0.0, description="Probabilidade de falha (0-1)")
    
    # Custos
    acquisition_cost: Optional[float] = Field(None, description="Custo de aquisicao em BRL")
    maintenance_cost: Optional[float] = Field(None, description="Custo de manutencao em BRL")
    operational_cost: Optional[float] = Field(None, description="Custo operacional em BRL")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "machine-001",
                "name": "Motor Principal - Linha de Producao A",
                "machine_type": "motor",
                "status": "operational",
                "device_ids": ["device-001", "device-002"],
                "production_line_id": "line-a",
                "facility_id": "facility-001",
                "specs": {
                    "power_rating": 55.0,
                    "voltage_rating": 440.0,
                    "current_rating": 85.0,
                    "frequency_rating": 60.0,
                    "rpm_rating": 1750.0,
                    "manufacturer": "Siemens",
                    "model": "1LE1 Series",
                    "year": 2022,
                    "mtbf": 50000.0,
                    "mttr": 4.0,
                    "expected_lifetime": 15.0
                },
                "location": "Linha de Producao A - Setor 1",
                "installation_date": "2022-01-15T00:00:00Z",
                "commissioning_date": "2022-02-01T00:00:00Z",
                "last_maintenance": "2024-06-01T00:00:00Z",
                "next_maintenance": "2024-12-01T00:00:00Z",
                "total_operating_hours": 25000.5,
                "total_cycles": 150000,
                "health_score": 95.5,
                "active_alerts": ["alert-001"],
                "total_alerts": 25,
                "critical_alerts": 2,
                "failure_probability": 0.05,
                "remaining_useful_life": 365.0,
                "acquisition_cost": 150000.0,
                "created_at": "2022-01-01T00:00:00Z",
                "updated_at": "2024-07-15T12:00:00Z"
            }
        }
    
    @validator('machine_type', pre=True)
    def validate_machine_type(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [mt.value for mt in MachineType]:
                raise ValueError(f'Tipo de maquina invalido: {v}. Tipos validos: {[mt.value for mt in MachineType]}')
            return MachineType(v)
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in MachineStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in MachineStatus]}')
            return MachineStatus(v)
        return v
    
    @validator('device_ids', 'child_machine_ids', 'active_alerts')
    def validate_ids(cls, v):
        if v is None:
            return []
        return list(set(v))  # Remover duplicados
    
    def is_operational(self) -> bool:
        """Verifica se a maquina esta operacional"""
        return self.status == MachineStatus.OPERATIONAL
    
    def is_in_maintenance(self) -> bool:
        """Verifica se a maquina esta em manutencao"""
        return self.status == MachineStatus.MAINTENANCE
    
    def has_critical_alerts(self) -> bool:
        """Verifica se a maquina tem alertas criticos"""
        return self.critical_alerts > 0
    
    def get_utilization(self) -> float:
        """Calcula a utilizacao da maquina em percentual"""
        if self.expected_lifetime is None or self.expected_lifetime == 0:
            return 0.0
        
        years_operating = self.total_operating_hours / (24 * 365)
        return min((years_operating / self.expected_lifetime) * 100, 100.0)
    
    def get_maintenance_urgency(self) -> str:
        """Determina a urgencia de manutencao"""
        if self.health_score < 30:
            return "CRITICAL"
        elif self.health_score < 60:
            return "HIGH"
        elif self.health_score < 80:
            return "MEDIUM"
        elif self.failure_probability > 0.3:
            return "HIGH"
        elif self.failure_probability > 0.1:
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
    def from_dict(cls, data: Dict) -> 'Machine':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
