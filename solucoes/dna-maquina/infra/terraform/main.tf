"""
CORETHREE3 - DNA de Maquinas
Configuracao Terraform Principal

Este arquivo define a infraestrutura principal do sistema DNA de Maquinas usando Terraform.
"""

# Configuracao do Terraform
tf {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Configuracao do provedor AWS
provider "aws" {
  region = var.aws_region
  
  # Credenciais (serao fornecidas via variaveis de ambiente ou secrets)
  # access_key = var.aws_access_key
  # secret_key = var.aws_secret_key
}

# ==================== Variaveis ====================

variable "aws_region" {
  description = "Regiao AWS"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "corethree3-dna-maquina"
}

# ==================== Tags ====================

locals {
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ==================== VPC e Rede ====================

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"
  
  name = "${var.project_name}-${var.environment}-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway   = true
  enable_vpn_gateway   = false
  single_nat_gateway   = true
  one_nat_gateway_per_az = false
  
  tags = local.tags
}

# ==================== Seguranca ====================

# Security Groups
resource "aws_security_group" "iot_core" {
  name        = "${var.project_name}-${var.environment}-iot-core"
  description = "Security Group para AWS IoT Core"
  vpc_id      = module.vpc.vpc_id
  
  # Regra de saida padrao
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.tags, {
    Name = "${var.project_name}-${var.environment}-iot-core"
  })
}

resource "aws_security_group" "ec2_instances" {
  name        = "${var.project_name}-${var.environment}-ec2"
  description = "Security Group para instancias EC2"
  vpc_id      = module.vpc.vpc_id
  
  # SSH (apenas para IP especifico em producao)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.environment == "prod" ? ["192.168.1.0/24"] : ["0.0.0.0/0"]
  }
  
  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # MQTT (para IoT)
  ingress {
    from_port   = 8883
    to_port     = 8883
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Regra de saida padrao
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.tags, {
    Name = "${var.project_name}-${var.environment}-ec2"
  })
}

# IAM Roles
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-${var.environment}-ec2-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "ec2_role_ssm" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ec2_role_s3" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "ec2_role_cloudwatch" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# ==================== IoT Core ====================

resource "aws_iot_thing_type" "dna_maquina" {
  name = "DNAMaquina-Device"
  
  tags = local.tags
}

resource "aws_iot_policy" "dna_maquina_device_policy" {
  name = "DNAMaquina-Device-Policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Publish",
          "iot:Receive"
        ]
        Resource = [
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topic/corethree3/dna-maquina/*",
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topic/$aws/things/*/shadow/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Subscribe"
        ]
        Resource = [
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topicfilter/corethree3/dna-maquina/*"
        ]
      }
    ]
  })
  
  tags = local.tags
}

# ==================== Bancos de Dados ====================

# DynamoDB
resource "aws_dynamodb_table" "devices" {
  name           = "${var.project_name}-${var.environment}-devices"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "machine_id"
    type = "S"
  }
  
  global_secondary_index {
    name            = "MachineIndex"
    hash_key       = "machine_id"
    projection_type = "ALL"
  }
  
  tags = local.tags
}

resource "aws_dynamodb_table" "sensors" {
  name           = "${var.project_name}-${var.environment}-sensors"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "device_id"
    type = "S"
  }
  
  attribute {
    name = "machine_id"
    type = "S"
  }
  
  global_secondary_index {
    name            = "DeviceIndex"
    hash_key       = "device_id"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "MachineIndex"
    hash_key       = "machine_id"
    projection_type = "ALL"
  }
  
  tags = local.tags
}

resource "aws_dynamodb_table" "alerts" {
  name           = "${var.project_name}-${var.environment}-alerts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "machine_id"
    type = "S"
  }
  
  attribute {
    name = "device_id"
    type = "S"
  }
  
  attribute {
    name = "severity"
    type = "S"
  }
  
  attribute {
    name = "status"
    type = "S"
  }
  
  global_secondary_index {
    name            = "MachineIndex"
    hash_key       = "machine_id"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "DeviceIndex"
    hash_key       = "device_id"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "SeverityStatusIndex"
    hash_key       = "severity"
    range_key      = "status"
    projection_type = "ALL"
  }
  
  tags = local.tags
}

resource "aws_dynamodb_table" "predictions" {
  name           = "${var.project_name}-${var.environment}-predictions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "machine_id"
    type = "S"
  }
  
  attribute {
    name = "prediction_type"
    type = "S"
  }
  
  global_secondary_index {
    name            = "MachineIndex"
    hash_key       = "machine_id"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "TypeIndex"
    hash_key       = "prediction_type"
    projection_type = "ALL"
  }
  
  tags = local.tags
}

resource "aws_dynamodb_table" "maintenance" {
  name           = "${var.project_name}-${var.environment}-maintenance"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "machine_id"
    type = "S"
  }
  
  attribute {
    name = "status"
    type = "S"
  }
  
  global_secondary_index {
    name            = "MachineIndex"
    hash_key       = "machine_id"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "StatusIndex"
    hash_key       = "status"
    projection_type = "ALL"
  }
  
  tags = local.tags
}

# Timestream
resource "aws_timestreamwrite_database" "dna_maquina" {
  database_name = "${var.project_name}-${var.environment}-timestream"
  
  tags = local.tags
}

resource "aws_timestreamwrite_table" "vibration" {
  database_name = aws_timestreamwrite_database.dna_maquina.database_name
  table_name   = "vibration"
  
  retention_properties {
    memory_store_retention_period_in_hours = 24 * 365  # 1 ano
    magnetic_store_retention_period_in_days = 365 * 2   # 2 anos
  }
  
  tags = local.tags
}

resource "aws_timestreamwrite_table" "temperature" {
  database_name = aws_timestreamwrite_database.dna_maquina.database_name
  table_name   = "temperature"
  
  retention_properties {
    memory_store_retention_period_in_hours = 24 * 365
    magnetic_store_retention_period_in_days = 365 * 2
  }
  
  tags = local.tags
}

resource "aws_timestreamwrite_table" "pressure" {
  database_name = aws_timestreamwrite_database.dna_maquina.database_name
  table_name   = "pressure"
  
  retention_properties {
    memory_store_retention_period_in_hours = 24 * 365
    magnetic_store_retention_period_in_days = 365 * 2
  }
  
  tags = local.tags
}

resource "aws_timestreamwrite_table" "current" {
  database_name = aws_timestreamwrite_database.dna_maquina.database_name
  table_name   = "current"
  
  retention_properties {
    memory_store_retention_period_in_hours = 24 * 365
    magnetic_store_retention_period_in_days = 365 * 2
  }
  
  tags = local.tags
}

resource "aws_timestreamwrite_table" "voltage" {
  database_name = aws_timestreamwrite_database.dna_maquina.database_name
  table_name   = "voltage"
  
  retention_properties {
    memory_store_retention_period_in_hours = 24 * 365
    magnetic_store_retention_period_in_days = 365 * 2
  }
  
  tags = local.tags
}

# ==================== S3 ====================

resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-${var.environment}-data-lake"
  
  versioning {
    enabled = true
  }
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  
  tags = local.tags
}

resource "aws_s3_bucket" "firmware" {
  bucket = "${var.project_name}-${var.environment}-firmware"
  
  versioning {
    enabled = true
  }
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  
  tags = local.tags
}

resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_name}-${var.environment}-logs"
  
  lifecycle_rule {
    id      = "log-retention"
    enabled = true
    
    expiration {
      days = 90
    }
  }
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  
  tags = local.tags
}

# ==================== Lambda ====================

resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-${var.environment}-lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.tags
}

resource "aws_iam_role_policy" "lambda_basic_execution" {
  name = "${var.project_name}-${var.environment}-lambda-basic-execution"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_iot_access" {
  name = "${var.project_name}-${var.environment}-lambda-iot-access"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Describe*",
          "iot:List*",
          "iot:Get*",
          "iot:Update*",
          "iot:Publish",
          "iot:Subscribe"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_dynamodb_access" {
  name = "${var.project_name}-${var.environment}-lambda-dynamodb-access"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.devices.arn,
          aws_dynamodb_table.sensors.arn,
          aws_dynamodb_table.alerts.arn,
          aws_dynamodb_table.predictions.arn,
          aws_dynamodb_table.maintenance.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_timestream_access" {
  name = "${var.project_name}-${var.environment}-lambda-timestream-access"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "timestream:WriteRecords",
          "timestream:Select",
          "timestream:Describe*"
        ]
        Resource = [
          aws_timestreamwrite_database.dna_maquina.arn,
          "${aws_timestreamwrite_database.dna_maquina.arn}/table/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_sagemaker_access" {
  name = "${var.project_name}-${var.environment}-lambda-sagemaker-access"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sagemaker:InvokeEndpoint",
          "sagemaker:Describe*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Funcoes Lambda
resource "aws_lambda_function" "process_readings" {
  function_name = "${var.project_name}-${var.environment}-process-readings"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"
  timeout       = 60
  memory_size   = 256
  
  s3_bucket = aws_s3_bucket.data_lake.bucket
  s3_key    = "lambda/code/process_readings.zip"
  
  environment {
    variables = {
      ENVIRONMENT     = var.environment
      PROJECT_NAME    = var.project_name
      IOT_ENDPOINT    = data.aws_iot_endpoint.current.endpoint_address
      TIMESTREAM_DB   = aws_timestreamwrite_database.dna_maquina.database_name
    }
  }
  
  tags = local.tags
}

resource "aws_lambda_function" "detect_anomalies" {
  function_name = "${var.project_name}-${var.environment}-detect-anomalies"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"
  timeout       = 120
  memory_size   = 512
  
  s3_bucket = aws_s3_bucket.data_lake.bucket
  s3_key    = "lambda/code/detect_anomalies.zip"
  
  environment {
    variables = {
      ENVIRONMENT           = var.environment
      PROJECT_NAME          = var.project_name
      SAGEMAKER_ENDPOINT    = "${var.project_name}-${var.environment}-anomaly-detection"
    }
  }
  
  tags = local.tags
}

resource "aws_lambda_function" "predict_failures" {
  function_name = "${var.project_name}-${var.environment}-predict-failures"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"
  timeout       = 120
  memory_size   = 512
  
  s3_bucket = aws_s3_bucket.data_lake.bucket
  s3_key    = "lambda/code/predict_failures.zip"
  
  environment {
    variables = {
      ENVIRONMENT           = var.environment
      PROJECT_NAME          = var.project_name
      SAGEMAKER_ENDPOINT    = "${var.project_name}-${var.environment}-failure-prediction"
    }
  }
  
  tags = local.tags
}

resource "aws_lambda_function" "schedule_maintenance" {
  function_name = "${var.project_name}-${var.environment}-schedule-maintenance"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"
  timeout       = 60
  memory_size   = 256
  
  s3_bucket = aws_s3_bucket.data_lake.bucket
  s3_key    = "lambda/code/schedule_maintenance.zip"
  
  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT_NAME = var.project_name
    }
  }
  
  tags = local.tags
}

# ==================== API Gateway ====================

resource "aws_apigatewayv2_api" "dna_maquina" {
  name          = "${var.project_name}-${var.environment}-api"
  protocol_type = "HTTP"
  
  tags = local.tags
}

resource "aws_apigatewayv2_stage" "dna_maquina" {
  api_id      = aws_apigatewayv2_api.dna_maquina.id
  name        = var.environment
  auto_deploy = true
  
  default_route_settings {
    throttling_burst_limit = 100
    throttling_rate_limit  = 50
  }
  
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format          = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller        = "$context.identity.caller"
      user          = "$context.identity.user"
      requestTime   = "$context.requestTime"
      httpMethod    = "$context.httpMethod"
      resourcePath  = "$context.resourcePath"
      status       = "$context.status"
      protocol      = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
  
  tags = local.tags
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.project_name}-${var.environment}"
  retention_in_days = 30
  
  tags = local.tags
}

# ==================== EventBridge ====================

resource "aws_cloudwatch_event_rule" "process_readings_schedule" {
  name                = "${var.project_name}-${var.environment}-process-readings-schedule"
  description         = "Agenda processamento de leituras"
  schedule_expression = "rate(5 minutes)"
  
  tags = local.tags
}

resource "aws_cloudwatch_event_target" "process_readings_target" {
  rule      = aws_cloudwatch_event_rule.process_readings_schedule.name
  target_id = "ProcessReadings"
  arn       = aws_lambda_function.process_readings.arn
}

resource "aws_lambda_permission" "process_readings_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_readings.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.process_readings_schedule.arn
}

resource "aws_cloudwatch_event_rule" "detect_anomalies_schedule" {
  name                = "${var.project_name}-${var.environment}-detect-anomalies-schedule"
  description         = "Agenda deteccao de anomalias"
  schedule_expression = "rate(15 minutes)"
  
  tags = local.tags
}

resource "aws_cloudwatch_event_target" "detect_anomalies_target" {
  rule      = aws_cloudwatch_event_rule.detect_anomalies_schedule.name
  target_id = "DetectAnomalies"
  arn       = aws_lambda_function.detect_anomalies.arn
}

resource "aws_lambda_permission" "detect_anomalies_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.detect_anomalies.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.detect_anomalies_schedule.arn
}

resource "aws_cloudwatch_event_rule" "predict_failures_schedule" {
  name                = "${var.project_name}-${var.environment}-predict-failures-schedule"
  description         = "Agenda predicao de falhas"
  schedule_expression = "rate(1 hour)"
  
  tags = local.tags
}

resource "aws_cloudwatch_event_target" "predict_failures_target" {
  rule      = aws_cloudwatch_event_rule.predict_failures_schedule.name
  target_id = "PredictFailures"
  arn       = aws_lambda_function.predict_failures.arn
}

resource "aws_lambda_permission" "predict_failures_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.predict_failures.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.predict_failures_schedule.arn
}

# ==================== SNS ====================

resource "aws_sns_topic" "critical_alerts" {
  name = "${var.project_name}-${var.environment}-critical-alerts"
  
  tags = local.tags
}

resource "aws_sns_topic" "high_alerts" {
  name = "${var.project_name}-${var.environment}-high-alerts"
  
  tags = local.tags
}

resource "aws_sns_topic" "medium_alerts" {
  name = "${var.project_name}-${var.environment}-medium-alerts"
  
  tags = local.tags
}

resource "aws_sns_topic" "low_alerts" {
  name = "${var.project_name}-${var.environment}-low-alerts"
  
  tags = local.tags
}

# ==================== CloudWatch ====================

resource "aws_cloudwatch_dashboard" "dna_maquina" {
  dashboard_name = "${var.project_name}-${var.environment}-dashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/IoT", "ConnectedDevices", "ThingType", "DNAMaquina-Device", {
              label = "Dispositivos Conectados"
            }]
          ]
          period    = 300
          stat      = "Average"
          region    = var.aws_region
          title     = "Dispositivos Conectados"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/IoT", "MessagesReceived", "ThingType", "DNAMaquina-Device", {
              label = "Mensagens Recebidas"
            }]
          ]
          period    = 300
          stat      = "Sum"
          region    = var.aws_region
          title     = "Mensagens Recebidas"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Timestream", "WriteRequests", "Database", aws_timestreamwrite_database.dna_maquina.database_name, {
              label = "Escritas no Timestream"
            }]
          ]
          period    = 300
          stat      = "Sum"
          region    = var.aws_region
          title     = "Escritas no Timestream"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", aws_dynamodb_table.alerts.name, {
              label = "Leituras de Alertas"
            }]
          ]
          period    = 300
          stat      = "Sum"
          region    = var.aws_region
          title     = "Leituras de Alertas"
        }
      }
    ]
  })
  
  tags = local.tags
}

# ==================== Dados ====================

data "aws_caller_identity" "current" {}

data "aws_iot_endpoint" "current" {
  endpoint_type = "iot:Data-ATS"
}

# ==================== Saidas ====================

output "vpc_id" {
  description = "ID da VPC"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "Subnets privadas"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "Subnets publicas"
  value       = module.vpc.public_subnets
}

output "iot_endpoint" {
  description = "Endpoint do IoT Core"
  value       = data.aws_iot_endpoint.current.endpoint_address
}

output "timestream_database" {
  description = "Nome do banco de dados Timestream"
  value       = aws_timestreamwrite_database.dna_maquina.database_name
}

output "dynamodb_tables" {
  description = "Tabelas DynamoDB"
  value = {
    devices     = aws_dynamodb_table.devices.name
    sensors     = aws_dynamodb_table.sensors.name
    alerts      = aws_dynamodb_table.alerts.name
    predictions = aws_dynamodb_table.predictions.name
    maintenance = aws_dynamodb_table.maintenance.name
  }
}

output "s3_buckets" {
  description = "Buckets S3"
  value = {
    data_lake = aws_s3_bucket.data_lake.bucket
    firmware  = aws_s3_bucket.firmware.bucket
    logs      = aws_s3_bucket.logs.bucket
  }
}

output "lambda_functions" {
  description = "Funcoes Lambda"
  value = {
    process_readings   = aws_lambda_function.process_readings.function_name
    detect_anomalies   = aws_lambda_function.detect_anomalies.function_name
    predict_failures   = aws_lambda_function.predict_failures.function_name
    schedule_maintenance = aws_lambda_function.schedule_maintenance.function_name
  }
}

output "api_gateway_endpoint" {
  description = "Endpoint do API Gateway"
  value       = aws_apigatewayv2_api.dna_maquina.api_endpoint
}

output "sns_topics" {
  description = "Topicos SNS"
  value = {
    critical_alerts = aws_sns_topic.critical_alerts.arn
    high_alerts    = aws_sns_topic.high_alerts.arn
    medium_alerts  = aws_sns_topic.medium_alerts.arn
    low_alerts     = aws_sns_topic.low_alerts.arn
  }
}
