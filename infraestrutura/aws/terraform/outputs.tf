# CORETHREE3 - Outputs do Terraform

# Outputs de API Gateway
output "api_gateway_endpoint" {
  description = "Endpoint do API Gateway"
  value       = module.api_gateway.api_endpoint
}

output "api_gateway_id" {
  description = "ID do API Gateway"
  value       = module.api_gateway.api_id
}

output "api_gateway_stage_name" {
  description = "Nome do stage do API Gateway"
  value       = var.api_gateway_stage_name
}

# Outputs de Cognito
output "cognito_user_pool_id" {
  description = "ID do User Pool do Cognito"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "ARN do User Pool do Cognito"
  value       = module.cognito.user_pool_arn
}

output "cognito_user_pool_client_id" {
  description = "ID do Client do User Pool do Cognito"
  value       = module.cognito.user_pool_client_id
}

output "cognito_user_pool_client_secret" {
  description = "Secret do Client do User Pool do Cognito"
  value       = module.cognito.user_pool_client_secret
  sensitive   = true
}

output "cognito_identity_pool_id" {
  description = "ID do Identity Pool do Cognito"
  value       = module.cognito.identity_pool_id
}

# Outputs de S3
output "s3_data_bucket_id" {
  description = "ID do bucket de dados"
  value       = module.s3.buckets["data_bucket"].id
}

output "s3_data_bucket_arn" {
  description = "ARN do bucket de dados"
  value       = module.s3.buckets["data_bucket"].arn
}

output "s3_models_bucket_id" {
  description = "ID do bucket de modelos"
  value       = module.s3.buckets["models_bucket"].id
}

output "s3_models_bucket_arn" {
  description = "ARN do bucket de modelos"
  value       = module.s3.buckets["models_bucket"].arn
}

output "s3_logs_bucket_id" {
  description = "ID do bucket de logs"
  value       = module.s3.buckets["logs_bucket"].id
}

output "s3_logs_bucket_arn" {
  description = "ARN do bucket de logs"
  value       = module.s3.buckets["logs_bucket"].arn
}

# Outputs de IoT Core
output "iot_endpoint" {
  description = "Endpoint do IoT Core"
  value       = module.iot_core.iot_endpoint
}

output "iot_policy_arn" {
  description = "ARN da politica IoT"
  value       = module.iot_core.iot_policy_arn
}

output "iot_role_arn" {
  description = "ARN da role IoT"
  value       = module.iot_core.iot_role_arn
}

# Outputs de Timestream
output "timestream_database_name" {
  description = "Nome do banco de dados Timestream"
  value       = module.timestream.database_name
}

output "timestream_database_arn" {
  description = "ARN do banco de dados Timestream"
  value       = module.timestream.database_arn
}

output "timestream_table_names" {
  description = "Nomes das tabelas Timestream"
  value       = module.timestream.table_names
}

# Outputs de Lambda
output "lambda_sensor_processor_arn" {
  description = "ARN da funcao Lambda de processamento de sensores"
  value       = module.lambda_processing["sensor_processor"].arn
}

output "lambda_sensor_processor_name" {
  description = "Nome da funcao Lambda de processamento de sensores"
  value       = module.lambda_processing["sensor_processor"].function_name
}

output "lambda_anomaly_detector_arn" {
  description = "ARN da funcao Lambda de deteccao de anomalias"
  value       = module.lambda_processing["anomaly_detector"].arn
}

output "lambda_anomaly_detector_name" {
  description = "Nome da funcao Lambda de deteccao de anomalias"
  value       = module.lambda_processing["anomaly_detector"].function_name
}

output "lambda_prediction_model_arn" {
  description = "ARN da funcao Lambda de predicao"
  value       = module.lambda_processing["prediction_model"].arn
}

output "lambda_prediction_model_name" {
  description = "Nome da funcao Lambda de predicao"
  value       = module.lambda_processing["prediction_model"].function_name
}

# Outputs de SageMaker
output "sagemaker_endpoint_name" {
  description = "Nome do endpoint SageMaker"
  value       = module.sagemaker.endpoint_name
}

output "sagemaker_endpoint_arn" {
  description = "ARN do endpoint SageMaker"
  value       = module.sagemaker.endpoint_arn
}

output "sagemaker_model_name" {
  description = "Nome do modelo SageMaker"
  value       = module.sagemaker.model_name
}

output "sagemaker_model_arn" {
  description = "ARN do modelo SageMaker"
  value       = module.sagemaker.model_arn
}

output "sagemaker_execution_role_arn" {
  description = "ARN da role de execucao do SageMaker"
  value       = aws_iam_role.sagemaker_execution.arn
}

# Outputs de DynamoDB
output "dynamodb_machines_table_name" {
  description = "Nome da tabela DynamoDB de maquinas"
  value       = module.dynamodb.tables["machines_table"].name
}

output "dynamodb_machines_table_arn" {
  description = "ARN da tabela DynamoDB de maquinas"
  value       = module.dynamodb.tables["machines_table"].arn
}

output "dynamodb_sensors_table_name" {
  description = "Nome da tabela DynamoDB de sensores"
  value       = module.dynamodb.tables["sensors_table"].name
}

output "dynamodb_sensors_table_arn" {
  description = "ARN da tabela DynamoDB de sensores"
  value       = module.dynamodb.tables["sensors_table"].arn
}

output "dynamodb_alerts_table_name" {
  description = "Nome da tabela DynamoDB de alertas"
  value       = module.dynamodb.tables["alerts_table"].name
}

output "dynamodb_alerts_table_arn" {
  description = "ARN da tabela DynamoDB de alertas"
  value       = module.dynamodb.tables["alerts_table"].arn
}

# Outputs de SNS
output "sns_alert_topic_arn" {
  description = "ARN do topico SNS de alertas"
  value       = module.sns.topics["alert_topic"].arn
}

output "sns_notification_topic_arn" {
  description = "ARN do topico SNS de notificacoes"
  value       = module.sns.topics["notification_topic"].arn
}

# Outputs de CloudWatch
output "cloudwatch_dashboard_names" {
  description = "Nomes dos dashboards CloudWatch"
  value       = module.cloudwatch.dashboard_names
}

output "cloudwatch_dashboard_urls" {
  description = "URLs dos dashboards CloudWatch"
  value       = module.cloudwatch.dashboard_urls
}

output "cloudwatch_alarm_names" {
  description = "Nomes dos alarmes CloudWatch"
  value       = module.cloudwatch.alarm_names
}

# Outputs de Kinesis
output "kinesis_sensor_data_stream_name" {
  description = "Nome do stream Kinesis de dados de sensores"
  value       = module.kinesis.streams["sensor_data_stream"].name
}

output "kinesis_sensor_data_stream_arn" {
  description = "ARN do stream Kinesis de dados de sensores"
  value       = module.kinesis.streams["sensor_data_stream"].arn
}

# Outputs de VPC (se criado)
output "vpc_id" {
  description = "ID da VPC"
  value       = var.create_vpc ? module.vpc[0].vpc_id : null
}

output "vpc_public_subnets" {
  description = "Subnets publicas da VPC"
  value       = var.create_vpc ? module.vpc[0].public_subnets : []
}

output "vpc_private_subnets" {
  description = "Subnets privadas da VPC"
  value       = var.create_vpc ? module.vpc[0].private_subnets : []
}

output "vpc_nat_gateway_id" {
  description = "ID do NAT Gateway da VPC"
  value       = var.create_vpc ? module.vpc[0].natgw_id : null
}

# Outputs de configuracao
output "environment" {
  description = "Ambiente de deploy"
  value       = var.environment
}

output "aws_region" {
  description = "Regiao AWS"
  value       = var.aws_region
}

# Outputs para frontend
output "frontend_config" {
  description = "Configuracoes para o frontend"
  value = {
    api_endpoint          = module.api_gateway.api_endpoint
    user_pool_id          = module.cognito.user_pool_id
    user_pool_client_id   = module.cognito.user_pool_client_id
    region                = var.aws_region
    data_bucket_name      = module.s3.buckets["data_bucket"].id
    models_bucket_name    = module.s3.buckets["models_bucket"].id
  }
  sensitive = false
}

# Outputs para backend
output "backend_config" {
  description = "Configuracoes para o backend"
  value = {
    api_endpoint          = module.api_gateway.api_endpoint
    user_pool_id          = module.cognito.user_pool_id
    user_pool_client_id   = module.cognito.user_pool_client_id
    region                = var.aws_region
    data_bucket_name      = module.s3.buckets["data_bucket"].id
    models_bucket_name    = module.s3.buckets["models_bucket"].id
    logs_bucket_name      = module.s3.buckets["logs_bucket"].id
    iot_endpoint          = module.iot_core.iot_endpoint
    timestream_database   = module.timestream.database_name
    dynamodb_machines     = module.dynamodb.tables["machines_table"].name
    dynamodb_sensors      = module.dynamodb.tables["sensors_table"].name
    dynamodb_alerts       = module.dynamodb.tables["alerts_table"].name
    sagemaker_endpoint    = module.sagemaker.endpoint_name
    kinesis_stream        = module.kinesis.streams["sensor_data_stream"].name
    sns_alert_topic       = module.sns.topics["alert_topic"].arn
    sns_notification_topic = module.sns.topics["notification_topic"].arn
  }
  sensitive = false
}

# Outputs para CI/CD
output "cicd_config" {
  description = "Configuracoes para CI/CD"
  value = {
    terraform_state_bucket = "corethree3-terraform-state"
    terraform_lock_table   = "corethree3-terraform-lock"
    region                 = var.aws_region
  }
  sensitive = false
}
