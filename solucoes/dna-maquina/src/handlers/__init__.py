"""
CORETHREE3 - DNA de Maquinas
Handlers

Este modulo contem todos os handlers para o sistema DNA de Maquinas.
"""

from .iot_handler import IoTHandler
from .data_handler import DataHandler
from .alert_handler import AlertHandler
from .prediction_handler import PredictionHandler
from .maintenance_handler import MaintenanceHandler

__all__ = [
    "IoTHandler",
    "DataHandler",
    "AlertHandler",
    "PredictionHandler",
    "MaintenanceHandler"
]
