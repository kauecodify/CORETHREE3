"""
CORETHREE3 - DNA de Maquinas
Configuracao do Greengrass

Este arquivo define os recursos do AWS IoT Greengrass para processamento edge.
"""

# ==================== Greengrass Core Definition ====================

resource "aws_iot_greengrass_core_definition" "dna_maquina" {
  name = "${var.project_name}-${var.environment}-DNAMaquina-Core"
  
  initial_version {
    core_version = "2.9.0"
    cores = [
      {
        id = "1"
        thing_arn = aws_iot_thing.greengrass_core.arn
        certificate_arn = aws_iot_certificate.greengrass_core.arn
        sync_shadow = true
      }
    ]
  }
  
  tags = local.tags
}

# ==================== Greengrass Thing ====================

resource "aws_iot_thing" "greengrass_core" {
  name = "${var.project_name}-${var.environment}-Greengrass-Core"
  thing_type_name = aws_iot_thing_type.dna_maquina.name
  
  attributes = {
    Project = var.project_name
    Environment = var.environment
    Type = "GreengrassCore"
  }
  
  tags = local.tags
}

# ==================== Greengrass Certificate ====================

resource "aws_iot_certificate" "greengrass_core" {
  active = true
  
  tags = local.tags
}

resource "aws_iot_thing_principal_attachment" "greengrass_core" {
  principal = aws_iot_certificate.greengrass_core.arn
  thing = aws_iot_thing.greengrass_core.name
}

resource "aws_iot_policy_attachment" "greengrass_core" {
  policy = aws_iot_policy.dna_maquina_device_policy.name
  target = aws_iot_certificate.greengrass_core.arn
}

# ==================== Greengrass Group ====================

resource "aws_iot_greengrass_group" "dna_maquina" {
  name = "${var.project_name}-${var.environment}-DNAMaquina-Group"
  
  core_definition_version_arn = aws_iot_greengrass_core_definition.dna_maquina.versions[0].arn
  
  tags = local.tags
}

# ==================== Greengrass Component ====================

resource "aws_iot_greengrass_component_version" "data_processor" {
  component_name = "${var.project_name}-${var.environment}-DataProcessor"
  
  lambda_function {
    lambda_arn = aws_lambda_function.edge_data_processor.arn
    
    lambda_function_config {
      timeout = 30
      memory_size = 128
    }
  }
  
  platform {
    os = "LINUX"
    architecture = "X86_64"
  }
  
  tags = local.tags
}

resource "aws_iot_greengrass_component_version" "anomaly_detector" {
  component_name = "${var.project_name}-${var.environment}-AnomalyDetector"
  
  lambda_function {
    lambda_arn = aws_lambda_function.edge_anomaly_detector.arn
    
    lambda_function_config {
      timeout = 60
      memory_size = 256
    }
  }
  
  platform {
    os = "LINUX"
    architecture = "X86_64"
  }
  
  tags = local.tags
}

resource "aws_iot_greengrass_component_version" "predictor" {
  component_name = "${var.project_name}-${var.environment}-Predictor"
  
  lambda_function {
    lambda_arn = aws_lambda_function.edge_predictor.arn
    
    lambda_function_config {
      timeout = 60
      memory_size = 256
    }
  }
  
  platform {
    os = "LINUX"
    architecture = "X86_64"
  }
  
  tags = local.tags
}

# ==================== Greengrass Deployment ====================

resource "aws_iot_greengrass_group_version" "dna_maquina" {
  group_id = aws_iot_greengrass_group.dna_maquina.id
  
  core_version_arn = aws_iot_greengrass_core_definition.dna_maquina.versions[0].arn
  
  components = {
    (aws_iot_greengrass_component_version.data_processor.component_name) = {
      version_arn = aws_iot_greengrass_component_version.data_processor.arn
      configuration_update = {
        merge = jsonencode({
          "FunctionConfiguration" = {
            "Timeout" = 30
            "MemorySize" = 128
          }
        })
      }
    }
    (aws_iot_greengrass_component_version.anomaly_detector.component_name) = {
      version_arn = aws_iot_greengrass_component_version.anomaly_detector.arn
      configuration_update = {
        merge = jsonencode({
          "FunctionConfiguration" = {
            "Timeout" = 60
            "MemorySize" = 256
          }
        })
      }
    }
    (aws_iot_greengrass_component_version.predictor.component_name) = {
      version_arn = aws_iot_greengrass_component_version.predictor.arn
      configuration_update = {
        merge = jsonencode({
          "FunctionConfiguration" = {
            "Timeout" = 60
            "MemorySize" = 256
          }
        })
      }
    }
  }
  
  tags = local.tags
}

resource "aws_iot_greengrass_deployment" "dna_maquina" {
  name = "${var.project_name}-${var.environment}-DNAMaquina-Deployment"
  
  group_arns = [aws_iot_greengrass_group.dna_maquina.arn]
  group_version_id = aws_iot_greengrass_group_version.dna_maquina.version_id
  
  deployment_type = "NewDeployment"
  
  tags = local.tags
}

# ==================== Lambda Functions para Edge ====================

resource "aws_lambda_function" "edge_data_processor" {
  function_name = "${var.project_name}-${var.environment}-edge-data-processor"
  role          = aws_iam_role.greengrass_lambda_role.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"
  timeout       = 30
  memory_size   = 128
  
  filename = "lambda/edge_data_processor.zip"
  
  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT_NAME = var.project_name
      IOT_ENDPOINT = data.aws_iot_endpoint.current.endpoint_address
    }
  }
  
  tags = local.tags
}

resource "aws_lambda_function" "edge_anomaly_detector" {
  function_name = "${var.project_name}-${var.environment}-edge-anomaly-detector"
  role          = aws_iam_role.greengrass_lambda_role.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"
  timeout       = 60
  memory_size   = 256
  
  filename = "lambda/edge_anomaly_detector.zip"
  
  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT_NAME = var.project_name
      MODEL_PATH = "/opt/ml/model"
    }
  }
  
  tags = local.tags
}

resource "aws_lambda_function" "edge_predictor" {
  function_name = "${var.project_name}-${var.environment}-edge-predictor"
  role          = aws_iam_role.greengrass_lambda_role.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"
  timeout       = 60
  memory_size   = 256
  
  filename = "lambda/edge_predictor.zip"
  
  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT_NAME = var.project_name
      MODEL_PATH = "/opt/ml/model"
    }
  }
  
  tags = local.tags
}

# ==================== IAM Role para Greengrass Lambda ====================

resource "aws_iam_role" "greengrass_lambda_role" {
  name = "${var.project_name}-${var.environment}-greengrass-lambda-role"
  
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

resource "aws_iam_role_policy_attachment" "greengrass_lambda_basic_execution" {
  role       = aws_iam_role.greengrass_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "greengrass_lambda_iot_access" {
  name = "${var.project_name}-${var.environment}-greengrass-lambda-iot-access"
  role = aws_iam_role.greengrass_lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Describe*",
          "iot:List*",
          "iot:Get*",
          "iot:Publish",
          "iot:Receive",
          "iot:UpdateThingShadow",
          "iot:GetThingShadow"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "greengrass_lambda_greengrass_access" {
  name = "${var.project_name}-${var.environment}-greengrass-lambda-greengrass-access"
  role = aws_iam_role.greengrass_lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "greengrass:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# ==================== Greengrass Subscription ====================

resource "aws_iot_topic_rule" "greengrass_subscription" {
  name = "${var.project_name}-${var.environment}-Greengrass-Subscription"
  description = "Regra para rotear mensagens para Greengrass"
  enabled = true
  sql = "SELECT * FROM 'corethree3/dna-maquina/data'"
  sql_version = "2016-03-23"
  
  greengrass {
    core_definition_version_arn = aws_iot_greengrass_core_definition.dna_maquina.versions[0].arn
    group_arn = aws_iot_greengrass_group.dna_maquina.arn
    
    function {
      function_arn = aws_lambda_function.edge_data_processor.arn
      timeout = 30
    }
  }
  
  tags = local.tags
}

# ==================== Greengrass Logger ====================

resource "aws_iot_greengrass_logger_definition" "dna_maquina" {
  name = "${var.project_name}-${var.environment}-DNAMaquina-Logger"
  
  initial_version {
    loggers = [
      {
        id = "1"
        type = "File"
        component = "GreengrassSystem"
        level = "INFO"
        space = "10"
        path = "/greengrass/log"
      },
      {
        id = "2"
        type = "File"
        component = "DataProcessor"
        level = "DEBUG"
        space = "10"
        path = "/greengrass/log"
      }
    ]
  }
  
  tags = local.tags
}

# ==================== Greengrass Resource ====================

resource "aws_iot_greengrass_resource_definition" "s3_access" {
  name = "${var.project_name}-${var.environment}-S3-Access"
  
  initial_version {
    resources = [
      {
        id = "1"
        name = "S3DataLakeAccess"
        resource_data_container {
          local_volume_resource_data {
            source_path = "/greengrass/s3"
            destination_path = "/s3"
          }
        }
      }
    ]
  }
  
  tags = local.tags
}

# ==================== Saidas ====================

output "greengrass_core_definition_arn" {
  description = "ARN da definicao do Greengrass Core"
  value = aws_iot_greengrass_core_definition.dna_maquina.arn
}

output "greengrass_group_arn" {
  description = "ARN do grupo Greengrass"
  value = aws_iot_greengrass_group.dna_maquina.arn
}

output "greengrass_deployment_arn" {
  description = "ARN do deployment Greengrass"
  value = aws_iot_greengrass_deployment.dna_maquina.arn
}

output "greengrass_thing_name" {
  description = "Nome da Thing Greengrass"
  value = aws_iot_thing.greengrass_core.name
}

output "greengrass_component_names" {
  description = "Nomes dos componentes Greengrass"
  value = [
    aws_iot_greengrass_component_version.data_processor.component_name,
    aws_iot_greengrass_component_version.anomaly_detector.component_name,
    aws_iot_greengrass_component_version.predictor.component_name
  ]
}
