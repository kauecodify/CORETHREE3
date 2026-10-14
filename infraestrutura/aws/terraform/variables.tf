# CORETHREE3 - Variaveis do Terraform

# Configuracoes gerais
variable "aws_region" {
  description = "Regiao AWS onde a infraestrutura sera deployada"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente de deploy (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# Configuracoes de VPC (opcional)
variable "create_vpc" {
  description = "Criar VPC para recursos que necessitam"
  type        = bool
  default     = false
}

variable "vpc_cidr" {
  description = "CIDR block para a VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Configuracoes de IoT
variable "iot_enabled" {
  description = "Habilitar modulo IoT"
  type        = bool
  default     = true
}

# Configuracoes de Timestream
variable "timestream_enabled" {
  description = "Habilitar modulo Timestream"
  type        = bool
  default     = true
}

variable "timestream_retention_days" {
  description = "Periodo de retencao de dados no Timestream"
  type        = number
  default     = 365
}

# Configuracoes de Lambda
variable "lambda_memory_size" {
  description = "Tamanho de memoria padrao para funcoes Lambda"
  type        = number
  default     = 256
}

variable "lambda_timeout" {
  description = "Timeout padrao para funcoes Lambda"
  type        = number
  default     = 30
}

# Configuracoes de SageMaker
variable "sagemaker_enabled" {
  description = "Habilitar modulo SageMaker"
  type        = bool
  default     = true
}

variable "sagemaker_instance_type" {
  description = "Tipo de instancia para endpoint SageMaker"
  type        = string
  default     = "ml.m5.large"
}

variable "sagemaker_initial_instance_count" {
  description = "Numero inicial de instancias para endpoint SageMaker"
  type        = number
  default     = 1
}

# Configuracoes de API Gateway
variable "api_gateway_enabled" {
  description = "Habilitar API Gateway"
  type        = bool
  default     = true
}

variable "api_gateway_stage_name" {
  description = "Nome do stage do API Gateway"
  type        = string
  default     = "prod"
}

# Configuracoes de S3
variable "s3_versioning_enabled" {
  description = "Habilitar versionamento nos buckets S3"
  type        = bool
  default     = true
}

variable "s3_encryption_enabled" {
  description = "Habilitar criptografia nos buckets S3"
  type        = bool
  default     = true
}

# Configuracoes de DynamoDB
variable "dynamodb_billing_mode" {
  description = "Modo de cobranca do DynamoDB"
  type        = string
  default     = "PAY_PER_REQUEST"
}

# Configuracoes de CloudWatch
variable "cloudwatch_alarms_enabled" {
  description = "Habilitar alarmes do CloudWatch"
  type        = bool
  default     = true
}

variable "cloudwatch_dashboards_enabled" {
  description = "Habilitar dashboards do CloudWatch"
  type        = bool
  default     = true
}

# Configuracoes de Cognito
variable "cognito_enabled" {
  description = "Habilitar Cognito para autenticacao"
  type        = bool
  default     = true
}

variable "cognito_callback_urls" {
  description = "URLs de callback para Cognito"
  type        = list(string)
  default     = [
    "https://app.corethree3.com/callback",
    "https://localhost:3000/callback"
  ]
}

variable "cognito_logout_urls" {
  description = "URLs de logout para Cognito"
  type        = list(string)
  default     = [
    "https://app.corethree3.com/logout",
    "https://localhost:3000/logout"
  ]
}

# Configuracoes de SNS
variable "sns_enabled" {
  description = "Habilitar SNS para notificacoes"
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email para alertas"
  type        = string
  default     = "alerts@corethree3.com"
}

variable "alert_phone" {
  description = "Telefone para alertas"
  type        = string
  default     = "+5511999999999"
}

# Configuracoes de Kinesis
variable "kinesis_enabled" {
  description = "Habilitar Kinesis para streaming"
  type        = bool
  default     = true
}

variable "kinesis_shard_count" {
  description = "Numero de shards para stream Kinesis"
  type        = number
  default     = 3
}

variable "kinesis_retention_period" {
  description = "Periodo de retencao do stream Kinesis"
  type        = number
  default     = 24
}

# Configuracoes de tags globais
variable "global_tags" {
  description = "Tags globais para todos os recursos"
  type        = map(string)
  default     = {
    Project     = "CORETHREE3"
    ManagedBy   = "terraform"
    Environment = "prod"
  }
}
