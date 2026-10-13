"""
CORETHREE3 - Gestao de Vendas Avancada
Configuracoes do Amazon SageMaker
"""

import os
from typing import Dict, List, Any


class SageMakerConfig:
    """Configuracoes do Amazon SageMaker para ML"""
    
    # Configuracoes gerais
    ENABLE_SAGEMAKER: bool = os.getenv("ENABLE_SAGEMAKER", "True").lower() == "true"
    SAGEMAKER_REGION: str = os.getenv("SAGEMAKER_REGION", "us-east-1")
    
    # Modelos disponiveis
    AVAILABLE_MODELS: List[str] = [
        "xgboost",
        "linear-learner",
        "mlp",
        "factorization-machines",
        "knn",
        "pca",
        "kmeans",
        "randomcutforest",
        "blazingtext",
        "object2vec",
        "object-detection",
        "image-classification",
        "semantic-segmentation",
    ]
    
    # Configuracoes de treinamento
    TRAINING_INSTANCE_TYPE: str = os.getenv("TRAINING_INSTANCE_TYPE", "ml.m5.xlarge")
    TRAINING_INSTANCE_COUNT: int = int(os.getenv("TRAINING_INSTANCE_COUNT", "1"))
    TRAINING_MAX_RUNTIME: int = int(os.getenv("TRAINING_MAX_RUNTIME", "86400"))  # 24 horas
    TRAINING_MAX_JOBS: int = int(os.getenv("TRAINING_MAX_JOBS", "5"))
    
    # Configuracoes de inferencia
    INFERENCE_INSTANCE_TYPE: str = os.getenv("INFERENCE_INSTANCE_TYPE", "ml.t2.medium")
    INFERENCE_INSTANCE_COUNT: int = int(os.getenv("INFERENCE_INSTANCE_COUNT", "1"))
    INFERENCE_MAX_CONCURRENCY: int = int(os.getenv("INFERENCE_MAX_CONCURRENCY", "10"))
    
    # Configuracoes de notebook
    NOTEBOOK_INSTANCE_TYPE: str = os.getenv("NOTEBOOK_INSTANCE_TYPE", "ml.t3.xlarge")
    NOTEBOOK_VOLUME_SIZE: int = int(os.getenv("NOTEBOOK_VOLUME_SIZE", "30"))  # GB
    NOTEBOOK_LIFECYCLE_CONFIG: str = os.getenv("NOTEBOOK_LIFECYCLE_CONFIG", "")
    
    # Modelos de previsao de demanda
    DEMAND_FORECAST_MODEL: Dict[str, Any] = {
        "name": "demand-forecast",
        "algorithm": "xgboost",
        "instance_type": "ml.m5.xlarge",
        "instance_count": 1,
        "hyperparameters": {
            "num_round": 100,
            "max_depth": 5,
            "eta": 0.2,
            "gamma": 4,
            "min_child_weight": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "reg:squarederror",
            "eval_metric": "rmse"
        },
        "input_shape": [100],  # Numero de features
        "output_shape": [1],   # Previsao de 1 valor
        "data_type": "float32"
    }
    
    # Modelos de otimizacao de estoque
    STOCK_OPTIMIZATION_MODEL: Dict[str, Any] = {
        "name": "stock-optimization",
        "algorithm": "xgboost",
        "instance_type": "ml.m5.xlarge",
        "instance_count": 1,
        "hyperparameters": {
            "num_round": 100,
            "max_depth": 6,
            "eta": 0.1,
            "gamma": 3,
            "min_child_weight": 5,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "objective": "reg:squarederror"
        }
    }
    
    # Modelos de segmentacao de clientes
    CUSTOMER_SEGMENTATION_MODEL: Dict[str, Any] = {
        "name": "customer-segmentation",
        "algorithm": "kmeans",
        "instance_type": "ml.m5.large",
        "instance_count": 1,
        "hyperparameters": {
            "k": 5,  # Numero de clusters
            "max_iter": 100,
            "tolerance": 0.001
        },
        "num_clusters": 5,
        "feature_dim": 10  # Numero de features
    }
    
    # Modelos de previsao de churn
    CHURN_PREDICTION_MODEL: Dict[str, Any] = {
        "name": "churn-prediction",
        "algorithm": "xgboost",
        "instance_type": "ml.m5.xlarge",
        "instance_count": 1,
        "hyperparameters": {
            "num_round": 150,
            "max_depth": 6,
            "eta": 0.1,
            "gamma": 4,
            "min_child_weight": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "binary:logistic",
            "eval_metric": "auc"
        }
    }
    
    # Configuracoes de processamento de dados
    PROCESSING_INSTANCE_TYPE: str = os.getenv("PROCESSING_INSTANCE_TYPE", "ml.m5.xlarge")
    PROCESSING_INSTANCE_COUNT: int = int(os.getenv("PROCESSING_INSTANCE_COUNT", "1"))
    
    # Configuracoes de pipelines
    PIPELINE_ENABLED: bool = os.getenv("PIPELINE_ENABLED", "True").lower() == "true"
    PIPELINE_NAME: str = "gestao-vendas-pipeline"
    PIPELINE_STEPS: List[Dict[str, Any]] = [
        {
            "name": "PreprocessData",
            "type": "ProcessingJob",
            "processor": "sklearn",
            "code": "preprocess.py"
        },
        {
            "name": "TrainModel",
            "type": "TrainingJob",
            "algorithm": "xgboost"
        },
        {
            "name": "EvaluateModel",
            "type": "ProcessingJob",
            "processor": "sklearn",
            "code": "evaluate.py"
        },
        {
            "name": "DeployModel",
            "type": "ModelDeployment",
            "instance_type": "ml.t2.medium"
        }
    ]
    
    # Configuracoes de monitoramento
    MODEL_MONITOR_ENABLED: bool = True
    MODEL_MONITOR_INTERVAL: int = 3600  # 1 hora
    MODEL_MONITOR_THRESHOLD: float = 0.8  # Limiar de performance
    
    # Configuracoes de versionamento
    MODEL_VERSIONING_ENABLED: bool = True
    MAX_MODEL_VERSIONS: int = 10
    
    # Configuracoes de logging
    LOG_TRAINING: bool = True
    LOG_INFERENCE: bool = True
    LOG_METRICS: bool = True
    
    # Configuracoes de cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutos
    
    # Configuracoes de timeout
    TIMEOUT_TRAINING: int = 86400  # 24 horas
    TIMEOUT_INFERENCE: int = 30  # 30 segundos
    
    # Configuracoes de retry
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # 1 segundo
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Dict[str, Any]:
        """Obter configuracao de um modelo"""
        models = {
            "demand-forecast": cls.DEMAND_FORECAST_MODEL,
            "stock-optimization": cls.STOCK_OPTIMIZATION_MODEL,
            "customer-segmentation": cls.CUSTOMER_SEGMENTATION_MODEL,
            "churn-prediction": cls.CHURN_PREDICTION_MODEL
        }
        return models.get(model_name, {})
    
    @classmethod
    def get_hyperparameters(cls, model_name: str) -> Dict[str, Any]:
        """Obter hiperparametros de um modelo"""
        config = cls.get_model_config(model_name)
        return config.get("hyperparameters", {})


# Instancia das configuracoes
sagemaker_config = SageMakerConfig()
