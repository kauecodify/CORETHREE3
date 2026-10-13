"""
CORETHREE3 - DNA de Maquinas
Variaveis do Terraform

Este arquivo define as variaveis de configuracao para o Terraform.
"""

# ==================== Variaveis Principais ====================

variable "aws_region" {
  description = "Regiao AWS onde os recursos serao criados"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente de implantacao (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Ambiente deve ser um de: dev, staging, prod"
  }
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "corethree3-dna-maquina"
}

# ==================== VPC ====================

variable "vpc_cidr" {
  description = "CIDR da VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "CIDRs das subnets privadas"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "CIDRs das subnets publicas"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# ==================== IoT ====================

variable "iot_thing_type" {
  description = "Tipo da Thing IoT"
  type        = string
  default     = "DNAMaquina-Device"
}

variable "iot_thing_name_prefix" {
  description = "Prefixo do nome da Thing IoT"
  type        = string
  default     = "dna-maquina-"
}

# ==================== Timestream ====================

variable "timestream_database_name" {
  description = "Nome do banco de dados Timestream"
  type        = string
  default     = "corethree3-dna-maquina-timestream"
}

variable "timestream_retention_hours" {
  description = "Horas de retencao no Memory Store"
  type        = number
  default     = 8760  # 1 ano
}

variable "timestream_retention_days" {
  description = "Dias de retencao no Magnetic Store"
  type        = number
  default     = 730  # 2 anos
}

# ==================== DynamoDB ====================

variable "dynamodb_billing_mode" {
  description = "Modo de cobranca do DynamoDB"
  type        = string
  default     = "PAY_PER_REQUEST"
}

# ==================== Lambda ====================

variable "lambda_runtime" {
  description = "Runtime das funcoes Lambda"
  type        = string
  default     = "python3.9"
}

variable "lambda_timeout" {
  description = "Timeout padrao das funcoes Lambda em segundos"
  type        = number
  default     = 60
}

variable "lambda_memory_size" {
  description = "Tamanho de memoria padrao das funcoes Lambda em MB"
  type        = number
  default     = 256
}

# ==================== API Gateway ====================

variable "api_gateway_protocol_type" {
  description = "Tipo de protocolo do API Gateway"
  type        = string
  default     = "HTTP"
}

variable "api_gateway_stage_name" {
  description = "Nome do stage do API Gateway"
  type        = string
  default     = "v1"
}

# ==================== CloudWatch ====================

variable "cloudwatch_log_retention" {
  description = "Dias de retencao dos logs do CloudWatch"
  type        = number
  default     = 30
}

# ==================== EventBridge ====================

variable "eventbridge_schedule_rate" {
  description = "Frequencia padrao das regras do EventBridge"
  type        = string
  default     = "rate(5 minutes)"
}

# ==================== SNS ====================

variable "sns_topic_names" {
  description = "Nomes dos topicos SNS"
  type = object({
    critical_alerts = string
    high_alerts    = string
    medium_alerts  = string
    low_alerts     = string
  })
  default = {
    critical_alerts = "corethree3-dna-maquina-critical-alerts"
    high_alerts    = "corethree3-dna-maquina-high-alerts"
    medium_alerts  = "corethree3-dna-maquina-medium-alerts"
    low_alerts     = "corethree3-dna-maquina-low-alerts"
  }
}

# ==================== Tags ====================

variable "default_tags" {
  description = "Tags padrao para todos os recursos"
  type        = map(string)
  default = {
    Project     = "CORETHREE3"
    Module      = "DNA de Maquinas"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}
