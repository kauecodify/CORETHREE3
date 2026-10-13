"""
CORETHREE3 - DNA de Maquinas
Modelo de Manutencao

Define a estrutura de dados para registros de manutencao.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class MaintenanceType(str, Enum):
    """Tipo de manutencao"""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"
    INSPECTION = "inspection"
    CALIBRATION = "calibration"
    REPLACEMENT = "replacement"
    UPGRADE = "upgrade"
    CLEANING = "cleaning"
    LUBRICATION = "lubrication"


class MaintenanceStatus(str, Enum):
    """Status da manutencao"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class MaintenancePriority(str, Enum):
    """Prioridade da manutencao"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Maintenance(BaseModel):
    """
    Modelo de Manutencao
    
    Representa um registro de manutencao para uma maquina ou dispositivo.
    """
    
    id: str = Field(..., description="Identificador unico da manutencao")
    
    # Classificacao
    maintenance_type: MaintenanceType = Field(..., description="Tipo de manutencao")
    status: MaintenanceStatus = Field(MaintenanceStatus.SCHEDULED, description="Status da manutencao")
    priority: MaintenancePriority = Field(MaintenancePriority.MEDIUM, description="Prioridade da manutencao")
    
    # Relacionamentos
    device_id: Optional[str] = Field(None, description="ID do dispositivo")
    machine_id: Optional[str] = Field(None, description="ID da maquina")
    sensor_ids: List[str] = Field(default_factory=list, description="IDs dos sensores afetados")
    
    # Informacoes de agendamento
    scheduled_start: datetime = Field(..., description="Data/hora de inicio agendada")
    scheduled_end: Optional[datetime] = Field(None, description="Data/hora de termino agendada")
    
    # Informacoes de execucao
    actual_start: Optional[datetime] = Field(None, description="Data/hora de inicio real")
    actual_end: Optional[datetime] = Field(None, description="Data/hora de termino real")
    
    # Duracao
    estimated_duration: Optional[float] = Field(None, description="Duracao estimada em horas")
    actual_duration: Optional[float] = Field(None, description="Duracao real em horas")
    
    # Responsaveis
    assigned_to: Optional[str] = Field(None, description="Usuario/equipe responsavel")
    assigned_team: Optional[str] = Field(None, description="Equipe responsavel")
    supervisor: Optional[str] = Field(None, description="Supervisor")
    
    # Descricao
    title: str = Field(..., description="Titulo da manutencao")
    description: str = Field(..., description="Descricao da manutencao")
    
    # Acoes executadas
    actions_performed: List[str] = Field(default_factory=list, description="Acoes executadas")
    parts_replaced: List[str] = Field(default_factory=list, description="Pecas substituidas")
    tools_used: List[str] = Field(default_factory=list, description="Ferramentas usadas")
    
    # Materiais
    materials_used: List[str] = Field(default_factory=list, description="Materiais usados")
    
    # Custos
    labor_cost: Optional[float] = Field(None, description="Custo de mao de obra em BRL")
    material_cost: Optional[float] = Field(None, description="Custo de materiais em BRL")
    total_cost: Optional[float] = Field(None, description="Custo total em BRL")
    
    # Predicao associada
    prediction_id: Optional[str] = Field(None, description="ID da predicao associada")
    alert_ids: List[str] = Field(default_factory=list, description="IDs dos alertas associados")
    
    # Avaliacao
    root_cause: Optional[str] = Field(None, description="Causa raiz")
    effectiveness: Optional[float] = Field(None, description="Efetividade da manutencao (0-1)")
    notes: Optional[str] = Field(None, description="Notas")
    
    # Documentacao
    work_order_number: Optional[str] = Field(None, description="Numero da ordem de servico")
    invoice_number: Optional[str] = Field(None, description="Numero da nota fiscal")
    attachments: List[str] = Field(default_factory=list, description="Anexos (URLs)")
    
    # Metadados
    source: str = Field("system", description="Fonte da manutencao (system, manual)")
    tags: List[str] = Field(default_factory=list, description="Tags da manutencao")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da ultima atualizacao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "maintenance-001",
                "maintenance_type": "preventive",
                "status": "completed",
                "priority": "high",
                "device_id": "device-001",
                "machine_id": "machine-001",
                "sensor_ids": ["sensor-001"],
                "scheduled_start": "2024-07-15T08:00:00Z",
                "scheduled_end": "2024-07-15T12:00:00Z",
                "actual_start": "2024-07-15T08:15:00Z",
                "actual_end": "2024-07-15T11:45:00Z",
                "estimated_duration": 4.0,
                "actual_duration": 3.5,
                "assigned_to": "joao.silva",
                "assigned_team": "Manutencao Mecanica",
                "supervisor": "maria.santos",
                "title": "Manutencao preventiva - Motor Principal",
                "description": "Troca de oleo, verificacao de rolamentos e ajustes gerais",
                "actions_performed": [
                    "Troca de oleo lubrificante",
                    "Verificacao de rolamentos",
                    "Ajuste de tensoes de correias"
                ],
                "parts_replaced": ["Filtro de oleo", "Correia principal"],
                "materials_used": ["Oleo lubrificante SAE 40", "Graxa industrial"],
                "labor_cost": 1500.0,
                "material_cost": 800.0,
                "total_cost": 2300.0,
                "prediction_id": "prediction-001",
                "alert_ids": ["alert-001"],
                "root_cause": "Desgaste normal por uso continuo",
                "effectiveness": 0.95,
                "notes": "Motor operando normalmente apos manutencao",
                "work_order_number": "WO-2024-001",
                "invoice_number": "NF-2024-001",
                "source": "system",
                "tags": ["preventive", "motor", "lubrication"],
                "created_at": "2024-07-10T00:00:00Z",
                "updated_at": "2024-07-15T11:45:00Z"
            }
        }
    
    @validator('maintenance_type', pre=True)
    def validate_maintenance_type(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [mt.value for mt in MaintenanceType]:
                raise ValueError(f'Tipo de manutencao invalido: {v}. Tipos validos: {[mt.value for mt in MaintenanceType]}')
            return MaintenanceType(v)
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in MaintenanceStatus]:
                raise ValueError(f'Status invalido: {v}. Status validos: {[s.value for s in MaintenanceStatus]}')
            return MaintenanceStatus(v)
        return v
    
    @validator('priority', pre=True)
    def validate_priority(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [p.value for p in MaintenancePriority]:
                raise ValueError(f'Prioridade invalida: {v}. Prioridades validas: {[p.value for p in MaintenancePriority]}')
            return MaintenancePriority(v)
        return v
    
    def is_completed(self) -> bool:
        """Verifica se a manutencao foi concluida"""
        return self.status == MaintenanceStatus.COMPLETED
    
    def is_overdue(self) -> bool:
        """Verifica se a manutencao esta atrasada"""
        if self.actual_start is None and self.scheduled_start is not None:
            return datetime.utcnow() > self.scheduled_start
        return False
    
    def get_duration(self) -> Optional[float]:
        """Calcula a duracao real em horas"""
        if self.actual_start is None or self.actual_end is None:
            return None
        
        delta = self.actual_end - self.actual_start
        return delta.total_seconds() / 3600
    
    def get_efficiency(self) -> Optional[float]:
        """Calcula a eficiencia (duracao real / duracao estimada)"""
        if self.estimated_duration is None or self.actual_duration is None:
            return None
        
        if self.estimated_duration == 0:
            return None
        
        return self.estimated_duration / self.actual_duration
    
    def to_dict(self) -> Dict:
        """Converte para dicionario"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Maintenance':
        """Cria a partir de um dicionario"""
        return cls(**data)
    
    @classmethod
    def get_schema(cls) -> Dict:
        """Retorna o schema JSON"""
        return cls.model_json_schema()
