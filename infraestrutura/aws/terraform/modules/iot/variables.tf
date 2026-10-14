# CORETHREE3 - Variaveis do Modulo IoT

variable "environment" {
  description = "Ambiente de deploy"
  type        = string
  default     = "prod"
}

variable "iot_policy_name" {
  description = "Nome da politica IoT"
  type        = string
  default     = "CORETHREE3_IoTPolicy"
}

variable "iot_role_name" {
  description = "Nome da role IoT"
  type        = string
  default     = "CORETHREE3_IoTRole"
}

variable "iot_role_arn" {
  description = "ARN da role IoT (opcional - se ja existir)"
  type        = string
  default     = null
}

variable "iot_policy_document" {
  description = "Documento da politica IoT em JSON"
  type        = string
  default     = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect",
          "iot:Publish",
          "iot:Subscribe",
          "iot:Receive"
        ]
        Resource = ["*"]
      }
    ]
  })
}

variable "sensor_names" {
  description = "Lista de nomes de sensores"
  type        = list(string)
  default     = null
}

variable "tags" {
  description = "Tags para os recursos"
  type        = map(string)
  default     = {}
}
