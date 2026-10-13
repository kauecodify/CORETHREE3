"""
CORETHREE3 - DNA de Maquinas
Handler de Predicoes

Handler para processamento de predicoes de manutencao preditiva.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models.prediction import Prediction, PredictionType, PredictionStatus
from ..models.reading import Reading, ReadingBatch
from ..models.alert import Alert, AlertSeverity, AlertType
from ..services.sagemaker_service import SageMakerService
from ..services.timestream_service import TimestreamService
from ..services.alert_service import AlertService
from ..handlers.alert_handler import AlertHandler

logger = logging.getLogger(__name__)


class PredictionHandler:
    """
    Handler de Predicoes para manutencao preditiva.
    
    Responsabilidades:
    - Execucao de modelos de predicao
    - Gerenciamento de predicoes
    - Integracao com alertas
    - Analise de tendencias
    """
    
    def __init__(self):
        """Inicializa o handler de predicoes"""
        self.sagemaker_service = SageMakerService()
        self.timestream_service = TimestreamService()
        self.alert_service = AlertService()
        self.alert_handler = AlertHandler()
        self.prediction_cache: Dict[str, Prediction] = {}
    
    # ==================== Predicao de Falhas ====================
    
    def predict_failures(self, machine_id: str, device_id: Optional[str] = None) -> List[Prediction]:
        """Prediz falhas para uma maquina"""
        try:
            logger.info(f"Predizendo falhas para maquina {machine_id}")
            
            # Obter leituras recentes
            readings = self._get_recent_readings(machine_id, device_id)
            
            if not readings:
                logger.warning(f"Nenhuma leitura encontrada para maquina {machine_id}")
                return []
            
            # Obter dados historicos
            historical_data = self._get_historical_data(machine_id)
            
            # Executar predicao
            predictions = self.sagemaker_service.predict_failures(
                readings=readings,
                machine_id=machine_id,
                device_id=device_id or '',
                historical_data=historical_data
            )
            
            # Processar predicoes
            for prediction in predictions:
                self._process_prediction(prediction)
            
            logger.info(f"Predicoes de falhas para maquina {machine_id} concluidas")
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao prever falhas para maquina {machine_id}: {e}")
            return []
    
    def _get_recent_readings(self, machine_id: str, device_id: Optional[str] = None) -> List[Reading]:
        """Obtem leituras recentes para uma maquina ou dispositivo"""
        try:
            # Obter leituras das ultimas 24 horas
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            # Buscar no Timestream
            readings_data = self.timestream_service.query_machine_readings(
                machine_id=machine_id,
                start_time=start_time,
                end_time=end_time,
                limit=1000
            )
            
            # Converter para objetos Reading
            readings = []
            for data in readings_data:
                reading = self._parse_reading_from_data(data)
                if reading:
                    # Filtrar por dispositivo se especificado
                    if device_id is None or reading.metadata.device_id == device_id:
                        readings.append(reading)
            
            return readings
            
        except Exception as e:
            logger.error(f"Erro ao obter leituras recentes para maquina {machine_id}: {e}")
            return []
    
    def _parse_reading_from_data(self, data: Dict) -> Optional[Reading]:
        """Analisa uma leitura a partir de dados do Timestream"""
        try:
            from ..models.reading import ReadingMetadata, ReadingQuality
            
            metadata = ReadingMetadata(
                sensor_id=data.get('sensor_id', ''),
                device_id=data.get('device_id', ''),
                machine_id=data.get('machine_id', ''),
                timestamp=datetime.fromisoformat(data.get('time')) if data.get('time') else datetime.utcnow(),
                quality=ReadingQuality(data.get('quality', 'good')),
                confidence=data.get('confidence')
            )
            
            reading = Reading(
                id=data.get('id', f"reading-{datetime.utcnow().isoformat()}"),
                value=data.get('value', 0.0),
                unit=data.get('unit', ''),
                metadata=metadata,
                rms=data.get('rms'),
                peak=data.get('peak'),
                frequency=data.get('frequency'),
                is_anomaly=data.get('is_anomaly', False),
                anomaly_score=data.get('anomaly_score'),
                created_at=datetime.utcnow()
            )
            
            return reading
            
        except Exception as e:
            logger.error(f"Erro ao analisar leitura: {e}")
            return None
    
    def _get_historical_data(self, machine_id: str) -> List[Dict]:
        """Obtem dados historicos para uma maquina"""
        try:
            # Obter dados agregados das ultimas 30 dias
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)
            
            aggregated_data = self.timestream_service.query_aggregated_readings(
                machine_id=machine_id,
                start_time=start_time,
                end_time=end_time,
                aggregation='AVG',
                interval='1d'
            )
            
            return aggregated_data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados historicos para maquina {machine_id}: {e}")
            return []
    
    # ==================== Estimativa de Vida Util (RUL) ====================
    
    def predict_rul(self, machine_id: str, device_id: Optional[str] = None) -> List[Prediction]:
        """Prediz a vida util restante para uma maquina"""
        try:
            logger.info(f"Predizendo RUL para maquina {machine_id}")
            
            # Obter leituras recentes
            readings = self._get_recent_readings(machine_id, device_id)
            
            if not readings:
                logger.warning(f"Nenhuma leitura encontrada para maquina {machine_id}")
                return []
            
            # Obter dados historicos
            historical_data = self._get_historical_data(machine_id)
            
            # Executar predicao de RUL
            predictions = self.sagemaker_service.predict_rul(
                readings=readings,
                machine_id=machine_id,
                device_id=device_id or '',
                historical_data=historical_data
            )
            
            # Processar predicoes
            for prediction in predictions:
                self._process_prediction(prediction)
            
            logger.info(f"Predicoes de RUL para maquina {machine_id} concluidas")
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao prever RUL para maquina {machine_id}: {e}")
            return []
    
    # ==================== Detecao de Anomalias ====================
    
    def detect_anomalies(self, machine_id: str, device_id: Optional[str] = None) -> List[Prediction]:
        """Detecta anomalias para uma maquina"""
        try:
            logger.info(f"Detectando anomalias para maquina {machine_id}")
            
            # Obter leituras recentes
            readings = self._get_recent_readings(machine_id, device_id)
            
            if not readings:
                logger.warning(f"Nenhuma leitura encontrada para maquina {machine_id}")
                return []
            
            # Executar detecao de anomalias
            predictions = self.sagemaker_service.detect_anomalies(
                readings=readings,
                machine_id=machine_id,
                device_id=device_id or ''
            )
            
            # Processar predicoes
            for prediction in predictions:
                self._process_prediction(prediction)
            
            logger.info(f"Detecao de anomalias para maquina {machine_id} concluida")
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao detectar anomalias para maquina {machine_id}: {e}")
            return []
    
    # ==================== Processamento de Predicoes ====================
    
    def _process_prediction(self, prediction: Prediction) -> bool:
        """Processa uma predicao"""
        try:
            # Salvar predicao no cache
            self.prediction_cache[prediction.id] = prediction
            
            # Criar alerta se necessario
            if self._should_create_alert(prediction):
                alert = self.alert_handler.create_alert_from_prediction(prediction)
                if alert:
                    prediction.alert_ids = [alert.id]
            
            # Atualizar status da predicao
            prediction.status = PredictionStatus.COMPLETED
            
            logger.info(f"Predicao {prediction.id} processada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar predicao {prediction.id}: {e}")
            return False
    
    def _should_create_alert(self, prediction: Prediction) -> bool:
        """Determina se deve criar um alerta para a predicao"""
        # Criar alerta para predicoes criticas
        if prediction.failure_probability > 0.5:
            return True
        
        # Criar alerta para RUL baixo
        if prediction.remaining_useful_life is not None and prediction.remaining_useful_life < 30:
            return True
        
        # Criar alerta para anomalias
        if prediction.is_anomaly and prediction.anomaly_score > 0.7:
            return True
        
        return False
    
    # ==================== Gerenciamento de Predicoes ====================
    
    def create_prediction(self, prediction_data: Dict) -> Optional[Prediction]:
        """Cria uma nova predicao"""
        try:
            prediction = self._parse_prediction(prediction_data)
            if prediction is None:
                return None
            
            # Processar predicao
            self._process_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erro ao criar predicao: {e}")
            return None
    
    def get_prediction(self, prediction_id: str) -> Optional[Prediction]:
        """Obtem uma predicao pelo ID"""
        # Verificar cache
        if prediction_id in self.prediction_cache:
            return self.prediction_cache[prediction_id]
        
        # Em um sistema real, buscar no banco de dados
        return None
    
    def list_predictions(self, machine_id: Optional[str] = None, device_id: Optional[str] = None,
                        prediction_type: Optional[PredictionType] = None, 
                        status: Optional[PredictionStatus] = None, limit: int = 100) -> List[Prediction]:
        """Lista predicoes com filtros"""
        try:
            # Filtrar cache
            predictions = list(self.prediction_cache.values())
            
            if machine_id:
                predictions = [p for p in predictions if p.machine_id == machine_id]
            if device_id:
                predictions = [p for p in predictions if p.device_id == device_id]
            if prediction_type:
                predictions = [p for p in predictions if p.prediction_type == prediction_type]
            if status:
                predictions = [p for p in predictions if p.status == status]
            
            return predictions[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao listar predicoes: {e}")
            return []
    
    def update_prediction(self, prediction_id: str, update_data: Dict) -> Optional[Prediction]:
        """Atualiza uma predicao"""
        try:
            prediction = self.get_prediction(prediction_id)
            if prediction is None:
                return None
            
            # Aplicar atualizacoes
            if 'status' in update_data:
                prediction.status = PredictionStatus(update_data['status'])
            if 'failure_probability' in update_data:
                prediction.failure_probability = update_data['failure_probability']
            if 'remaining_useful_life' in update_data:
                prediction.remaining_useful_life = update_data['remaining_useful_life']
            if 'confidence' in update_data:
                prediction.confidence = update_data['confidence']
            if 'interpretation' in update_data:
                prediction.interpretation = update_data['interpretation']
            
            prediction.updated_at = datetime.utcnow()
            
            # Atualizar cache
            self.prediction_cache[prediction_id] = prediction
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erro ao atualizar predicao {prediction_id}: {e}")
            return None
    
    def delete_prediction(self, prediction_id: str) -> bool:
        """Remove uma predicao"""
        try:
            if prediction_id in self.prediction_cache:
                del self.prediction_cache[prediction_id]
            
            # Em um sistema real, remover do banco de dados
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover predicao {prediction_id}: {e}")
            return False
    
    def _parse_prediction(self, data: Dict) -> Optional[Prediction]:
        """Analisa uma predicao a partir de dados"""
        try:
            prediction = Prediction(
                id=data.get('id', f"prediction-{datetime.utcnow().isoformat()}"),
                prediction_type=PredictionType(data.get('prediction_type', 'failure_prediction')),
                status=PredictionStatus(data.get('status', 'pending')),
                device_id=data.get('device_id'),
                machine_id=data.get('machine_id'),
                sensor_ids=data.get('sensor_ids', []),
                prediction_timestamp=datetime.fromisoformat(data.get('prediction_timestamp'))
                    if data.get('prediction_timestamp') else datetime.utcnow(),
                predicted_value=data.get('predicted_value'),
                predicted_unit=data.get('predicted_unit'),
                predicted_failure_date=datetime.fromisoformat(data.get('predicted_failure_date'))
                    if data.get('predicted_failure_date') else None,
                failure_probability=data.get('failure_probability', 0.0),
                confidence=data.get('confidence', 0.0),
                remaining_useful_life=data.get('remaining_useful_life'),
                rul_confidence=data.get('rul_confidence'),
                is_anomaly=data.get('is_anomaly', False),
                anomaly_score=data.get('anomaly_score'),
                anomaly_type=data.get('anomaly_type'),
                model_name=data.get('model_name', ''),
                model_version=data.get('model_version', ''),
                model_accuracy=data.get('model_accuracy'),
                features=data.get('features', []),
                feature_values=data.get('feature_values', {}),
                interpretation=data.get('interpretation'),
                recommended_actions=data.get('recommended_actions', []),
                validated_by=data.get('validated_by'),
                validated_at=datetime.fromisoformat(data.get('validated_at'))
                    if data.get('validated_at') else None,
                validation_notes=data.get('validation_notes'),
                source=data.get('source', 'system'),
                tags=data.get('tags', []),
                error_message=data.get('error_message'),
                error_details=data.get('error_details'),
                prediction_id=data.get('prediction_id'),
                alert_ids=data.get('alert_ids', []),
                created_at=datetime.fromisoformat(data.get('created_at'))
                    if data.get('created_at') else datetime.utcnow(),
                updated_at=datetime.fromisoformat(data.get('updated_at'))
                    if data.get('updated_at') else datetime.utcnow()
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erro ao analisar predicao: {e}")
            return None
    
    # ==================== Analises ====================
    
    def get_failure_risk(self, machine_id: str) -> Dict:
        """Obtem o risco de falha para uma maquina"""
        try:
            # Obter predicoes recentes
            predictions = self.list_predictions(
                machine_id=machine_id,
                prediction_type=PredictionType.FAILURE_PREDICTION,
                limit=10
            )
            
            if not predictions:
                return {'risk_level': 'low', 'risk_score': 0.0}
            
            # Calcular score de risco
            risk_score = self._calculate_risk_score(predictions)
            
            # Determinar nivel de risco
            risk_level = self._get_risk_level(risk_score)
            
            # Obter predicao mais recente
            latest_prediction = max(predictions, key=lambda p: p.prediction_timestamp)
            
            return {
                'machine_id': machine_id,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'failure_probability': latest_prediction.failure_probability,
                'predicted_failure_date': latest_prediction.predicted_failure_date.isoformat()
                    if latest_prediction.predicted_failure_date else None,
                'remaining_days': latest_prediction.get_days_until_failure(),
                'confidence': latest_prediction.confidence,
                'last_prediction': latest_prediction.prediction_timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular risco de falha para maquina {machine_id}: {e}")
            return {'risk_level': 'unknown', 'risk_score': 0.0}
    
    def _calculate_risk_score(self, predictions: List[Prediction]) -> float:
        """Calcula o score de risco com base em predicoes"""
        if not predictions:
            return 0.0
        
        # Calcular media ponderada das probabilidades de falha
        total_weight = 0
        weighted_sum = 0
        
        for prediction in predictions:
            # Peso com base na confiança e recencia
            age_hours = (datetime.utcnow() - prediction.prediction_timestamp).total_seconds() / 3600
            recency_weight = max(0, 1 - age_hours / 24)  # Peso decai em 24 horas
            confidence_weight = prediction.confidence
            
            weight = recency_weight * confidence_weight
            weighted_sum += prediction.failure_probability * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(weighted_sum / total_weight, 1.0)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Determina o nivel de risco com base no score"""
        if risk_score >= 0.8:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        elif risk_score >= 0.2:
            return 'low'
        else:
            return 'minimal'
    
    def get_rul_estimate(self, machine_id: str) -> Dict:
        """Obtem a estimativa de vida util restante para uma maquina"""
        try:
            # Obter predicoes de RUL
            predictions = self.list_predictions(
                machine_id=machine_id,
                prediction_type=PredictionType.REMAINING_USEFUL_LIFE,
                limit=10
            )
            
            if not predictions:
                return {'rul_days': None, 'confidence': 0.0}
            
            # Obter predicao mais recente
            latest_prediction = max(predictions, key=lambda p: p.prediction_timestamp)
            
            return {
                'machine_id': machine_id,
                'rul_days': latest_prediction.remaining_useful_life,
                'confidence': latest_prediction.rul_confidence or latest_prediction.confidence,
                'last_prediction': latest_prediction.prediction_timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estimativa de RUL para maquina {machine_id}: {e}")
            return {'rul_days': None, 'confidence': 0.0}
    
    def get_maintenance_recommendations(self, machine_id: str) -> List[Dict]:
        """Obtem recomendacoes de manutencao para uma maquina"""
        try:
            # Obter predicoes recentes
            predictions = self.list_predictions(
                machine_id=machine_id,
                limit=20
            )
            
            # Agrupar recomendacoes
            recommendations = {}
            for prediction in predictions:
                for action in prediction.recommended_actions:
                    if action not in recommendations:
                        recommendations[action] = {
                            'action': action,
                            'count': 0,
                            'predictions': []
                        }
                    recommendations[action]['count'] += 1
                    recommendations[action]['predictions'].append(prediction.id)
            
            # Ordenar por contagem
            sorted_recommendations = sorted(
                recommendations.values(),
                key=lambda r: r['count'],
                reverse=True
            )
            
            # Formatar resultado
            result = []
            for rec in sorted_recommendations:
                result.append({
                    'action': rec['action'],
                    'priority': self._get_recommendation_priority(rec['count']),
                    'count': rec['count'],
                    'prediction_ids': rec['predictions']
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter recomendacoes de manutencao para maquina {machine_id}: {e}")
            return []
    
    def _get_recommendation_priority(self, count: int) -> str:
        """Determina a prioridade de uma recomendacao com base na contagem"""
        if count >= 5:
            return 'critical'
        elif count >= 3:
            return 'high'
        elif count >= 2:
            return 'medium'
        else:
            return 'low'
    
    # ==================== Agendamento ====================
    
    def schedule_predictions(self, machine_id: str, frequency: str = 'daily') -> bool:
        """Agenda predicoes para uma maquina"""
        try:
            # Em um sistema real, isso criaria um agendamento no EventBridge ou CloudWatch Events
            logger.info(f"Agendando predicoes {frequency} para maquina {machine_id}")
            
            # Para demonstracao, executar predicoes agora
            if frequency == 'immediate':
                self.predict_failures(machine_id)
                self.predict_rul(machine_id)
                self.detect_anomalies(machine_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao agendar predicoes para maquina {machine_id}: {e}")
            return False
    
    def run_scheduled_predictions(self) -> bool:
        """Executa predicoes agendadas para todas as maquinas"""
        try:
            # Em um sistema real, isso seria chamado por um trigger agendado
            logger.info("Executando predicoes agendadas")
            
            # Obter lista de maquinas (simplificado)
            # Para demonstracao, usar maquinas conhecidas
            machine_ids = ['machine-001', 'machine-002', 'machine-003']
            
            for machine_id in machine_ids:
                self.predict_failures(machine_id)
                self.predict_rul(machine_id)
                self.detect_anomalies(machine_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar predicoes agendadas: {e}")
            return False
    
    # ==================== Monitoramento ====================
    
    def get_prediction_metrics(self) -> Dict:
        """Obtem metricas de predicoes"""
        try:
            predictions = list(self.prediction_cache.values())
            
            # Contar por tipo
            type_counts = {}
            for prediction_type in PredictionType:
                type_counts[prediction_type.value] = sum(
                    1 for p in predictions if p.prediction_type == prediction_type
                )
            
            # Contar por status
            status_counts = {}
            for status in PredictionStatus:
                status_counts[status.value] = sum(
                    1 for p in predictions if p.status == status
                )
            
            # Contar por maquina
            machine_counts = {}
            for p in predictions:
                if p.machine_id:
                    machine_counts[p.machine_id] = machine_counts.get(p.machine_id, 0) + 1
            
            # Predicoes criticas
            critical_predictions = sum(
                1 for p in predictions 
                if p.failure_probability > 0.7 or (p.remaining_useful_life is not None and p.remaining_useful_life < 30)
            )
            
            return {
                'total_predictions': len(predictions),
                'by_type': type_counts,
                'by_status': status_counts,
                'by_machine': machine_counts,
                'critical_predictions': critical_predictions,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter metricas de predicoes: {e}")
            return {}
    
    def get_prediction_summary(self, machine_id: str) -> Dict:
        """Obtem um resumo das predicoes para uma maquina"""
        try:
            predictions = self.list_predictions(machine_id=machine_id, limit=50)
            
            if not predictions:
                return {
                    'machine_id': machine_id,
                    'total_predictions': 0
                }
            
            # Obter predicao mais recente de cada tipo
            latest_predictions = {}
            for prediction in predictions:
                if prediction.prediction_type not in latest_predictions:
                    latest_predictions[prediction.prediction_type] = prediction
                else:
                    if prediction.prediction_timestamp > latest_predictions[prediction.prediction_type].prediction_timestamp:
                        latest_predictions[prediction.prediction_type] = prediction
            
            # Formatar resultado
            result = {
                'machine_id': machine_id,
                'total_predictions': len(predictions),
                'latest_predictions': {}
            }
            
            for pred_type, prediction in latest_predictions.items():
                result['latest_predictions'][pred_type.value] = {
                    'prediction_id': prediction.id,
                    'timestamp': prediction.prediction_timestamp.isoformat(),
                    'status': prediction.status.value,
                    'failure_probability': prediction.failure_probability,
                    'remaining_useful_life': prediction.remaining_useful_life,
                    'confidence': prediction.confidence
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de predicoes para maquina {machine_id}: {e}")
            return {}
