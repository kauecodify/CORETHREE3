"""
CORETHREE3 - Gestao de Vendas Avancada
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
    MODULE_NAME: str = "gestao-vendas"
    
    # S3
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", f"corethree3-{MODULE_NAME}-{ACCOUNT_ID}")
    S3_PREFIX: str = "gestao-vendas"
    S3_DATA_PREFIX: str = f"{S3_PREFIX}/data"
    S3_MODELS_PREFIX: str = f"{S3_PREFIX}/models"
    S3_EXPORTS_PREFIX: str = f"{S3_PREFIX}/exports"
    S3_LOGS_PREFIX: str = f"{S3_PREFIX}/logs"
    
    # Redshift
    REDSHIFT_CLUSTER_NAME: str = os.getenv("REDSHIFT_CLUSTER_NAME", f"corethree3-{MODULE_NAME}")
    REDSHIFT_DATABASE: str = os.getenv("REDSHIFT_DATABASE", "gestao_vendas")
    REDSHIFT_USER: str = os.getenv("REDSHIFT_USER", "admin")
    REDSHIFT_SCHEMA: str = "public"
    
    # SageMaker
    SAGEMAKER_ROLE: str = os.getenv("SAGEMAKER_ROLE", f"corethree3-{MODULE_NAME}-sagemaker-role")
    SAGEMAKER_BUCKET: str = os.getenv("SAGEMAKER_BUCKET", S3_BUCKET_NAME)
    SAGEMAKER_NOTEBOOK_INSTANCE: str = f"corethree3-{MODULE_NAME}-notebook"
    
    # DynamoDB
    DYNAMODB_TABLE_SALES: str = f"{MODULE_NAME}-sales"
    DYNAMODB_TABLE_PRODUCTS: str = f"{MODULE_NAME}-products"
    DYNAMODB_TABLE_CUSTOMERS: str = f"{MODULE_NAME}-customers"
    DYNAMODB_TABLE_STOCK: str = f"{MODULE_NAME}-stock"
    DYNAMODB_TABLE_FORECASTS: str = f"{MODULE_NAME}-forecasts"
    
    # Lambda
    LAMBDA_FUNCTION_FORECAST: str = f"{MODULE_NAME}-forecast"
    LAMBDA_FUNCTION_ANALYSIS: str = f"{MODULE_NAME}-analysis"
    LAMBDA_FUNCTION_EXPORT: str = f"{MODULE_NAME}-export"
    LAMBDA_LAYER_NAME: str = f"{MODULE_NAME}-layer"
    
    # API Gateway
    API_GATEWAY_NAME: str = f"{MODULE_NAME}-api"
    API_GATEWAY_STAGE: str = os.getenv("ENVIRONMENT", "dev")
    
    # Step Functions
    STATE_MACHINE_FORECAST: str = f"{MODULE_NAME}-forecast-state-machine"
    STATE_MACHINE_ANALYSIS: str = f"{MODULE_NAME}-analysis-state-machine"
    
    # EventBridge
    EVENT_BUS_NAME: str = f"{MODULE_NAME}-bus"
    
    # SNS
    SNS_TOPIC_ALERTS: str = f"{MODULE_NAME}-alerts"
    SNS_TOPIC_NOTIFICATIONS: str = f"{MODULE_NAME}-notifications"
    
    # CloudWatch
    CLOUDWATCH_LOG_GROUP: str = f"/aws/lambda/{MODULE_NAME}"
    CLOUDWATCH_METRIC_NAMESPACE: str = f"CORETHREE3/{MODULE_NAME}"
    
    # Kinesis
    KINESIS_STREAM_SALES: str = f"{MODULE_NAME}-sales-stream"
    KINESIS_STREAM_STOCK: str = f"{MODULE_NAME}-stock-stream"
    
    # Glue
    GLUE_JOB_ETL: str = f"{MODULE_NAME}-etl-job"
    GLUE_CRAWLER_SALES: str = f"{MODULE_NAME}-sales-crawler"
    
    # IAM
    IAM_ROLE_LAMBDA: str = f"{MODULE_NAME}-lambda-role"
    IAM_ROLE_SAGEMAKER: str = f"{MODULE_NAME}-sagemaker-role"
    IAM_ROLE_GLUE: str = f"{MODULE_NAME}-glue-role"
    
    # KMS
    KMS_KEY_ID: str = os.getenv("KMS_KEY_ID", "alias/corethree3-key")
    
    # Configuracoes de seguranca
    ENABLE_ENCRYPTION: bool = True
    ENABLE_CLOUDTRAIL: bool = True
    
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
