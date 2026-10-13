"""
CORETHREE3 - DNA de Maquinas
Modelos de Dados

Este modulo contem todos os modelos de dados Pydantic para o sistema DNA de Maquinas.
Os modelos sao usados para validacao, serializacao e documentacao da API.
"""

from .device import Device, DeviceType, DeviceStatus, DeviceMetadata
from .machine import Machine, MachineType, MachineStatus, MachineSpecs
from .sensor import Sensor, SensorType, SensorStatus, SensorCalibration
from .reading import Reading, ReadingBatch, ReadingMetadata
from .alert import Alert, AlertSeverity, AlertStatus, AlertType
from .prediction import Prediction, PredictionType, PredictionStatus
from .maintenance import Maintenance, MaintenanceType, MaintenanceStatus

__all__ = [
    "Device",
    "DeviceType",
    "DeviceStatus",
    "DeviceMetadata",
    "Machine",
    "MachineType",
    "MachineStatus",
    "MachineSpecs",
    "Sensor",
    "SensorType",
    "SensorStatus",
    "SensorCalibration",
    "Reading",
    "ReadingBatch",
    "ReadingMetadata",
    "Alert",
    "AlertSeverity",
    "AlertStatus",
    "AlertType",
    "Prediction",
    "PredictionType",
    "PredictionStatus",
    "Maintenance",
    "MaintenanceType",
    "MaintenanceStatus"
]
