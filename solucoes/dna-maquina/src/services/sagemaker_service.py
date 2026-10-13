"""
CORETHREE3 - DNA de Maquinas
Servico de SageMaker

Servico para execucao de modelos de machine learning usando AWS SageMaker.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import boto3
import numpy as np
from botocore.exceptions import ClientError

from ..config.aws_config import aws_config
from ..config.sagemaker_config import SageMakerConfig, sagemaker_config
from ..models.prediction import Prediction, PredictionType, PredictionStatus
from ..models.reading import Reading

logger = logging.getLogger(__name__)


class SageMakerService:
    """
    Servico de SageMaker para manutencao preditiva.
    
    Responsabilidades:
    - Execucao de modelos de ML para deteccao de anomalias
    - Execucao de modelos para predicao de falhas
    - Execucao de modelos para estimativa de vida util (RUL)
    - Gerenciamento de endpoints
    """
    
    def __init__(self):
        """Inicializa o servico de SageMaker"""
        self.sagemaker_client = None
        self.sagemaker_runtime_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa os clientes AWS SageMaker"""
        try:
            self.sagemaker_client = boto3.client(
                'sagemaker',
                region_name=aws_config.REGION,
                aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY
            )
            
            self.sagemaker_runtime_client = boto3.client(
                'sagemaker-runtime',
                region_name=aws_config.REGION,
                aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY
            )
            
            logger.info("Clientes AWS SageMaker inicializados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar clientes AWS SageMaker: {e}")
            raise
    
    def get_client(self):
        """Retorna o cliente SageMaker"""
        if self.sagemaker_client is None:
            self._initialize_client()
        return self.sagemaker_client
    
    def get_runtime_client(self):
        """Retorna o cliente SageMaker Runtime"""
        if self.sagemaker_runtime_client is None:
            self._initialize_client()
        return self.sagemaker_runtime_client
    
    # ==================== Gerenciamento de Endpoints ====================
    
    def create_endpoint(self, endpoint_name: str, model_name: str, instance_type: str = 'ml.m5.large') -> bool:
        """Cria um endpoint do SageMaker"""
        try:
            # Criar configuracao do endpoint
            endpoint_config_name = f"{endpoint_name}-config"
            
            self.get_client().create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[
                    {
                        'VariantName': 'AllTraffic',
                        'ModelName': model_name,
                        'InitialInstanceCount': 1,
                        'InstanceType': instance_type,
                        'InitialVariantWeight': 1.0
                    }
                ]
            )
            
            # Criar endpoint
            self.get_client().create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            
            logger.info(f"Endpoint {endpoint_name} criado com sucesso")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao criar endpoint {endpoint_name}: {e}")
            return False
    
    def delete_endpoint(self, endpoint_name: str) -> bool:
        """Remove um endpoint do SageMaker"""
        try:
            self.get_client().delete_endpoint(
                EndpointName=endpoint_name
            )
            
            logger.info(f"Endpoint {endpoint_name} removido com sucesso")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao remover endpoint {endpoint_name}: {e}")
            return False
    
    def list_endpoints(self) -> List[Dict]:
        """Lista todos os endpoints"""
        try:
            response = self.get_client().list_endpoints()
            return response.get('Endpoints', [])
            
        except ClientError as e:
            logger.error(f"Erro ao listar endpoints: {e}")
            return []
    
    def get_endpoint_status(self, endpoint_name: str) -> Optional[str]:
        """Obtem o status de um endpoint"""
        try:
            response = self.get_client().describe_endpoint(
                EndpointName=endpoint_name
            )
            return response.get('EndpointStatus')
            
        except ClientError as e:
            logger.error(f"Erro ao obter status do endpoint {endpoint_name}: {e}")
            return None
    
    def wait_for_endpoint_ready(self, endpoint_name: str, timeout: int = 300) -> bool:
        """Aguarda o endpoint ficar pronto"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_endpoint_status(endpoint_name)
            if status == 'InService':
                return True
            elif status in ['Failed', 'Deleted']:
                return False
            time.sleep(10)
        
        return False
    
    # ==================== Detecao de Anomalias ====================
    
    def detect_anomalies(self, readings: List[Reading], machine_id: str, device_id: str) -> List[Prediction]:
        """Detecta anomalias em leituras de sensores"""
        predictions = []
        
        try:
            # Agrupar leituras por sensor
            readings_by_sensor: Dict[str, List[Reading]] = {}
            for reading in readings:
                sensor_id = reading.metadata.sensor_id
                if sensor_id not in readings_by_sensor:
                    readings_by_sensor[sensor_id] = []
                readings_by_sensor[sensor_id].append(reading)
            
            # Processar cada sensor
            for sensor_id, sensor_readings in readings_by_sensor.items():
                # Preparar dados para o modelo
                features = self._prepare_anomaly_detection_features(sensor_readings)
                
                # Chamar endpoint de deteccao de anomalias
                endpoint_name = sagemaker_config.ANOMALY_DETECTION_ENDPOINT
                result = self._invoke_endpoint(endpoint_name, features)
                
                if result:
                    # Processar resultados
                    for i, reading in enumerate(sensor_readings):
                        if i < len(result.get('predictions', [])):
                            prediction_data = result['predictions'][i]
                            
                            prediction = Prediction(
                                id=f"pred-{datetime.utcnow().isoformat()}-{i}",
                                prediction_type=PredictionType.ANOMALY_DETECTION,
                                status=PredictionStatus.COMPLETED,
                                machine_id=machine_id,
                                device_id=device_id,
                                sensor_ids=[sensor_id],
                                prediction_timestamp=datetime.utcnow(),
                                predicted_value=prediction_data.get('score'),
                                is_anomaly=prediction_data.get('is_anomaly', False),
                                anomaly_score=prediction_data.get('score'),
                                anomaly_type=prediction_data.get('type'),
                                confidence=prediction_data.get('confidence', 0.0),
                                model_name=sagemaker_config.ANOMALY_DETECTION_MODEL_NAME,
                                model_version=sagemaker_config.ANOMALY_DETECTION_MODEL_VERSION,
                                features=list(features.keys()),
                                feature_values=features,
                                created_at=datetime.utcnow()
                            )
                            predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao detectar anomalias: {e}")
            return []
    
    def _prepare_anomaly_detection_features(self, readings: List[Reading]) -> Dict[str, float]:
        """Prepara features para deteccao de anomalias"""
        features = {}
        
        for i, reading in enumerate(readings):
            features[f'value_{i}'] = reading.value
            
            if reading.rms is not None:
                features[f'rms_{i}'] = reading.rms
            if reading.peak is not None:
                features[f'peak_{i}'] = reading.peak
            if reading.frequency is not None:
                features[f'frequency_{i}'] = reading.frequency
            
            # Adicionar metadados
            features[f'timestamp_{i}'] = reading.metadata.timestamp.timestamp()
            features[f'quality_{i}'] = 1.0 if reading.metadata.quality.value == 'excellent' else 0.5
        
        return features
    
    # ==================== Predicao de Falhas ====================
    
    def predict_failures(self, readings: List[Reading], machine_id: str, device_id: str, 
                         historical_data: Optional[List[Dict]] = None) -> List[Prediction]:
        """Prediz falhas com base em leituras de sensores"""
        predictions = []
        
        try:
            # Preparar features
            features = self._prepare_failure_prediction_features(readings, historical_data)
            
            # Chamar endpoint de predicao de falhas
            endpoint_name = sagemaker_config.FAILURE_PREDICTION_ENDPOINT
            result = self._invoke_endpoint(endpoint_name, features)
            
            if result:
                # Processar resultados
                for prediction_data in result.get('predictions', []):
                    prediction = Prediction(
                        id=f"pred-failure-{datetime.utcnow().isoformat()}",
                        prediction_type=PredictionType.FAILURE_PREDICTION,
                        status=PredictionStatus.COMPLETED,
                        machine_id=machine_id,
                        device_id=device_id,
                        sensor_ids=list(set([r.metadata.sensor_id for r in readings])),
                        prediction_timestamp=datetime.utcnow(),
                        predicted_failure_date=datetime.fromisoformat(prediction_data.get('predicted_failure_date')) 
                                            if prediction_data.get('predicted_failure_date') else None,
                        failure_probability=prediction_data.get('failure_probability', 0.0),
                        confidence=prediction_data.get('confidence', 0.0),
                        model_name=sagemaker_config.FAILURE_PREDICTION_MODEL_NAME,
                        model_version=sagemaker_config.FAILURE_PREDICTION_MODEL_VERSION,
                        features=list(features.keys()),
                        feature_values=features,
                        interpretation=prediction_data.get('interpretation'),
                        recommended_actions=prediction_data.get('recommended_actions', []),
                        created_at=datetime.utcnow()
                    )
                    predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao prever falhas: {e}")
            return []
    
    def _prepare_failure_prediction_features(self, readings: List[Reading], 
                                               historical_data: Optional[List[Dict]] = None) -> Dict[str, float]:
        """Prepara features para predicao de falhas"""
        features = {}
        
        # Features das leituras atuais
        sensor_values: Dict[str, List[float]] = {}
        for reading in readings:
            sensor_id = reading.metadata.sensor_id
            if sensor_id not in sensor_values:
                sensor_values[sensor_id] = []
            sensor_values[sensor_id].append(reading.value)
        
        # Calcular estatisticas por sensor
        for sensor_id, values in sensor_values.items():
            features[f'{sensor_id}_avg'] = np.mean(values)
            features[f'{sensor_id}_max'] = np.max(values)
            features[f'{sensor_id}_min'] = np.min(values)
            features[f'{sensor_id}_std'] = np.std(values)
        
        # Features de vibracao
        vibration_readings = [r for r in readings if 'vibration' in r.metadata.sensor_id]
        if vibration_readings:
            features['vibration_rms_avg'] = np.mean([r.rms or 0 for r in vibration_readings])
            features['vibration_peak_max'] = np.max([r.peak or 0 for r in vibration_readings])
        
        # Features de temperatura
        temp_readings = [r for r in readings if 'temperature' in r.metadata.sensor_id]
        if temp_readings:
            features['temperature_avg'] = np.mean([r.value for r in temp_readings])
            features['temperature_max'] = np.max([r.value for r in temp_readings])
        
        # Features de corrente
        current_readings = [r for r in readings if 'current' in r.metadata.sensor_id]
        if current_readings:
            features['current_avg'] = np.mean([r.value for r in current_readings])
            features['current_std'] = np.std([r.value for r in current_readings])
        
        # Features historicas
        if historical_data:
            # Calcular tendencias
            for sensor_type in ['vibration', 'temperature', 'current']:
                historical_values = [d.get(sensor_type, 0) for d in historical_data if sensor_type in d]
                if historical_values:
                    features[f'{sensor_type}_trend'] = self._calculate_trend(historical_values)
        
        return features
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcula a tendencia de uma serie temporal"""
        if len(values) < 2:
            return 0.0
        
        # Calcula a inclinação da reta de regressão linear
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calcular coeficientes
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        
        return float(m)
    
    # ==================== Estimativa de Vida Util (RUL) ====================
    
    def predict_rul(self, readings: List[Reading], machine_id: str, device_id: str,
                   historical_data: Optional[List[Dict]] = None) -> List[Prediction]:
        """Prediz a vida util restante (RUL) de uma maquina"""
        predictions = []
        
        try:
            # Preparar features
            features = self._prepare_rul_features(readings, historical_data)
            
            # Chamar endpoint de RUL
            endpoint_name = sagemaker_config.RUL_ENDPOINT
            result = self._invoke_endpoint(endpoint_name, features)
            
            if result:
                # Processar resultados
                for prediction_data in result.get('predictions', []):
                    prediction = Prediction(
                        id=f"pred-rul-{datetime.utcnow().isoformat()}",
                        prediction_type=PredictionType.REMAINING_USEFUL_LIFE,
                        status=PredictionStatus.COMPLETED,
                        machine_id=machine_id,
                        device_id=device_id,
                        sensor_ids=list(set([r.metadata.sensor_id for r in readings])),
                        prediction_timestamp=datetime.utcnow(),
                        remaining_useful_life=prediction_data.get('rul_days'),
                        rul_confidence=prediction_data.get('confidence'),
                        confidence=prediction_data.get('confidence', 0.0),
                        model_name=sagemaker_config.RUL_MODEL_NAME,
                        model_version=sagemaker_config.RUL_MODEL_VERSION,
                        features=list(features.keys()),
                        feature_values=features,
                        interpretation=prediction_data.get('interpretation'),
                        recommended_actions=prediction_data.get('recommended_actions', []),
                        created_at=datetime.utcnow()
                    )
                    predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao prever RUL: {e}")
            return []
    
    def _prepare_rul_features(self, readings: List[Reading], 
                              historical_data: Optional[List[Dict]] = None) -> Dict[str, float]:
        """Prepara features para estimativa de RUL"""
        features = {}
        
        # Features de desgaste
        vibration_readings = [r for r in readings if 'vibration' in r.metadata.sensor_id]
        if vibration_readings:
            features['vibration_degradation'] = self._calculate_degradation(
                [r.value for r in vibration_readings]
            )
        
        temp_readings = [r for r in readings if 'temperature' in r.metadata.sensor_id]
        if temp_readings:
            features['temperature_degradation'] = self._calculate_degradation(
                [r.value for r in temp_readings]
            )
        
        # Features de operacao
        if historical_data:
            features['operating_hours'] = len(historical_data) * 24  # Approximate
            features['maintenance_count'] = sum(1 for d in historical_data if d.get('maintenance', False))
        
        # Features de eficiencia
        features['efficiency_score'] = self._calculate_efficiency_score(readings)
        
        return features
    
    def _calculate_degradation(self, values: List[float]) -> float:
        """Calcula o nivel de degradacao"""
        if not values:
            return 0.0
        
        # Normalizar valores
        normalized = [v / max(values) if max(values) > 0 else 0 for v in values]
        
        # Calcular tendencia
        trend = self._calculate_trend(normalized)
        
        # Calcular variabilidade
        variability = np.std(normalized)
        
        # Combinar metricas
        degradation = (abs(trend) + variability) / 2
        
        return float(min(degradation, 1.0))
    
    def _calculate_efficiency_score(self, readings: List[Reading]) -> float:
        """Calcula o score de eficiencia"""
        if not readings:
            return 1.0
        
        # Contar leituras com anomalias
        anomaly_count = sum(1 for r in readings if r.is_anomaly)
        
        # Calcular score
        efficiency = 1.0 - (anomaly_count / len(readings))
        
        return float(max(efficiency, 0.0))
    
    # ==================== Invocacao de Endpoints ====================
    
    def _invoke_endpoint(self, endpoint_name: str, features: Dict[str, Any]) -> Optional[Dict]:
        """Invoca um endpoint do SageMaker"""
        try:
            # Verificar se endpoint existe e esta pronto
            status = self.get_endpoint_status(endpoint_name)
            if status != 'InService':
                logger.warning(f"Endpoint {endpoint_name} nao esta pronto (status: {status})")
                return None
            
            # Preparar payload
            payload = {
                'features': features,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Invocar endpoint
            response = self.get_runtime_client().invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            
            # Processar resposta
            result = json.loads(response['Body'].read().decode('utf-8'))
            
            logger.info(f"Endpoint {endpoint_name} invocado com sucesso")
            return result
            
        except ClientError as e:
            logger.error(f"Erro ao invocar endpoint {endpoint_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao processar resposta do endpoint {endpoint_name}: {e}")
            return None
    
    # ==================== Batch Transform ====================
    
    def batch_transform(self, input_data: List[Dict], model_name: str, 
                       transform_job_name: str = None) -> Optional[str]:
        """Executa transformacao em batch"""
        try:
            job_name = transform_job_name or f"batch-transform-{datetime.utcnow().isoformat()}"
            
            # Criar job de transformacao
            response = self.get_client().create_transform_job(
                TransformJobName=job_name,
                ModelName=model_name,
                MaxConcurrentTransforms=1,
                MaxPayloadInMB=6,
                BatchStrategy='MultiRecord',
                TransformInput={
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': f"s3://{aws_config.S3_BUCKET_NAME}/batch-input/"
                        }
                    },
                    'ContentType': 'application/json',
                    'CompressionType': 'None',
                    'SplitType': 'Line'
                },
                TransformOutput={
                    'S3OutputPath': f"s3://{aws_config.S3_BUCKET_NAME}/batch-output/"
                },
                TransformResources={
                    'InstanceType': 'ml.m5.xlarge',
                    'InstanceCount': 1
                }
            )
            
            logger.info(f"Job de transformacao {job_name} criado com sucesso")
            return response['TransformJobArn']
            
        except ClientError as e:
            logger.error(f"Erro ao criar job de transformacao: {e}")
            return None
    
    def get_transform_job_status(self, job_name: str) -> Optional[str]:
        """Obtem o status de um job de transformacao"""
        try:
            response = self.get_client().describe_transform_job(
                TransformJobName=job_name
            )
            return response.get('TransformJobStatus')
            
        except ClientError as e:
            logger.error(f"Erro ao obter status do job {job_name}: {e}")
            return None
    
    # ==================== Utilitarios ====================
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Obtem informacoes sobre um modelo"""
        try:
            response = self.get_client().describe_model(
                ModelName=model_name
            )
            return {
                'model_name': model_name,
                'model_arn': response.get('ModelArn'),
                'creation_time': response.get('CreationTime'),
                'training_algorithm': response.get('PrimaryContainer', {}).get('TrainingAlgorithm')
            }
            
        except ClientError as e:
            logger.error(f"Erro ao obter informacoes do modelo {model_name}: {e}")
            return None
    
    def list_models(self) -> List[Dict]:
        """Lista todos os modelos"""
        try:
            response = self.get_client().list_models()
            return [
                {
                    'model_name': model['ModelName'],
                    'model_arn': model['ModelArn'],
                    'creation_time': model['CreationTime']
                }
                for model in response.get('Models', [])
            ]
            
        except ClientError as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    def initialize_models(self) -> bool:
        """Inicializa os modelos e endpoints necessarios"""
        try:
            # Criar endpoints para cada modelo
            endpoints = [
                (sagemaker_config.ANOMALY_DETECTION_ENDPOINT, sagemaker_config.ANOMALY_DETECTION_MODEL_NAME),
                (sagemaker_config.FAILURE_PREDICTION_ENDPOINT, sagemaker_config.FAILURE_PREDICTION_MODEL_NAME),
                (sagemaker_config.RUL_ENDPOINT, sagemaker_config.RUL_MODEL_NAME)
            ]
            
            for endpoint_name, model_name in endpoints:
                # Verificar se endpoint ja existe
                existing_endpoints = self.list_endpoints()
                if any(e['EndpointName'] == endpoint_name for e in existing_endpoints):
                    logger.info(f"Endpoint {endpoint_name} ja existe")
                    continue
                
                # Criar endpoint
                if not self.create_endpoint(endpoint_name, model_name):
                    logger.error(f"Falha ao criar endpoint {endpoint_name}")
                    return False
                
                # Aguardar endpoint ficar pronto
                if not self.wait_for_endpoint_ready(endpoint_name):
                    logger.error(f"Endpoint {endpoint_name} nao ficou pronto")
                    return False
            
            logger.info("Todos os endpoints foram inicializados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar modelos: {e}")
            return False
