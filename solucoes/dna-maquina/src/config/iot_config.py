"""
CORETHREE3 - DNA de Maquinas
Configuracoes de IoT
"""

import os
from typing import Dict, List, Any


class IoTConfig:
    """Configuracoes de IoT para monitoramento de maquinas"""
    
    # Configuracoes gerais
    ENABLE_IOT: bool = os.getenv("ENABLE_IOT", "True").lower() == "true"
    IOT_REGION: str = os.getenv("IOT_REGION", "us-east-1")
    
    # Configuracoes do IoT Core
    IOT_ENDPOINT: str = os.getenv("IOT_ENDPOINT", "")
    IOT_THING_TYPE: str = "DNAMaquina-Device"
    IOT_THING_NAME_PREFIX: str = "dna-maquina-"
    
    # Tipos de dispositivos
    DEVICE_TYPES: List[str] = [
        "motor",
        "bomb",
        "compressor",
        "forno",
        "caldeira",
        "gerador",
        "torno",
        "fresadora",
        "injetora",
        "generic"
    ]
    
    # Configuracoes de certificados
    CERTIFICATE_VALIDITY: int = 365  # Dias
    CERTIFICATE_AUTO_RENEW: bool = True
    CERTIFICATE_AUTO_ATTACH: bool = True
    
    # Configuracoes de politicas
    DEFAULT_POLICY_NAME: str = "DNAMaquina-Device-Policy"
    DEFAULT_POLICY_DOCUMENT: Dict[str, Any] = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "iot:Connect"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iot:Publish",
                    "iot:Receive"
                ],
                "Resource": [
                    "arn:aws:iot:REGION:ACCOUNT_ID:topic/corethree3/dna-maquina/*",
                    "arn:aws:iot:REGION:ACCOUNT_ID:topic/$aws/things/*/shadow/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iot:Subscribe"
                ],
                "Resource": [
                    "arn:aws:iot:REGION:ACCOUNT_ID:topicfilter/corethree3/dna-maquina/*"
                ]
            }
        ]
    }
    
    # Topicos MQTT
    MQTT_TOPICS: Dict[str, str] = {
        "data": "corethree3/dna-maquina/data",
        "alerts": "corethree3/dna-maquina/alerts",
        "commands": "corethree3/dna-maquina/commands",
        "status": "corethree3/dna-maquina/status",
        "heartbeat": "corethree3/dna-maquina/heartbeat",
        "shadow_update": "$aws/things/+/shadow/update",
        "shadow_get": "$aws/things/+/shadow/get"
    }
    
    # Configuracoes de QoS
    MQTT_QOS_DATA: int = 1  # QoS 1 para dados
    MQTT_QOS_ALERTS: int = 1  # QoS 1 para alertas
    MQTT_QOS_COMMANDS: int = 1  # QoS 1 para comandos
    MQTT_QOS_STATUS: int = 0  # QoS 0 para status
    
    # Configuracoes de retain
    MQTT_RETAIN_DATA: bool = False
    MQTT_RETAIN_ALERTS: bool = False
    MQTT_RETAIN_COMMANDS: bool = False
    MQTT_RETAIN_STATUS: bool = True
    
    # Configuracoes de sensores
    SENSOR_TYPES: List[str] = [
        "vibration",
        "temperature",
        "pressure",
        "current",
        "voltage",
        "humidity",
        "rotation",
        "acceleration",
        "sound",
        "image"
    ]
    
    # Configuracoes padrao de sensores
    SENSOR_CONFIGS: Dict[str, Dict[str, Any]] = {
        "vibration": {
            "enabled": True,
            "sampling_rate": 100,  # Hz
            "batch_interval": 1,  # Segundos
            "axes": ["x", "y", "z"],
            "units": ["g"],
            "min_value": -10,
            "max_value": 10,
            "threshold_critical": 8.0,
            "threshold_high": 5.0,
            "threshold_medium": 3.0
        },
        "temperature": {
            "enabled": True,
            "sampling_rate": 1,  # Hz
            "batch_interval": 60,  # Segundos
            "units": ["C", "F"],
            "min_value": -50,
            "max_value": 200,
            "threshold_critical": 150,
            "threshold_high": 120,
            "threshold_medium": 100
        },
        "pressure": {
            "enabled": True,
            "sampling_rate": 10,  # Hz
            "batch_interval": 10,  # Segundos
            "units": ["bar", "psi"],
            "min_value": 0,
            "max_value": 1000,
            "threshold_critical": 900,
            "threshold_high": 800,
            "threshold_medium": 700
        },
        "current": {
            "enabled": True,
            "sampling_rate": 100,  # Hz
            "batch_interval": 1,  # Segundos
            "units": ["A"],
            "min_value": 0,
            "max_value": 1000,
            "threshold_critical": 950,
            "threshold_high": 900,
            "threshold_medium": 850
        },
        "voltage": {
            "enabled": True,
            "sampling_rate": 100,  # Hz
            "batch_interval": 1,  # Segundos
            "units": ["V"],
            "min_value": 0,
            "max_value": 1000,
            "threshold_critical": 950,
            "threshold_high": 900,
            "threshold_medium": 850
        },
        "humidity": {
            "enabled": True,
            "sampling_rate": 1,  # Hz
            "batch_interval": 60,  # Segundos
            "units": ["%"],
            "min_value": 0,
            "max_value": 100,
            "threshold_critical": 90,
            "threshold_high": 80,
            "threshold_medium": 70
        }
    }
    
    # Configuracoes de processamento edge (Greengrass)
    GREENGRASS_ENABLED: bool = os.getenv("GREENGRASS_ENABLED", "True").lower() == "true"
    GREENGRASS_GROUP_NAME: str = "DNAMaquina-Group"
    GREENGRASS_CORE_NAME: str = "DNAMaquina-Core"
    GREENGRASS_COMPONENT_NAME: str = "DNAMaquina-Component"
    
    # Funcoes de processamento edge
    EDGE_FUNCTIONS: List[str] = [
        "filter_data",
        "aggregate_data",
        "detect_anomalies",
        "predict_failures",
        "compress_data"
    ]
    
    # Configuracoes de shadow
    SHADOW_ENABLED: bool = True
    SHADOW_SYNC_INTERVAL: int = 60  # Segundos
    
    # Configuracoes de OTA (Over-the-Air updates)
    OTA_ENABLED: bool = True
    OTA_JOB_NAME: str = "DNAMaquina-OTA-Job"
    OTA_ROLE_NAME: str = "DNAMaquina-OTA-Role"
    OTA_BUCKET_NAME: str = os.getenv("OTA_BUCKET_NAME", "corethree3-dna-maquina-ota")
    OTA_FIRMWARE_PREFIX: str = "firmware"
    
    # Configuracoes de seguranca
    IOT_AUTH_ENABLED: bool = True
    IOT_AUTH_PROVIDER: str = "AWS_IOT"  # AWS_IOT, CUSTOM
    IOT_CUSTOM_AUTH_LAMBDA: str = ""
    
    # Configuracoes de logging
    IOT_LOG_LEVEL: str = os.getenv("IOT_LOG_LEVEL", "INFO")
    IOT_LOG_FORMAT: str = "JSON"
    IOT_LOG_TO_CLOUDWATCH: bool = True
    
    # Configuracoes de monitoramento
    IOT_MONITOR_INTERVAL: int = 60  # Segundos
    IOT_MONITOR_METRICS: List[str] = [
        "connected_devices",
        "disconnected_devices",
        "messages_received",
        "messages_processed",
        "latency",
        "errors"
    ]
    
    @classmethod
    def get_sensor_config(cls, sensor_type: str) -> Dict[str, Any]:
        """Obter configuracao de um sensor"""
        return cls.SENSOR_CONFIGS.get(sensor_type, {})
    
    @classmethod
    def get_mqtt_topic(cls, topic_type: str) -> str:
        """Obter topico MQTT"""
        return cls.MQTT_TOPICS.get(topic_type, cls.MQTT_TOPICS["data"])
    
    @classmethod
    def get_device_type_config(cls, device_type: str) -> Dict[str, Any]:
        """Obter configuracao de um tipo de dispositivo"""
        # Configuracoes padrao para todos os dispositivos
        base_config = {
            "sensors": ["vibration", "temperature"],
            "sampling_rate": 10,
            "batch_interval": 60,
            "alert_threshold": 0.9
        }
        
        # Configuracoes especificas por tipo
        device_configs = {
            "motor": {
                "sensors": ["vibration", "temperature", "current"],
                "sampling_rate": 100,
                "batch_interval": 1,
                "critical_sensors": ["vibration", "temperature"]
            },
            "bomb": {
                "sensors": ["vibration", "temperature", "pressure", "current"],
                "sampling_rate": 50,
                "batch_interval": 5,
                "critical_sensors": ["vibration", "pressure"]
            },
            "compressor": {
                "sensors": ["vibration", "temperature", "pressure", "current"],
                "sampling_rate": 100,
                "batch_interval": 1,
                "critical_sensors": ["vibration", "temperature", "pressure"]
            },
            "forno": {
                "sensors": ["temperature", "current", "voltage"],
                "sampling_rate": 10,
                "batch_interval": 30,
                "critical_sensors": ["temperature"]
            },
            "caldeira": {
                "sensors": ["temperature", "pressure", "current"],
                "sampling_rate": 10,
                "batch_interval": 30,
                "critical_sensors": ["temperature", "pressure"]
            }
        }
        
        # Mesclar configuracoes
        device_config = device_configs.get(device_type, {})
        config = {**base_config, **device_config}
        
        # Adicionar configuracoes dos sensores
        config["sensor_configs"] = {}
        for sensor in config["sensors"]:
            config["sensor_configs"][sensor] = cls.get_sensor_config(sensor)
        
        return config


# Instancia das configuracoes
iot_config = IoTConfig()
