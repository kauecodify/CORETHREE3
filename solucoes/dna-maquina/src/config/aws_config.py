"""
CORETHREE3 - DNA de Maquinas
Configuracoes AWS
"""

import os
from typing import Dict, Any


class AWSConfig:
    """Configuracoes especificas da AWS"""
    
    # Regiao
    REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Conta AWS (opcional)
    ACCOUNT_ID: str = os.getenv("AWS_ACCOUNT_ID", "")
    
    # Nomes de recursos
    MODULE_NAME: str = "dna-maquina"
    
    # IoT Core
    IOT_THING_TYPE: str = f"{MODULE_NAME}-device"
    IOT_POLICY_NAME: str = f"{MODULE_NAME}-policy"
    IOT_CERTIFICATE_ID: str = f"{MODULE_NAME}-certificate"
    IOT_ROLE_NAME: str = f"{MODULE_NAME}-role"
    
    # IoT Greengrass
    GREENGRASS_GROUP_NAME: str = f"{MODULE_NAME}-group"
    GREENGRASS_CORE_NAME: str = f"{MODULE_NAME}-core"
    
    # Timestream
    TIMESTREAM_DATABASE_NAME: str = f"{MODULE_NAME}-db"
    TIMESTREAM_TABLE_VIBRATION: str = f"{MODULE_NAME}-vibration"
    TIMESTREAM_TABLE_TEMPERATURE: str = f"{MODULE_NAME}-temperature"
    TIMESTREAM_TABLE_PRESSURE: str = f"{MODULE_NAME}-pressure"
    TIMESTREAM_TABLE_CURRENT: str = f"{MODULE_NAME}-current"
    TIMESTREAM_TABLE_VOLTAGE: str = f"{MODULE_NAME}-voltage"
    TIMESTREAM_TABLE_HUMIDITY: str = f"{MODULE_NAME}-humidity"
    TIMESTREAM_TABLE_GENERIC: str = f"{MODULE_NAME}-generic"
    
    # S3
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", f"corethree3-{MODULE_NAME}-{ACCOUNT_ID}")
    S3_PREFIX: str = "dna-maquina"
    S3_DATA_PREFIX: str = f"{S3_PREFIX}/data"
    S3_MODELS_PREFIX: str = f"{S3_PREFIX}/models"
    S3_LOGS_PREFIX: str = f"{S3_PREFIX}/logs"
    S3_FIRMWARE_PREFIX: str = f"{S3_PREFIX}/firmware"
    
    # DynamoDB
    DYNAMODB_TABLE_DEVICES: str = f"{MODULE_NAME}-devices"
    DYNAMODB_TABLE_MACHINES: str = f"{MODULE_NAME}-machines"
    DYNAMODB_TABLE_ALERTS: str = f"{MODULE_NAME}-alerts"
    DYNAMODB_TABLE_PREDICTIONS: str = f"{MODULE_NAME}-predictions"
    DYNAMODB_TABLE_MAINTENANCE: str = f"{MODULE_NAME}-maintenance"
    DYNAMODB_TABLE_SENSORS: str = f"{MODULE_NAME}-sensors"
    
    # Lambda
    LAMBDA_FUNCTION_PROCESS: str = f"{MODULE_NAME}-process"
    LAMBDA_FUNCTION_ANALYSIS: str = f"{MODULE_NAME}-analysis"
    LAMBDA_FUNCTION_PREDICTION: str = f"{MODULE_NAME}-prediction"
    LAMBDA_FUNCTION_ALERT: str = f"{MODULE_NAME}-alert"
    LAMBDA_LAYER_NAME: str = f"{MODULE_NAME}-layer"
    
    # API Gateway
    API_GATEWAY_NAME: str = f"{MODULE_NAME}-api"
    API_GATEWAY_STAGE: str = os.getenv("ENVIRONMENT", "dev")
    
    # Step Functions
    STATE_MACHINE_PROCESS: str = f"{MODULE_NAME}-process-state-machine"
    STATE_MACHINE_ANALYSIS: str = f"{MODULE_NAME}-analysis-state-machine"
    STATE_MACHINE_PREDICTION: str = f"{MODULE_NAME}-prediction-state-machine"
    
    # EventBridge
    EVENT_BUS_NAME: str = f"{MODULE_NAME}-bus"
    
    # SNS
    SNS_TOPIC_ALERTS: str = f"{MODULE_NAME}-alerts"
    SNS_TOPIC_NOTIFICATIONS: str = f"{MODULE_NAME}-notifications"
    SNS_TOPIC_WARNINGS: str = f"{MODULE_NAME}-warnings"
    
    # CloudWatch
    CLOUDWATCH_LOG_GROUP: str = f"/aws/lambda/{MODULE_NAME}"
    CLOUDWATCH_METRIC_NAMESPACE: str = f"CORETHREE3/{MODULE_NAME}"
    
    # Kinesis
    KINESIS_STREAM_SENSOR_DATA: str = f"{MODULE_NAME}-sensor-data-stream"
    KINESIS_STREAM_ALERTS: str = f"{MODULE_NAME}-alerts-stream"
    
    # SageMaker
    SAGEMAKER_ROLE: str = os.getenv("SAGEMAKER_ROLE", f"corethree3-{MODULE_NAME}-sagemaker-role")
    SAGEMAKER_BUCKET: str = os.getenv("SAGEMAKER_BUCKET", S3_BUCKET_NAME)
    SAGEMAKER_NOTEBOOK_INSTANCE: str = f"corethree3-{MODULE_NAME}-notebook"
    
    # IAM
    IAM_ROLE_LAMBDA: str = f"{MODULE_NAME}-lambda-role"
    IAM_ROLE_IOT: str = f"{MODULE_NAME}-iot-role"
    IAM_ROLE_SAGEMAKER: str = f"{MODULE_NAME}-sagemaker-role"
    
    # KMS
    KMS_KEY_ID: str = os.getenv("KMS_KEY_ID", "alias/corethree3-key")
    
    # Configuracoes de seguranca
    ENABLE_ENCRYPTION: bool = True
    ENABLE_CLOUDTRAIL: bool = True
    ENABLE_IOT_AUTH: bool = True
    
    @classmethod
    def get_resource_name(cls, resource_type: str, suffix: str = "") -> str:
        """Gerar nome de recurso padronizado"""
        env = os.getenv("ENVIRONMENT", "dev")
        name = f"corethree3-{cls.MODULE_NAME}-{resource_type}"
        if suffix:
            name = f"{name}-{suffix}"
        if env != "production":
            name = f"{name}-{env}"
        return name


# Instancia das configuracoes
aws_config = AWSConfig()
