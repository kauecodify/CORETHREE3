# CORETHREE3 - Modulo IoT Core
# Gerenciamento de dispositivos IoT para sensores

resource "aws_iot_thing_type" "sensor_type" {
  name = "CORETHREE3_Sensor"
  
  attributes = {
    Description = "Tipo de coisa para sensores CORETHREE3"
  }
  
  tags = merge(var.tags, {
    Name = "CORETHREE3_Sensor_Type"
  })
}

resource "aws_iot_thing" "sensors" {
  for_each = var.sensor_names != null ? { for sensor in var.sensor_names : sensor => sensor } : {}
  
  name          = each.value
  thing_type_name = aws_iot_thing_type.sensor_type.name
  
  attributes = {
    Project     = "CORETHREE3"
    Environment = var.environment
    Type        = "Sensor"
  }
  
  tags = merge(var.tags, {
    Name = each.value
  })
}

resource "aws_iot_policy" "sensor_policy" {
  name        = var.iot_policy_name
  description = "Politica para sensores CORETHREE3"
  policy      = var.iot_policy_document
  
  tags = merge(var.tags, {
    Name = var.iot_policy_name
  })
}

resource "aws_iot_certificate" "sensor_certificates" {
  for_each = var.sensor_names != null ? { for sensor in var.sensor_names : sensor => sensor } : {}
  
  active = true
  
  tags = merge(var.tags, {
    Name = "${each.value}_Certificate"
  })
}

resource "aws_iot_thing_principal_attachment" "sensor_attachment" {
  for_each = var.sensor_names != null ? { for sensor in var.sensor_names : sensor => sensor } : {}
  
  principal = aws_iot_certificate.sensor_certificates[each.value].arn
  thing     = aws_iot_thing.sensors[each.value].name
}

resource "aws_iot_policy_attachment" "sensor_policy_attachment" {
  for_each = var.sensor_names != null ? { for sensor in var.sensor_names : sensor => sensor } : {}
  
  policy = aws_iot_policy.sensor_policy.name
  target = aws_iot_certificate.sensor_certificates[each.value].arn
}

resource "aws_iot_role_alias" "sensor_role_alias" {
  name = var.iot_role_name
  
  role_arn = var.iot_role_arn != null ? var.iot_role_arn : aws_iam_role.iot_role[0].arn
  
  tags = merge(var.tags, {
    Name = var.iot_role_name
  })
}

resource "aws_iam_role" "iot_role" {
  count = var.iot_role_arn == null ? 1 : 0
  
  name = var.iot_role_name
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "iot.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = merge(var.tags, {
    Name = var.iot_role_name
  })
}

resource "aws_iam_role_policy_attachment" "iot_role_cloudwatch" {
  count = var.iot_role_arn == null ? 1 : 0
  
  role       = aws_iam_role.iot_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSIoTLogging"
}

resource "aws_iam_role_policy_attachment" "iot_role_dynamodb" {
  count = var.iot_role_arn == null ? 1 : 0
  
  role       = aws_iam_role.iot_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "iot_role_timestream" {
  count = var.iot_role_arn == null ? 1 : 0
  
  role       = aws_iam_role.iot_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonTimestreamFullAccess"
}

# Outputs
output "iot_endpoint" {
  value = data.aws_iot_endpoint.current.endpoint_address
}

output "iot_policy_arn" {
  value = aws_iot_policy.sensor_policy.arn
}

output "iot_role_arn" {
  value = var.iot_role_arn != null ? var.iot_role_arn : aws_iam_role.iot_role[0].arn
}

output "iot_role_alias_arn" {
  value = aws_iot_role_alias.sensor_role_alias.arn
}

output "sensor_thing_names" {
  value = var.sensor_names != null ? var.sensor_names : []
}

output "sensor_certificate_arns" {
  value = var.sensor_names != null ? [for cert in aws_iot_certificate.sensor_certificates : cert.arn] : []
}

# Data source para endpoint IoT
data "aws_iot_endpoint" "current" {
  endpoint_type = "iot:Data-ATS"
}
