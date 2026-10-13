"""
CORETHREE3 - DNA de Maquinas
Configuracao do SageMaker

Este arquivo define os recursos do AWS SageMaker para manutencao preditiva.
"""

# ==================== SageMaker Models ====================

resource "aws_sagemaker_model" "anomaly_detection" {
  name               = "${var.project_name}-${var.environment}-anomaly-detection"
  execution_role_arn = aws_iam_role.sagemaker_execution_role.arn
  
  primary_container {
    image          = "763104351884.dkr.ecr.${var.aws_region}.amazonaws.com/randomcutforest:latest"
    model_data_url = "s3://${aws_s3_bucket.data_lake.bucket}/models/anomaly-detection/model.tar.gz"
    environment = {
      SAGEMAKER_PROGRAM            = "inference"
      SAGEMAKER_SUBMIT_DIRECTORY   = "/opt/ml/model/code"
      SAGEMAKER_CONTAINER_LOG_LEVEL = "20"
      SAGEMAKER_REGION              = var.aws_region
    }
  }
  
  tags = local.tags
}

resource "aws_sagemaker_model" "failure_prediction" {
  name               = "${var.project_name}-${var.environment}-failure-prediction"
  execution_role_arn = aws_iam_role.sagemaker_execution_role.arn
  
  primary_container {
    image          = "763104351884.dkr.ecr.${var.aws_region}.amazonaws.com/xgboost:latest"
    model_data_url = "s3://${aws_s3_bucket.data_lake.bucket}/models/failure-prediction/model.tar.gz"
    environment = {
      SAGEMAKER_PROGRAM            = "inference"
      SAGEMAKER_SUBMIT_DIRECTORY   = "/opt/ml/model/code"
      SAGEMAKER_CONTAINER_LOG_LEVEL = "20"
      SAGEMAKER_REGION              = var.aws_region
    }
  }
  
  tags = local.tags
}

resource "aws_sagemaker_model" "rul_prediction" {
  name               = "${var.project_name}-${var.environment}-rul-prediction"
  execution_role_arn = aws_iam_role.sagemaker_execution_role.arn
  
  primary_container {
    image          = "763104351884.dkr.ecr.${var.aws_region}.amazonaws.com/xgboost:latest"
    model_data_url = "s3://${aws_s3_bucket.data_lake.bucket}/models/rul-prediction/model.tar.gz"
    environment = {
      SAGEMAKER_PROGRAM            = "inference"
      SAGEMAKER_SUBMIT_DIRECTORY   = "/opt/ml/model/code"
      SAGEMAKER_CONTAINER_LOG_LEVEL = "20"
      SAGEMAKER_REGION              = var.aws_region
    }
  }
  
  tags = local.tags
}

# ==================== SageMaker Endpoints ====================

resource "aws_sagemaker_endpoint_configuration" "anomaly_detection" {
  name = "${var.project_name}-${var.environment}-anomaly-detection-config"
  
  production_variants {
    variant_name           = "AllTraffic"
    model_name            = aws_sagemaker_model.anomaly_detection.name
    initial_instance_count = 1
    instance_type         = "ml.m5.large"
    initial_variant_weight = 1.0
  }
  
  tags = local.tags
}

resource "aws_sagemaker_endpoint_configuration" "failure_prediction" {
  name = "${var.project_name}-${var.environment}-failure-prediction-config"
  
  production_variants {
    variant_name           = "AllTraffic"
    model_name            = aws_sagemaker_model.failure_prediction.name
    initial_instance_count = 1
    instance_type         = "ml.m5.xlarge"
    initial_variant_weight = 1.0
  }
  
  tags = local.tags
}

resource "aws_sagemaker_endpoint_configuration" "rul_prediction" {
  name = "${var.project_name}-${var.environment}-rul-prediction-config"
  
  production_variants {
    variant_name           = "AllTraffic"
    model_name            = aws_sagemaker_model.rul_prediction.name
    initial_instance_count = 1
    instance_type         = "ml.m5.xlarge"
    initial_variant_weight = 1.0
  }
  
  tags = local.tags
}

resource "aws_sagemaker_endpoint" "anomaly_detection" {
  name                 = "${var.project_name}-${var.environment}-anomaly-detection"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.anomaly_detection.name
  
  tags = local.tags
}

resource "aws_sagemaker_endpoint" "failure_prediction" {
  name                 = "${var.project_name}-${var.environment}-failure-prediction"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.failure_prediction.name
  
  tags = local.tags
}

resource "aws_sagemaker_endpoint" "rul_prediction" {
  name                 = "${var.project_name}-${var.environment}-rul-prediction"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.rul_prediction.name
  
  tags = local.tags
}

# ==================== IAM Role para SageMaker ====================

resource "aws_iam_role" "sagemaker_execution_role" {
  name = "${var.project_name}-${var.environment}-sagemaker-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "sagemaker_execution_role_s3" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "sagemaker_execution_role_cloudwatch" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_iam_role_policy_attachment" "sagemaker_execution_role_ecr" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# ==================== Notebook Instances ====================

resource "aws_sagemaker_notebook_instance" "development" {
  count = var.environment == "dev" ? 1 : 0
  
  name          = "${var.project_name}-${var.environment}-notebook"
  role_arn      = aws_iam_role.sagemaker_execution_role.arn
  instance_type = "ml.t3.medium"
  
  lifecycle_config_name = aws_sagemaker_notebook_instance_lifecycle_config.development[0].name
  
  tags = local.tags
}

resource "aws_sagemaker_notebook_instance_lifecycle_config" "development" {
  count = var.environment == "dev" ? 1 : 0
  
  name = "${var.project_name}-${var.environment}-notebook-lifecycle"
  
  on_start = [
    {
      content = <<EOF
#!/bin/bash
set -e

# Instalar dependencias
pip install pandas numpy scikit-learn matplotlib seaborn boto3 sagemaker

# Configurar ambiente
echo "Configurando ambiente..."
EOF
    }
  ]
  
  on_create = [
    {
      content = <<EOF
#!/bin/bash
set -e

# Clonar repositorio
git clone https://github.com/kauecodify/CORETHREE3.git /home/ec2-user/CORETHREE3

# Instalar dependencias do projeto
cd /home/ec2-user/CORETHREE3/solucoes/dna-maquina
pip install -r requirements.txt
EOF
    }
  ]
  
  tags = local.tags
}

# ==================== Training Jobs ====================

resource "aws_sagemaker_training_job" "anomaly_detection_training" {
  name = "${var.project_name}-${var.environment}-anomaly-detection-training"
  
  algorithm_specification {
    training_image  = "763104351884.dkr.ecr.${var.aws_region}.amazonaws.com/randomcutforest:latest"
    training_input_mode = "File"
    enable_sage_metric_time_series = true
  }
  
  role_arn = aws_iam_role.sagemaker_execution_role.arn
  
  input_data_config {
    channel_name = "train"
    data_source {
      s3_data_source {
        s3_data_type = "S3Prefix"
        s3_uri = "s3://${aws_s3_bucket.data_lake.bucket}/data/training/anomaly-detection/"
        s3_data_distribution_type = "FullyReplicated"
      }
    }
    content_type = "text/csv"
    compression_type = "None"
  }
  
  output_data_config {
    s3_output_path = "s3://${aws_s3_bucket.data_lake.bucket}/output/training/anomaly-detection/"
  }
  
  resource_config {
    instance_type = "ml.m5.xlarge"
    instance_count = 1
    volume_size_in_gb = 30
  }
  
  stopping_condition {
    max_runtime_in_seconds = 86400  # 24 horas
  }
  
  hyper_parameters = {
    num_samples_per_tree = "100"
    num_trees = "100"
    feature_dim = "10"
  }
  
  tags = local.tags
}

resource "aws_sagemaker_training_job" "failure_prediction_training" {
  name = "${var.project_name}-${var.environment}-failure-prediction-training"
  
  algorithm_specification {
    training_image  = "763104351884.dkr.ecr.${var.aws_region}.amazonaws.com/xgboost:latest"
    training_input_mode = "File"
  }
  
  role_arn = aws_iam_role.sagemaker_execution_role.arn
  
  input_data_config {
    channel_name = "train"
    data_source {
      s3_data_source {
        s3_data_type = "S3Prefix"
        s3_uri = "s3://${aws_s3_bucket.data_lake.bucket}/data/training/failure-prediction/"
        s3_data_distribution_type = "FullyReplicated"
      }
    }
    content_type = "text/csv"
    compression_type = "None"
  }
  
  input_data_config {
    channel_name = "validation"
    data_source {
      s3_data_source {
        s3_data_type = "S3Prefix"
        s3_uri = "s3://${aws_s3_bucket.data_lake.bucket}/data/validation/failure-prediction/"
        s3_data_distribution_type = "FullyReplicated"
      }
    }
    content_type = "text/csv"
    compression_type = "None"
  }
  
  output_data_config {
    s3_output_path = "s3://${aws_s3_bucket.data_lake.bucket}/output/training/failure-prediction/"
  }
  
  resource_config {
    instance_type = "ml.m5.xlarge"
    instance_count = 1
    volume_size_in_gb = 30
  }
  
  stopping_condition {
    max_runtime_in_seconds = 86400
  }
  
  hyper_parameters = {
    num_round = "100"
    max_depth = "5"
    eta = "0.2"
    gamma = "4"
    min_child_weight = "1"
    subsample = "0.8"
    colsample_bytree = "0.8"
    objective = "binary:logistic"
    eval_metric = "auc"
  }
  
  tags = local.tags
}

# ==================== Model Registry ====================

resource "aws_sagemaker_model_package" "anomaly_detection" {
  model_package_name = "${var.project_name}-${var.environment}-anomaly-detection-package"
  model_package_group_name = "${var.project_name}"
  model_package_description = "Modelo de deteccao de anomalias para DNA de Maquinas"
  
  model_approval_status = "Approved"
  
  source_algorithm {
    algorithm_name = "Random Cut Forest"
    model_data_url = "s3://${aws_s3_bucket.data_lake.bucket}/models/anomaly-detection/model.tar.gz"
  }
  
  tags = local.tags
}

resource "aws_sagemaker_model_package" "failure_prediction" {
  model_package_name = "${var.project_name}-${var.environment}-failure-prediction-package"
  model_package_group_name = "${var.project_name}"
  model_package_description = "Modelo de predicao de falhas para DNA de Maquinas"
  
  model_approval_status = "Approved"
  
  source_algorithm {
    algorithm_name = "XGBoost"
    model_data_url = "s3://${aws_s3_bucket.data_lake.bucket}/models/failure-prediction/model.tar.gz"
  }
  
  tags = local.tags
}

# ==================== Pipelines ====================

resource "aws_sagemaker_pipeline" "training_pipeline" {
  name = "${var.project_name}-${var.environment}-training-pipeline"
  
  pipeline_definition = jsonencode({
    Version = "1.0"
    Steps = [
      {
        Name = "PreprocessData"
        Type = "SageMaker"
        Arguments = {
          ProcessingJobName = "${var.project_name}-${var.environment}-preprocess-data"
          ProcessingResources = {
            ClusterConfig = {
              InstanceCount = 1
              InstanceType = "ml.m5.xlarge"
              VolumeSizeInGB = 30
            }
          }
          ProcessingJobConfig = {
            InputDataConfig = [
              {
                ChannelName = "input"
                DataSource = {
                  S3DataSource = {
                    S3DataType = "S3Prefix"
                    S3Uri = "s3://${aws_s3_bucket.data_lake.bucket}/data/raw/"
                    S3DataDistributionType = "FullyReplicated"
                  }
                }
              }
            ]
            OutputDataConfig = {
              S3OutputPath = "s3://${aws_s3_bucket.data_lake.bucket}/data/processed/"
            }
            RoleArn = aws_iam_role.sagemaker_execution_role.arn
          }
        }
      },
      {
        Name = "TrainAnomalyDetection"
        Type = "SageMaker"
        Arguments = {
          TrainingJobName = aws_sagemaker_training_job.anomaly_detection_training.name
        }
        DependsOn = ["PreprocessData"]
      },
      {
        Name = "TrainFailurePrediction"
        Type = "SageMaker"
        Arguments = {
          TrainingJobName = aws_sagemaker_training_job.failure_prediction_training.name
        }
        DependsOn = ["PreprocessData"]
      },
      {
        Name = "CreateModels"
        Type = "SageMaker"
        Arguments = {
          ModelCreationConfig = {
            ModelName = aws_sagemaker_model.anomaly_detection.name
            ExecutionRoleArn = aws_iam_role.sagemaker_execution_role.arn
            PrimaryContainer = {
              Image = "763104351884.dkr.ecr.${var.aws_region}.amazonaws.com/randomcutforest:latest"
              ModelDataUrl = "s3://${aws_s3_bucket.data_lake.bucket}/models/anomaly-detection/model.tar.gz"
            }
          }
        }
        DependsOn = ["TrainAnomalyDetection"]
      },
      {
        Name = "DeployEndpoints"
        Type = "SageMaker"
        Arguments = {
          EndpointConfigName = aws_sagemaker_endpoint_configuration.anomaly_detection.name
          EndpointName = aws_sagemaker_endpoint.anomaly_detection.name
        }
        DependsOn = ["CreateModels"]
      }
    ]
  })
  
  tags = local.tags
}

# ==================== Saidas ====================

output "sagemaker_endpoint_anomaly_detection" {
  description = "Endpoint de deteccao de anomalias"
  value = aws_sagemaker_endpoint.anomaly_detection.endpoint_name
}

output "sagemaker_endpoint_failure_prediction" {
  description = "Endpoint de predicao de falhas"
  value = aws_sagemaker_endpoint.failure_prediction.endpoint_name
}

output "sagemaker_endpoint_rul_prediction" {
  description = "Endpoint de predicao de RUL"
  value = aws_sagemaker_endpoint.rul_prediction.endpoint_name
}

output "sagemaker_notebook_instance" {
  description = "Instancia de notebook do SageMaker"
  value = var.environment == "dev" ? aws_sagemaker_notebook_instance.development[0].name : "Nao disponivel em producao"
}

output "sagemaker_models" {
  description = "Modelos do SageMaker"
  value = {
    anomaly_detection = aws_sagemaker_model.anomaly_detection.name
    failure_prediction = aws_sagemaker_model.failure_prediction.name
    rul_prediction = aws_sagemaker_model.rul_prediction.name
  }
}
