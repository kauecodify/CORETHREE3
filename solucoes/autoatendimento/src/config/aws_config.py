"""
CORETHREE3 - Autoatendimento Inteligente
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
    LEX_BOT_NAME: str = f"corethree3-autoatendimento-{os.getenv('ENVIRONMENT', 'dev')}"
    LEX_BOT_ALIAS: str = "prod" if os.getenv("ENVIRONMENT") == "production" else "dev"
    
    # S3
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", f"corethree3-{MODULE_NAME}-{ACCOUNT_ID}")
    S3_PREFIX: str = "autoatendimento"
    S3_LOG_PREFIX: str = f"{S3_PREFIX}/logs"
    S3_DATA_PREFIX: str = f"{S3_PREFIX}/data"
    
    # DynamoDB
    DYNAMODB_TABLE_SESSIONS: str = f"{LEX_BOT_NAME}-sessions"
    DYNAMODB_TABLE_CONVERSATIONS: str = f"{LEX_BOT_NAME}-conversations"
    DYNAMODB_TABLE_KNOWLEDGE: str = f"{LEX_BOT_NAME}-knowledge"
    DYNAMODB_TABLE_USERS: str = f"{LEX_BOT_NAME}-users"
    
    # Lambda
    LAMBDA_FUNCTION_PROCESS: str = f"{LEX_BOT_NAME}-process"
    LAMBDA_FUNCTION_HANDLER: str = f"{LEX_BOT_NAME}-handler"
    LAMBDA_FUNCTION_NLP: str = f"{LEX_BOT_NAME}-nlp"
    LAMBDA_LAYER_NAME: str = f"{LEX_BOT_NAME}-layer"
    
    # API Gateway
    API_GATEWAY_NAME: str = f"{LEX_BOT_NAME}-api"
    API_GATEWAY_STAGE: str = os.getenv("ENVIRONMENT", "dev")
    
    # CloudWatch
    CLOUDWATCH_LOG_GROUP: str = f"/aws/lambda/{LEX_BOT_NAME}"
    CLOUDWATCH_METRIC_NAMESPACE: str = f"CORETHREE3/{LEX_BOT_NAME}"
    
    # SNS
    SNS_TOPIC_ALERTS: str = f"{LEX_BOT_NAME}-alerts"
    SNS_TOPIC_NOTIFICATIONS: str = f"{LEX_BOT_NAME}-notifications"
    
    # EventBridge
    EVENT_BUS_NAME: str = f"{LEX_BOT_NAME}-bus"
    
    # Step Functions
    STATE_MACHINE_NAME: str = f"{LEX_BOT_NAME}-state-machine"
    
    # IAM
    IAM_ROLE_LAMBDA: str = f"{LEX_BOT_NAME}-lambda-role"
    IAM_ROLE_LEX: str = f"{LEX_BOT_NAME}-lex-role"
    IAM_ROLE_BEDROCK: str = f"{LEX_BOT_NAME}-bedrock-role"
    
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


# Modulo
MODULE_NAME = "autoatendimento"

# Instancia das configuracoes
aws_config = AWSConfig()
