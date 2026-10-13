"""
CORETHREE3 - DNA de Maquinas
Saidas do Terraform

Este arquivo define as saidas do Terraform para acesso aos recursos criados.
"""

# ==================== VPC ====================

output "vpc_id" {
  description = "ID da VPC criada"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "Bloco CIDR da VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnet_ids" {
  description = "IDs das subnets privadas"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "IDs das subnets publicas"
  value       = module.vpc.public_subnets
}

output "nat_gateway_ids" {
  description = "IDs dos NAT Gateways"
  value       = module.vpc.nat_gateway_ids
}

# ==================== Seguranca ====================

output "security_group_iot_core_id" {
  description = "ID do Security Group do IoT Core"
  value       = aws_security_group.iot_core.id
}

output "security_group_ec2_id" {
  description = "ID do Security Group das instancias EC2"
  value       = aws_security_group.ec2_instances.id
}

output "iam_role_ec2_arn" {
  description = "ARN da IAM Role para EC2"
  value       = aws_iam_role.ec2_role.arn
}

output "iam_role_lambda_arn" {
  description = "ARN da IAM Role para Lambda"
  value       = aws_iam_role.lambda_role.arn
}

# ==================== IoT Core ====================

output "iot_thing_type_name" {
  description = "Nome do tipo de Thing IoT"
  value       = aws_iot_thing_type.dna_maquina.name
}

output "iot_policy_name" {
  description = "Nome da politica IoT"
  value       = aws_iot_policy.dna_maquina_device_policy.name
}

output "iot_endpoint_address" {
  description = "Endereco do endpoint do IoT Core"
  value       = data.aws_iot_endpoint.current.endpoint_address
}

# ==================== Bancos de Dados ====================

output "dynamodb_table_devices_arn" {
  description = "ARN da tabela DynamoDB de dispositivos"
  value       = aws_dynamodb_table.devices.arn
}

output "dynamodb_table_devices_name" {
  description = "Nome da tabela DynamoDB de dispositivos"
  value       = aws_dynamodb_table.devices.name
}

output "dynamodb_table_sensors_arn" {
  description = "ARN da tabela DynamoDB de sensores"
  value       = aws_dynamodb_table.sensors.arn
}

output "dynamodb_table_sensors_name" {
  description = "Nome da tabela DynamoDB de sensores"
  value       = aws_dynamodb_table.sensors.name
}

output "dynamodb_table_alerts_arn" {
  description = "ARN da tabela DynamoDB de alertas"
  value       = aws_dynamodb_table.alerts.arn
}

output "dynamodb_table_alerts_name" {
  description = "Nome da tabela DynamoDB de alertas"
  value       = aws_dynamodb_table.alerts.name
}

output "dynamodb_table_predictions_arn" {
  description = "ARN da tabela DynamoDB de predicoes"
  value       = aws_dynamodb_table.predictions.arn
}

output "dynamodb_table_predictions_name" {
  description = "Nome da tabela DynamoDB de predicoes"
  value       = aws_dynamodb_table.predictions.name
}

output "dynamodb_table_maintenance_arn" {
  description = "ARN da tabela DynamoDB de manutencao"
  value       = aws_dynamodb_table.maintenance.arn
}

output "dynamodb_table_maintenance_name" {
  description = "Nome da tabela DynamoDB de manutencao"
  value       = aws_dynamodb_table.maintenance.name
}

output "timestream_database_arn" {
  description = "ARN do banco de dados Timestream"
  value       = aws_timestreamwrite_database.dna_maquina.arn
}

output "timestream_database_name" {
  description = "Nome do banco de dados Timestream"
  value       = aws_timestreamwrite_database.dna_maquina.database_name
}

output "timestream_table_names" {
  description = "Nomes das tabelas Timestream"
  value = [
    aws_timestreamwrite_table.vibration.table_name,
    aws_timestreamwrite_table.temperature.table_name,
    aws_timestreamwrite_table.pressure.table_name,
    aws_timestreamwrite_table.current.table_name,
    aws_timestreamwrite_table.voltage.table_name
  ]
}

# ==================== S3 ====================

output "s3_bucket_data_lake_arn" {
  description = "ARN do bucket S3 do Data Lake"
  value       = aws_s3_bucket.data_lake.arn
}

output "s3_bucket_data_lake_name" {
  description = "Nome do bucket S3 do Data Lake"
  value       = aws_s3_bucket.data_lake.bucket
}

output "s3_bucket_firmware_arn" {
  description = "ARN do bucket S3 de firmware"
  value       = aws_s3_bucket.firmware.arn
}

output "s3_bucket_firmware_name" {
  description = "Nome do bucket S3 de firmware"
  value       = aws_s3_bucket.firmware.bucket
}

output "s3_bucket_logs_arn" {
  description = "ARN do bucket S3 de logs"
  value       = aws_s3_bucket.logs.arn
}

output "s3_bucket_logs_name" {
  description = "Nome do bucket S3 de logs"
  value       = aws_s3_bucket.logs.bucket
}

# ==================== Lambda ====================

output "lambda_function_process_readings_arn" {
  description = "ARN da funcao Lambda de processamento de leituras"
  value       = aws_lambda_function.process_readings.arn
}

output "lambda_function_process_readings_name" {
  description = "Nome da funcao Lambda de processamento de leituras"
  value       = aws_lambda_function.process_readings.function_name
}

output "lambda_function_detect_anomalies_arn" {
  description = "ARN da funcao Lambda de deteccao de anomalias"
  value       = aws_lambda_function.detect_anomalies.arn
}

output "lambda_function_detect_anomalies_name" {
  description = "Nome da funcao Lambda de deteccao de anomalias"
  value       = aws_lambda_function.detect_anomalies.function_name
}

output "lambda_function_predict_failures_arn" {
  description = "ARN da funcao Lambda de predicao de falhas"
  value       = aws_lambda_function.predict_failures.arn
}

output "lambda_function_predict_failures_name" {
  description = "Nome da funcao Lambda de predicao de falhas"
  value       = aws_lambda_function.predict_failures.function_name
}

output "lambda_function_schedule_maintenance_arn" {
  description = "ARN da funcao Lambda de agendamento de manutencao"
  value       = aws_lambda_function.schedule_maintenance.arn
}

output "lambda_function_schedule_maintenance_name" {
  description = "Nome da funcao Lambda de agendamento de manutencao"
  value       = aws_lambda_function.schedule_maintenance.function_name
}

# ==================== API Gateway ====================

output "api_gateway_id" {
  description = "ID do API Gateway"
  value       = aws_apigatewayv2_api.dna_maquina.id
}

output "api_gateway_arn" {
  description = "ARN do API Gateway"
  value       = aws_apigatewayv2_api.dna_maquina.arn
}

output "api_gateway_endpoint" {
  description = "Endpoint do API Gateway"
  value       = aws_apigatewayv2_api.dna_maquina.api_endpoint
}

output "api_gateway_stage_name" {
  description = "Nome do stage do API Gateway"
  value       = aws_apigatewayv2_stage.dna_maquina.name
}

# ==================== EventBridge ====================

output "eventbridge_rule_process_readings_arn" {
  description = "ARN da regra do EventBridge para processamento de leituras"
  value       = aws_cloudwatch_event_rule.process_readings_schedule.arn
}

output "eventbridge_rule_detect_anomalies_arn" {
  description = "ARN da regra do EventBridge para deteccao de anomalias"
  value       = aws_cloudwatch_event_rule.detect_anomalies_schedule.arn
}

output "eventbridge_rule_predict_failures_arn" {
  description = "ARN da regra do EventBridge para predicao de falhas"
  value       = aws_cloudwatch_event_rule.predict_failures_schedule.arn
}

# ==================== SNS ====================

output "sns_topic_critical_alerts_arn" {
  description = "ARN do topico SNS de alertas criticos"
  value       = aws_sns_topic.critical_alerts.arn
}

output "sns_topic_high_alerts_arn" {
  description = "ARN do topico SNS de alertas altos"
  value       = aws_sns_topic.high_alerts.arn
}

output "sns_topic_medium_alerts_arn" {
  description = "ARN do topico SNS de alertas medios"
  value       = aws_sns_topic.medium_alerts.arn
}

output "sns_topic_low_alerts_arn" {
  description = "ARN do topico SNS de alertas baixos"
  value       = aws_sns_topic.low_alerts.arn
}

# ==================== CloudWatch ====================

output "cloudwatch_dashboard_name" {
  description = "Nome do dashboard do CloudWatch"
  value       = aws_cloudwatch_dashboard.dna_maquina.dashboard_name
}

output "cloudwatch_log_group_api_gateway_name" {
  description = "Nome do grupo de logs do API Gateway"
  value       = aws_cloudwatch_log_group.api_gateway.name
}

# ==================== Conta AWS ====================

output "aws_account_id" {
  description = "ID da conta AWS"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_caller_arn" {
  description = "ARN do chamador"
  value       = data.aws_caller_identity.current.arn
}

output "aws_caller_user_id" {
  description = "ID do usuario chamador"
  value       = data.aws_caller_identity.current.user_id
}

# ==================== Resumo ====================

output "summary" {
  description = "Resumo de todos os recursos criados"
  value = {
    vpc = {
      vpc_id           = module.vpc.vpc_id
      private_subnets  = module.vpc.private_subnets
      public_subnets   = module.vpc.public_subnets
    }
    
    iot = {
      endpoint_address = data.aws_iot_endpoint.current.endpoint_address
      thing_type       = aws_iot_thing_type.dna_maquina.name
      policy_name      = aws_iot_policy.dna_maquina_device_policy.name
    }
    
    databases = {
      dynamodb = {
        devices     = aws_dynamodb_table.devices.name
        sensors     = aws_dynamodb_table.sensors.name
        alerts      = aws_dynamodb_table.alerts.name
        predictions = aws_dynamodb_table.predictions.name
        maintenance = aws_dynamodb_table.maintenance.name
      }
      timestream = {
        database = aws_timestreamwrite_database.dna_maquina.database_name
        tables   = [
          aws_timestreamwrite_table.vibration.table_name,
          aws_timestreamwrite_table.temperature.table_name,
          aws_timestreamwrite_table.pressure.table_name,
          aws_timestreamwrite_table.current.table_name,
          aws_timestreamwrite_table.voltage.table_name
        ]
      }
    }
    
    storage = {
      s3 = {
        data_lake = aws_s3_bucket.data_lake.bucket
        firmware  = aws_s3_bucket.firmware.bucket
        logs      = aws_s3_bucket.logs.bucket
      }
    }
    
    compute = {
      lambda = {
        process_readings   = aws_lambda_function.process_readings.function_name
        detect_anomalies   = aws_lambda_function.detect_anomalies.function_name
        predict_failures   = aws_lambda_function.predict_failures.function_name
        schedule_maintenance = aws_lambda_function.schedule_maintenance.function_name
      }
    }
    
    networking = {
      api_gateway = {
        endpoint = aws_apigatewayv2_api.dna_maquina.api_endpoint
        stage    = aws_apigatewayv2_stage.dna_maquina.name
      }
    }
    
    messaging = {
      sns = {
        critical_alerts = aws_sns_topic.critical_alerts.name
        high_alerts    = aws_sns_topic.high_alerts.name
        medium_alerts  = aws_sns_topic.medium_alerts.name
        low_alerts     = aws_sns_topic.low_alerts.name
      }
    }
    
    monitoring = {
      cloudwatch = {
        dashboard = aws_cloudwatch_dashboard.dna_maquina.dashboard_name
      }
    }
  }
}
