# CORETHREE3 - Infraestrutura AWS com Terraform
# Configuracao principal de infraestrutura serverless

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    
    random = {
      source  = "hashicorp/random"
      version = ">= 3.5"
    }
  }
  
  backend "s3" {
    bucket         = "corethree3-terraform-state"
    key            = "global/infra/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "corethree3-terraform-lock"
  }
}

# Configuracao do provider AWS
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "CORETHREE3"
      Terraform   = "true"
      ManagedBy   = "terraform"
    }
  }
}

# Modulo de VPC (opcional para servicos que necessitam)
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  count = var.create_vpc ? 1 : 0
  
  name = "corethree3-vpc"
  cidr = var.vpc_cidr
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  public_subnets  = [cidrsubnet(var.vpc_cidr, 8, 1), cidrsubnet(var.vpc_cidr, 8, 2), cidrsubnet(var.vpc_cidr, 8, 3)]
  private_subnets = [cidrsubnet(var.vpc_cidr, 8, 101), cidrsubnet(var.vpc_cidr, 8, 102), cidrsubnet(var.vpc_cidr, 8, 103)]
  
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de IoT Core para DNA de Maquinas
module "iot_core" {
  source = "./modules/iot"
  
  iot_policy_name = "CORETHREE3_IoTPolicy"
  iot_role_name   = "CORETHREE3_IoTRole"
  
  # Permissoes para sensores
  iot_policy_document = jsonencode({
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
        Resource = [
          "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
        ]
      }
    ]
  })
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de Timestream para dados de sensores
module "timestream" {
  source = "./modules/timestream"
  
  database_name = "corethree3_sensors"
  
  # Tabelas para diferentes tipos de dados
  tables = [
    {
      name = "machine_vibration"
      retention_properties = {
        MemoryStoreRetentionPeriodInHours = 24
        MagneticStoreRetentionPeriodInDays = 365
      }
    },
    {
      name = "machine_temperature"
      retention_properties = {
        MemoryStoreRetentionPeriodInHours = 24
        MagneticStoreRetentionPeriodInDays = 365
      }
    },
    {
      name = "machine_pressure"
      retention_properties = {
        MemoryStoreRetentionPeriodInHours = 24
        MagneticStoreRetentionPeriodInDays = 365
      }
    },
    {
      name = "machine_current"
      retention_properties = {
        MemoryStoreRetentionPeriodInHours = 24
        MagneticStoreRetentionPeriodInDays = 365
      }
    }
  ]
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de Lambda para processamento
module "lambda_processing" {
  source = "./modules/lambda"
  
  for_each = {
    sensor_processor = {
      name        = "corethree3-sensor-processor"
      description = "Processador de dados de sensores IoT"
      runtime     = "python3.11"
      handler     = "lambda_function.lambda_handler"
      memory_size = 256
      timeout     = 30
      
      environment = {
        TIMESTREAM_DATABASE = module.timestream.database_name
        IOT_ENDPOINT          = module.iot_core.iot_endpoint
      }
      
      policy_arns = [
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        module.iot_core.iot_policy_arn,
        module.timestream.write_policy_arn
      ]
    }
    
    anomaly_detector = {
      name        = "corethree3-anomaly-detector"
      description = "Detector de anomalias com ML"
      runtime     = "python3.11"
      handler     = "lambda_function.lambda_handler"
      memory_size = 512
      timeout     = 60
      
      environment = {
        SAGEMAKER_ENDPOINT = module.sagemaker.endpoint_name
        ALERT_TOPIC_ARN    = module.sns.alert_topic_arn
      }
      
      policy_arns = [
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        module.sagemaker.inference_policy_arn,
        module.sns.publish_policy_arn
      ]
    }
    
    prediction_model = {
      name        = "corethree3-prediction-model"
      description = "Modelo de predicao de falhas"
      runtime     = "python3.11"
      handler     = "lambda_function.lambda_handler"
      memory_size = 1024
      timeout     = 120
      
      environment = {
        SAGEMAKER_ENDPOINT = module.sagemaker.endpoint_name
        MODEL_BUCKET       = module.s3.models_bucket_id
      }
      
      policy_arns = [
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        module.sagemaker.inference_policy_arn,
        module.s3.read_policy_arn
      ]
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
    Module      = "Processing"
  }
}

# Modulo de SageMaker para modelos de ML
module "sagemaker" {
  source = "./modules/sagemaker"
  
  model_name          = "corethree3-prediction-model"
  execution_role_arn  = aws_iam_role.sagemaker_execution.arn
  endpoint_name       = "corethree3-prediction-endpoint"
  instance_type       = "ml.m5.large"
  initial_instance_count = 1
  
  # Configuracao do modelo
  model_config = {
    image_uri     = "763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:1.13.1-gpu-py39"
    model_data_url = "s3://${module.s3.models_bucket_id}/models/prediction-model.tar.gz"
    
    environment = {
      SAGEMAKER_PROGRAM = "inference.py"
      SAGEMAKER_SUBMIT_DIRECTORY = "/opt/ml/model/code"
      SAGEMAKER_CONTAINER_LOG_LEVEL = "20"
      SAGEMAKER_REGION = var.aws_region
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de API Gateway
module "api_gateway" {
  source = "./modules/api_gateway"
  
  api_name        = "corethree3-api"
  description     = "API principal do CORETHREE3"
  protocol_type   = "HTTP"
  
  routes = [
    {
      path   = "/sensors"
      method = "POST"
      lambda_arn = module.lambda_processing["sensor_processor"].arn
    },
    {
      path   = "/sensors/{id}"
      method = "GET"
      lambda_arn = module.lambda_processing["sensor_processor"].arn
    },
    {
      path   = "/predictions"
      method = "POST"
      lambda_arn = module.lambda_processing["prediction_model"].arn
    },
    {
      path   = "/anomalies"
      method = "POST"
      lambda_arn = module.lambda_processing["anomaly_detector"].arn
    },
    {
      path   = "/machines"
      method = "GET"
      lambda_arn = module.lambda_processing["sensor_processor"].arn
    },
    {
      path   = "/machines/{id}"
      method = "GET"
      lambda_arn = module.lambda_processing["sensor_processor"].arn
    }
  ]
  
  # Configuracao de autorizacao
  authorizers = [
    {
      name          = "cognito-authorizer"
      type          = "JWT"
      identity_source = "$request.header.Authorization"
      issuer       = "https://cognito-idp.${var.aws_region}.amazonaws.com/${module.cognito.user_pool_id}"
      audiences    = [module.cognito.user_pool_client_id]
    }
  ]
  
  # Configuracao de rate limiting
  usage_plans = [
    {
      name         = "standard-plan"
      throttle_settings = {
        burst_limit = 100
        rate_limit  = 50
      }
      api_stages = [
        {
          api_id = module.api_gateway.api_id
          stage  = "prod"
        }
      ]
    }
  ]
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de S3 para armazenamento
module "s3" {
  source = "./modules/s3"
  
  buckets = {
    data_bucket = {
      name = "corethree3-data-${data.aws_caller_identity.current.account_id}"
      acl  = "private"
      versioning = true
      logging = true
      
      lifecycle_rules = [
        {
          id     = "archive_old_data"
          status = "Enabled"
          
          transition = [
            {
              days          = 30
              storage_class = "STANDARD_IA"
            },
            {
              days          = 90
              storage_class = "GLACIER"
            }
          ]
          
          expiration = {
            days = 365
          }
        }
      ]
      
      server_side_encryption = {
        algorithm = "AES256"
      }
    }
    
    models_bucket = {
      name = "corethree3-models-${data.aws_caller_identity.current.account_id}"
      acl  = "private"
      versioning = true
      
      lifecycle_rules = [
        {
          id     = "archive_old_models"
          status = "Enabled"
          
          transition = [
            {
              days          = 90
              storage_class = "GLACIER"
            }
          ]
        }
      ]
      
      server_side_encryption = {
        algorithm = "AES256"
      }
    }
    
    logs_bucket = {
      name = "corethree3-logs-${data.aws_caller_identity.current.account_id}"
      acl  = "private"
      versioning = false
      
      lifecycle_rules = [
        {
          id     = "expire_old_logs"
          status = "Enabled"
          
          expiration = {
            days = 90
          }
        }
      ]
      
      server_side_encryption = {
        algorithm = "AES256"
      }
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de DynamoDB para dados estruturados
module "dynamodb" {
  source = "./modules/dynamodb"
  
  tables = {
    machines_table = {
      name           = "corethree3-machines"
      billing_mode   = "PAY_PER_REQUEST"
      hash_key       = "machine_id"
      
      attributes = [
        {
          name = "machine_id"
          type = "S"
        },
        {
          name = "status"
          type = "S"
        },
        {
          name = "health_score"
          type = "N"
        }
      ]
      
      global_secondary_indexes = [
        {
          name            = "status-index"
          hash_key       = "status"
          projection_type = "ALL"
        },
        {
          name            = "health-index"
          hash_key       = "health_score"
          projection_type = "ALL"
        }
      ]
      
      ttl = {
        attribute_name = "expiration_time"
        enabled        = true
      }
    }
    
    sensors_table = {
      name           = "corethree3-sensors"
      billing_mode   = "PAY_PER_REQUEST"
      hash_key       = "sensor_id"
      range_key      = "timestamp"
      
      attributes = [
        {
          name = "sensor_id"
          type = "S"
        },
        {
          name = "timestamp"
          type = "N"
        },
        {
          name = "machine_id"
          type = "S"
        },
        {
          name = "sensor_type"
          type = "S"
        }
      ]
      
      global_secondary_indexes = [
        {
          name            = "machine-index"
          hash_key       = "machine_id"
          range_key      = "timestamp"
          projection_type = "ALL"
        },
        {
          name            = "type-index"
          hash_key       = "sensor_type"
          range_key      = "timestamp"
          projection_type = "ALL"
        }
      ]
      
      ttl = {
        attribute_name = "expiration_time"
        enabled        = true
      }
    }
    
    alerts_table = {
      name           = "corethree3-alerts"
      billing_mode   = "PAY_PER_REQUEST"
      hash_key       = "alert_id"
      
      attributes = [
        {
          name = "alert_id"
          type = "S"
        },
        {
          name = "machine_id"
          type = "S"
        },
        {
          name = "severity"
          type = "S"
        },
        {
          name = "status"
          type = "S"
        },
        {
          name = "timestamp"
          type = "N"
        }
      ]
      
      global_secondary_indexes = [
        {
          name            = "machine-index"
          hash_key       = "machine_id"
          range_key      = "timestamp"
          projection_type = "ALL"
        },
        {
          name            = "severity-index"
          hash_key       = "severity"
          range_key      = "timestamp"
          projection_type = "ALL"
        },
        {
          name            = "status-index"
          hash_key       = "status"
          range_key      = "timestamp"
          projection_type = "ALL"
        }
      ]
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de SNS para notificacoes
module "sns" {
  source = "./modules/sns"
  
  topics = {
    alert_topic = {
      name         = "corethree3-alerts"
      display_name = "Alertas do CORETHREE3"
      
      subscriptions = [
        {
          protocol = "email"
          endpoint = "alerts@corethree3.com"
        },
        {
          protocol = "sms"
          endpoint = "+5511999999999"
        }
      ]
    }
    
    notification_topic = {
      name         = "corethree3-notifications"
      display_name = "Notificacoes do CORETHREE3"
      
      subscriptions = [
        {
          protocol = "email"
          endpoint = "notifications@corethree3.com"
        }
      ]
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de CloudWatch para monitoramento
module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  alarms = [
    {
      name          = "corethree3-high-error-rate"
      description   = "Alerta para taxa de erros elevada"
      comparison_operator = "GreaterThanThreshold"
      evaluation_periods  = 1
      metric_name         = "Errors"
      namespace           = "AWS/ApiGateway"
      period              = 60
      statistic           = "Sum"
      threshold           = 10
      alarm_actions       = [module.sns.alert_topic_arn]
      
      dimensions = {
        ApiName = module.api_gateway.api_name
      }
    },
    {
      name          = "corethree3-high-latency"
      description   = "Alerta para latencia elevada"
      comparison_operator = "GreaterThanThreshold"
      evaluation_periods  = 3
      metric_name         = "Latency"
      namespace           = "AWS/ApiGateway"
      period              = 60
      statistic           = "Average"
      threshold           = 1000
      alarm_actions       = [module.sns.alert_topic_arn]
      
      dimensions = {
        ApiName = module.api_gateway.api_name
      }
    },
    {
      name          = "corethree3-high-cpu"
      description   = "Alerta para uso elevado de CPU"
      comparison_operator = "GreaterThanThreshold"
      evaluation_periods  = 5
      metric_name         = "CPUUtilization"
      namespace           = "AWS/Lambda"
      period              = 60
      statistic           = "Average"
      threshold           = 80
      alarm_actions       = [module.sns.alert_topic_arn]
      
      dimensions = {
        FunctionName = module.lambda_processing["sensor_processor"].function_name
      }
    }
  ]
  
  dashboards = [
    {
      name = "corethree3-overview"
      body = jsonencode({
        widgets = [
          {
            type   = "metric"
            x      = 0
            y      = 0
            width  = 12
            height = 6
            
            properties = {
              metrics = [
                ["AWS/ApiGateway", "Requests", "ApiName", module.api_gateway.api_name, "Stage", "prod"]
              ]
              period = 300
              stat   = "Sum"
              region = var.aws_region
              title  = "Requisicoes da API"
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
                ["AWS/ApiGateway", "Latency", "ApiName", module.api_gateway.api_name, "Stage", "prod"]
              ]
              period = 300
              stat   = "Average"
              region = var.aws_region
              title  = "Latencia da API"
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
                ["AWS/Lambda", "Invocations", "FunctionName", module.lambda_processing["sensor_processor"].function_name]
              ]
              period = 300
              stat   = "Sum"
              region = var.aws_region
              title  = "Invocacoes Lambda"
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
                ["AWS/Lambda", "Errors", "FunctionName", module.lambda_processing["sensor_processor"].function_name]
              ]
              period = 300
              stat   = "Sum"
              region = var.aws_region
              title  = "Erros Lambda"
            }
          }
        ]
      })
    }
  ]
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de Cognito para autenticacao
module "cognito" {
  source = "./modules/cognito"
  
  user_pool_name = "corethree3-user-pool"
  
  # Configuracao do user pool
  user_pool_config = {
    alias_attributes = ["email"]
    auto_verified_attributes = ["email"]
    
    password_policy = {
      minimum_length                   = 8
      require_lowercase                = true
      require_numbers                  = true
      require_symbols                  = true
      require_uppercase                = true
      temporary_password_validity_days = 7
    }
    
    account_recovery_setting = {
      recovery_mechanism = ["verified_email"]
    }
    
    email_configuration = {
      email_sending_account = "COGNITO_DEFAULT"
    }
    
    schema_attributes = [
      {
        name       = "email"
        attribute_data_type = "String"
        mutable    = true
        required   = true
      },
      {
        name       = "name"
        attribute_data_type = "String"
        mutable    = true
        required   = false
      },
      {
        name       = "company"
        attribute_data_type = "String"
        mutable    = true
        required   = false
      },
      {
        name       = "role"
        attribute_data_type = "String"
        mutable    = true
        required   = false
      }
    ]
  }
  
  # Configuracao do client
  client_config = {
    name = "corethree3-client"
    
    callback_urls = [
      "https://app.corethree3.com/callback",
      "https://localhost:3000/callback"
    ]
    
    logout_urls = [
      "https://app.corethree3.com/logout",
      "https://localhost:3000/logout"
    ]
    
    allowed_oauth_flows = ["code", "implicit"]
    allowed_oauth_scopes = ["phone", "email", "profile", "openid", "aws.cognito.signin.user.admin"]
    allowed_oauth_flows_user_pools = ["true"]
    
    supported_identity_providers = ["COGNITO"]
    explicit_auth_flows = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  }
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# Modulo de Kinesis para streaming de dados
module "kinesis" {
  source = "./modules/kinesis"
  
  streams = {
    sensor_data_stream = {
      name             = "corethree3-sensor-data"
      shard_count      = 3
      retention_period = 24
      
      shard_level_metrics = [
        "IncomingBytes",
        "IncomingRecords",
        "IteratorAgeMilliseconds",
        "OutgoingBytes",
        "OutgoingRecords",
        "ReadProvisionedThroughputExceeded",
        "WriteProvisionedThroughputExceeded"
      ]
      
      tags = {
        Environment = var.environment
        Project     = "CORETHREE3"
        StreamType  = "SensorData"
      }
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# IAM Role para SageMaker
resource "aws_iam_role" "sagemaker_execution" {
  name = "corethree3-sagemaker-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = {
    Environment = var.environment
    Project     = "CORETHREE3"
  }
}

# IAM Policy para SageMaker
resource "aws_iam_role_policy_attachment" "sagemaker_execution" {
  role       = aws_iam_role.sagemaker_execution.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy_attachment" "sagemaker_s3" {
  role       = aws_iam_role.sagemaker_execution.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "sagemaker_cloudwatch" {
  role       = aws_iam_role.sagemaker_execution.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# Data source para account ID
data "aws_caller_identity" "current" {}

# Outputs
output "api_endpoint" {
  value = module.api_gateway.api_endpoint
}

output "user_pool_id" {
  value = module.cognito.user_pool_id
}

output "user_pool_client_id" {
  value = module.cognito.user_pool_client_id
}

output "data_bucket_name" {
  value = module.s3.buckets["data_bucket"].id
}

output "models_bucket_name" {
  value = module.s3.buckets["models_bucket"].id
}

output "logs_bucket_name" {
  value = module.s3.buckets["logs_bucket"].id
}

output "iot_endpoint" {
  value = module.iot_core.iot_endpoint
}

output "timestream_database_name" {
  value = module.timestream.database_name
}

output "sagemaker_endpoint_name" {
  value = module.sagemaker.endpoint_name
}

output "cloudwatch_dashboard_url" {
  value = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${module.cloudwatch.dashboards[0].name}"
}
