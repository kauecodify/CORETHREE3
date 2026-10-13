"""
CORETHREE3 - DNA de Maquinas
Configuracoes do Amazon SageMaker para ML
"""

import os
from typing import Dict, List, Any


class SageMakerConfig:
    """Configuracoes do Amazon SageMaker para manutencao preditiva"""
    
    # Configuracoes gerais
    ENABLE_SAGEMAKER: bool = os.getenv("ENABLE_SAGEMAKER", "True").lower() == "true"
    SAGEMAKER_REGION: str = os.getenv("SAGEMAKER_REGION", "us-east-1")
    
    # Modelos disponiveis
    AVAILABLE_MODELS: List[str] = [
        "xgboost",
        "linear-learner",
        "randomcutforest",
        "kmeans",
        "pca",
        "blazingtext",
        "object2vec",
        "seq2seq",
        "deepfm",
        "factorization-machines"
    ]
    
    # Configuracoes de treinamento
    TRAINING_INSTANCE_TYPE: str = os.getenv("TRAINING_INSTANCE_TYPE", "ml.m5.xlarge")
    TRAINING_INSTANCE_COUNT: int = int(os.getenv("TRAINING_INSTANCE_COUNT", "1"))
    TRAINING_MAX_RUNTIME: int = int(os.getenv("TRAINING_MAX_RUNTIME", "86400"))  # 24 horas
    TRAINING_MAX_JOBS: int = int(os.getenv("TRAINING_MAX_JOBS", "10"))
    
    # Configuracoes de inferencia
    INFERENCE_INSTANCE_TYPE: str = os.getenv("INFERENCE_INSTANCE_TYPE", "ml.t2.medium")
    INFERENCE_INSTANCE_COUNT: int = int(os.getenv("INFERENCE_INSTANCE_COUNT", "2"))
    INFERENCE_MAX_CONCURRENCY: int = int(os.getenv("INFERENCE_MAX_CONCURRENCY", "50"))
    
    # Configuracoes de notebook
    NOTEBOOK_INSTANCE_TYPE: str = os.getenv("NOTEBOOK_INSTANCE_TYPE", "ml.t3.xlarge")
    NOTEBOOK_VOLUME_SIZE: int = int(os.getenv("NOTEBOOK_VOLUME_SIZE", "50"))  # GB
    NOTEBOOK_LIFECYCLE_CONFIG: str = os.getenv("NOTEBOOK_LIFECYCLE_CONFIG", "")
    
    # Modelo de deteccao de anomalias (Isolation Forest)
    ANOMALY_DETECTION_MODEL: Dict[str, Any] = {
        "name": "anomaly-detection",
        "algorithm": "randomcutforest",
        "instance_type": "ml.m5.xlarge",
        "instance_count": 1,
        "hyperparameters": {
            "num_trees": 100,
            "num_samples": 256,
            "feature_dim": 10,
            "random_state": 42
        },
        "input_shape": [10],  # Numero de features
        "output_shape": [1],   # Score de anomalia
        "data_type": "float32",
        "threshold": 0.95  # Limiar para anomalia
    }
    
    # Modelo de previsao de falhas (LSTM)
    FAILURE_PREDICTION_MODEL: Dict[str, Any] = {
        "name": "failure-prediction",
        "algorithm": "blazingtext",  # Para sequencias temporais
        "instance_type": "ml.m5.xlarge",
        "instance_count": 1,
        "hyperparameters": {
            "mode": "supervised",
            "epochs": 100,
            "batch_size": 32,
            "learning_rate": 0.001,
            "vector_dim": 100,
            "min_count": 5,
            "window_size": 5,
            "sample": 0.001
        },
        "input_shape": [100, 10],  # 100 timesteps, 10 features
        "output_shape": [2],  # 2 classes: normal, falha
        "sequence_length": 100,
        "prediction_horizon": 14  # Dias
    }
    
    # Modelo de previsao de RUL (Remaining Useful Life)
    RUL_PREDICTION_MODEL: Dict[str, Any] = {
        "name": "rul-prediction",
        "algorithm": "xgboost",
        "instance_type": "ml.m5.xlarge",
        "instance_count": 1,
        "hyperparameters": {
            "num_round": 200,
            "max_depth": 8,
            "eta": 0.1,
            "gamma": 4,
            "min_child_weight": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "reg:squarederror",
            "eval_metric": "rmse"
        },
        "input_shape": [50],  # Numero de features
        "output_shape": [1],   # Dias de vida util
        "data_type": "float32",
        "min_rul": 1,
        "max_rul": 365
    }
    
    # Modelo de classificacao de falhas
    FAILURE_CLASSIFICATION_MODEL: Dict[str, Any] = {
        "name": "failure-classification",
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
            "objective": "multi:softprob",
            "num_class": 10
        },
        "input_shape": [30],  # Numero de features
        "output_shape": [10],  # 10 tipos de falhas
        "data_type": "float32",
        "failure_types": [
            "vibration_excessive",
            "temperature_high",
            "pressure_low",
            "current_overload",
            "voltage_unstable",
            "bearing_wear",
            "lubrication_failure",
            "mechanical_failure",
            "electrical_failure",
            "unknown"
        ]
    }
    
    # Modelo de clusterizacao de maquinas
    MACHINE_CLUSTERING_MODEL: Dict[str, Any] = {
        "name": "machine-clustering",
        "algorithm": "kmeans",
        "instance_type": "ml.m5.large",
        "instance_count": 1,
        "hyperparameters": {
            "k": 5,  # Numero de clusters
            "max_iter": 100,
            "tolerance": 0.001
        },
        "num_clusters": 5,
        "feature_dim": 20  # Numero de features
    }
    
    # Configuracoes de processamento de dados
    PROCESSING_INSTANCE_TYPE: str = os.getenv("PROCESSING_INSTANCE_TYPE", "ml.m5.xlarge")
    PROCESSING_INSTANCE_COUNT: int = int(os.getenv("PROCESSING_INSTANCE_COUNT", "1"))
    
    # Configuracoes de pipelines
    PIPELINE_ENABLED: bool = os.getenv("PIPELINE_ENABLED", "True").lower() == "true"
    PIPELINE_NAME: str = "dna-maquina-pipeline"
    PIPELINE_STEPS: List[Dict[str, Any]] = [
        {
            "name": "PreprocessData",
            "type": "ProcessingJob",
            "processor": "sklearn",
            "code": "preprocess.py",
            "instance_type": "ml.m5.xlarge"
        },
        {
            "name": "FeatureEngineering",
            "type": "ProcessingJob",
            "processor": "sklearn",
            "code": "feature_engineering.py",
            "instance_type": "ml.m5.xlarge"
        },
        {
            "name": "TrainAnomalyDetection",
            "type": "TrainingJob",
            "algorithm": "randomcutforest",
            "instance_type": "ml.m5.xlarge"
        },
        {
            "name": "TrainFailurePrediction",
            "type": "TrainingJob",
            "algorithm": "blazingtext",
            "instance_type": "ml.m5.xlarge"
        },
        {
            "name": "TrainRULPrediction",
            "type": "TrainingJob",
            "algorithm": "xgboost",
            "instance_type": "ml.m5.xlarge"
        },
        {
            "name": "EvaluateModels",
            "type": "ProcessingJob",
            "processor": "sklearn",
            "code": "evaluate.py",
            "instance_type": "ml.m5.large"
        },
        {
            "name": "DeployModels",
            "type": "ModelDeployment",
            "instance_type": "ml.t2.medium",
            "initial_instance_count": 2
        }
    ]
    
    # Configuracoes de monitoramento
    MODEL_MONITOR_ENABLED: bool = True
    MODEL_MONITOR_INTERVAL: int = 3600  # 1 hora
    MODEL_MONITOR_THRESHOLD: float = 0.85  # Limiar de performance
    
    # Configuracoes de drift detection
    DRIFT_DETECTION_ENABLED: bool = True
    DRIFT_DETECTION_INTERVAL: int = 86400  # 24 horas
    DRIFT_DETECTION_THRESHOLD: float = 0.1  # Limiar de drift
    
    # Configuracoes de versionamento
    MODEL_VERSIONING_ENABLED: bool = True
    MAX_MODEL_VERSIONS: int = 10
    AUTO_VERSIONING: bool = True
    
    # Configuracoes de logging
    LOG_TRAINING: bool = True
    LOG_INFERENCE: bool = True
    LOG_METRICS: bool = True
    LOG_PREDICTIONS: bool = True
    
    # Configuracoes de cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutos
    
    # Configuracoes de timeout
    TIMEOUT_TRAINING: int = 86400  # 24 horas
    TIMEOUT_INFERENCE: int = 10  # 10 segundos
    TIMEOUT_PREDICTION: int = 30  # 30 segundos
    
    # Configuracoes de retry
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # 1 segundo
    
    # Configuracoes de alertas
    ALERT_ON_ANOMALY: bool = True
    ALERT_ON_FAILURE_PREDICTION: bool = True
    ALERT_ON_RUL_LOW: bool = True
    ALERT_RUL_THRESHOLD: int = 7  # Dias
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Dict[str, Any]:
        """Obter configuracao de um modelo"""
        models = {
            "anomaly-detection": cls.ANOMALY_DETECTION_MODEL,
            "failure-prediction": cls.FAILURE_PREDICTION_MODEL,
            "rul-prediction": cls.RUL_PREDICTION_MODEL,
            "failure-classification": cls.FAILURE_CLASSIFICATION_MODEL,
            "machine-clustering": cls.MACHINE_CLUSTERING_MODEL
        }
        return models.get(model_name, {})
    
    @classmethod
    def get_hyperparameters(cls, model_name: str) -> Dict[str, Any]:
        """Obter hiperparametros de um modelo"""
        config = cls.get_model_config(model_name)
        return config.get("hyperparameters", {})
    
    @classmethod
    def get_failure_types(cls) -> List[str]:
        """Obter tipos de falhas"""
        return cls.FAILURE_CLASSIFICATION_MODEL.get("failure_types", [])


# Instancia das configuracoes
sagemaker_config = SageMakerConfig()
