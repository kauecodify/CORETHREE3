# CORETHREE3 - Outputs do Modulo IoT

output "iot_endpoint" {
  description = "Endpoint do IoT Core"
  value       = data.aws_iot_endpoint.current.endpoint_address
}

output "iot_policy_arn" {
  description = "ARN da politica IoT"
  value       = aws_iot_policy.sensor_policy.arn
}

output "iot_policy_name" {
  description = "Nome da politica IoT"
  value       = aws_iot_policy.sensor_policy.name
}

output "iot_role_arn" {
  description = "ARN da role IoT"
  value       = var.iot_role_arn != null ? var.iot_role_arn : aws_iam_role.iot_role[0].arn
}

output "iot_role_name" {
  description = "Nome da role IoT"
  value       = var.iot_role_name
}

output "iot_role_alias_arn" {
  description = "ARN do alias da role IoT"
  value       = aws_iot_role_alias.sensor_role_alias.arn
}

output "sensor_thing_names" {
  description = "Nomes das coisas (things) de sensores"
  value       = var.sensor_names != null ? var.sensor_names : []
}

output "sensor_thing_arns" {
  description = "ARNs das coisas (things) de sensores"
  value       = var.sensor_names != null ? [for thing in aws_iot_thing.sensors : thing.arn] : []
}

output "sensor_certificate_arns" {
  description = "ARNs dos certificados de sensores"
  value       = var.sensor_names != null ? [for cert in aws_iot_certificate.sensor_certificates : cert.arn] : []
}

output "sensor_certificate_ids" {
  description = "IDs dos certificados de sensores"
  value       = var.sensor_names != null ? [for cert in aws_iot_certificate.sensor_certificates : cert.id] : []
}

# Data source para endpoint IoT
data "aws_iot_endpoint" "current" {
  endpoint_type = "iot:Data-ATS"
}
