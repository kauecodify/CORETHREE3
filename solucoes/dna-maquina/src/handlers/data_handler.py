"""
CORETHREE3 - DNA de Maquinas
Handler de Dados

Handler para processamento e armazenamento de dados de sensores.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..config.timestream_config import timestream_config
from ..models.reading import Reading, ReadingBatch, ReadingMetadata, ReadingQuality
from ..models.sensor import SensorType
from ..models.alert import Alert, AlertSeverity, AlertType
from ..services.timestream_service import TimestreamService
from ..services.alert_service import AlertService
from ..services.sagemaker_service import SageMakerService

logger = logging.getLogger(__name__)


class DataHandler:
    """
    Handler de Dados para processamento de leituras de sensores.
    
    Responsabilidades:
    - Processamento de leituras individuais e batches
    - Armazenamento no Timestream
    - Detecao de anomalias e thresholds
    - Geracao de alertas
    - Pre-processamento para ML
    """
    
    def __init__(self):
        """Inicializa o handler de dados"""
        self.timestream_service = TimestreamService()
        self.alert_service = AlertService()
        self.sagemaker_service = SageMakerService()
        self.sensor_thresholds: Dict[str, Dict] = {}
    
    # ==================== Processamento de Leituras ====================
    
    def process_reading(self, reading: Reading) -> bool:
        """Processa uma leitura individual"""
        try:
            logger.info(f"Processando leitura {reading.id}")
            
            # Validar leitura
            if not self._validate_reading(reading):
                logger.warning(f"Leitura invalida: {reading.id}")
                return False
            
            # Verificar qualidade
            if not self._check_quality(reading):
                logger.warning(f"Leitura com qualidade ruim: {reading.id}")
                # Armazenar mesmo assim para auditoria
                self._store_reading(reading)
                return True
            
            # Verificar thresholds
            alert = self._check_thresholds(reading)
            if alert:
                logger.info(f"Threshold violado - Alerta criado: {alert.id}")
            
            # Verificar anomalias
            is_anomaly = self._check_anomalies(reading)
            if is_anomaly:
                reading.is_anomaly = True
                logger.info(f"Anomalia detectada na leitura: {reading.id}")
                
                # Criar alerta de anomalia
                anomaly_alert = self._create_anomaly_alert(reading)
                if anomaly_alert:
                    logger.info(f"Alerta de anomalia criado: {anomaly_alert.id}")
            
            # Armazenar leitura
            self._store_reading(reading)
            
            # Atualizar cache de thresholds
            self._update_threshold_cache(reading)
            
            logger.info(f"Leitura {reading.id} processada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar leitura {reading.id}: {e}")
            return False
    
    def process_reading_batch(self, batch: ReadingBatch) -> bool:
        """Processa um batch de leituras"""
        try:
            logger.info(f"Processando batch {batch.id} com {len(batch.readings)} leituras")
            
            success_count = 0
            
            # Processar cada leitura individualmente
            for reading in batch.readings:
                if self.process_reading(reading):
                    success_count += 1
            
            # Atualizar status do batch
            batch.is_processed = True
            batch.processed_at = datetime.utcnow()
            
            # Armazenar batch
            self._store_reading_batch(batch)
            
            logger.info(f"Batch {batch.id} processado - {success_count}/{len(batch.readings)} leituras com sucesso")
            return success_count == len(batch.readings)
            
        except Exception as e:
            logger.error(f"Erro ao processar batch {batch.id}: {e}")
            return False
    
    # ==================== Validacao ====================
    
    def _validate_reading(self, reading: Reading) -> bool:
        """Valida uma leitura"""
        if reading.value is None:
            return False
        if reading.metadata.sensor_id is None or reading.metadata.sensor_id == '':
            return False
        if reading.metadata.timestamp is None:
            return False
        
        # Verificar se o valor esta dentro dos limites
        sensor_type = self._get_sensor_type(reading.metadata.sensor_id)
        thresholds = self._get_sensor_thresholds(sensor_type)
        
        if thresholds:
            min_val = thresholds.get('min_value')
            max_val = thresholds.get('max_value')
            
            if min_val is not None and reading.value < min_val:
                return False
            if max_val is not None and reading.value > max_val:
                return False
        
        return True
    
    def _check_quality(self, reading: Reading) -> bool:
        """Verifica a qualidade da leitura"""
        if reading.metadata.quality == ReadingQuality.INVALID:
            return False
        
        # Verificar confiança
        if reading.metadata.confidence is not None and reading.metadata.confidence < 0.5:
            return False
        
        return True
    
    # ==================== Thresholds ====================
    
    def _check_thresholds(self, reading: Reading) -> Optional[Alert]:
        """Verifica se a leitura violou algum threshold"""
        try:
            sensor_type = self._get_sensor_type(reading.metadata.sensor_id)
            thresholds = self._get_sensor_thresholds(sensor_type)
            
            if not thresholds:
                return None
            
            # Verificar thresholds
            if reading.value >= thresholds.get('threshold_critical', float('inf')):
                return self._create_threshold_alert(reading, 'critical', AlertSeverity.CRITICAL)
            elif reading.value >= thresholds.get('threshold_high', float('inf')):
                return self._create_threshold_alert(reading, 'high', AlertSeverity.HIGH)
            elif reading.value >= thresholds.get('threshold_medium', float('inf')):
                return self._create_threshold_alert(reading, 'medium', AlertSeverity.MEDIUM)
            elif reading.value <= thresholds.get('threshold_low', float('-inf')):
                return self._create_threshold_alert(reading, 'low', AlertSeverity.MEDIUM)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao verificar thresholds para leitura {reading.id}: {e}")
            return None
    
    def _create_threshold_alert(self, reading: Reading, threshold_type: str, severity: AlertSeverity) -> Optional[Alert]:
        """Cria um alerta de threshold"""
        try:
            sensor_type = self._get_sensor_type(reading.metadata.sensor_id)
            thresholds = self._get_sensor_thresholds(sensor_type)
            
            threshold_value = thresholds.get(f'threshold_{threshold_type}')
            
            alert = self.alert_service.create_alert_from_reading(
                reading=reading,
                threshold=threshold_value or 0,
                threshold_type=threshold_type,
                severity=severity
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta de threshold: {e}")
            return None
    
    # ==================== Detecao de Anomalias ====================
    
    def _check_anomalies(self, reading: Reading) -> bool:
        """Verifica se a leitura e uma anomalia"""
        try:
            # Usar SageMaker para detecao de anomalias
            # Para simplificacao, usar metodo local
            
            sensor_type = self._get_sensor_type(reading.metadata.sensor_id)
            
            # Obter dados historicos para contexto
            historical_data = self._get_historical_data(
                reading.metadata.sensor_id,
                datetime.utcnow() - timedelta(hours=1),
                datetime.utcnow()
            )
            
            # Detectar anomalia usando SageMaker
            if historical_data:
                # Criar uma lista de leituras para o modelo
                readings_for_detection = [reading]
                
                predictions = self.sagemaker_service.detect_anomalies(
                    readings=readings_for_detection,
                    machine_id=reading.metadata.machine_id or '',
                    device_id=reading.metadata.device_id or ''
                )
                
                if predictions and predictions[0].is_anomaly:
                    reading.anomaly_score = predictions[0].anomaly_score
                    return True
            
            # Metodo de detecao local (simplificado)
            # Verificar se o valor esta muito longe da media historica
            if historical_data:
                values = [d.get('value', 0) for d in historical_data if 'value' in d]
                if values:
                    mean = sum(values) / len(values)
                    std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
                    
                    # Se o valor esta a mais de 3 desvios padrao da media
                    if abs(reading.value - mean) > 3 * std:
                        reading.anomaly_score = min(abs(reading.value - mean) / (std + 0.001), 1.0)
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao detectar anomalias: {e}")
            return False
    
    def _create_anomaly_alert(self, reading: Reading) -> Optional[Alert]:
        """Cria um alerta de anomalia"""
        try:
            alert = Alert(
                id=f"alert-anomaly-{reading.id}",
                alert_type=AlertType.ANOMALY,
                severity=AlertSeverity.HIGH if reading.anomaly_score > 0.8 else AlertSeverity.MEDIUM,
                status=AlertStatus.ACTIVE,
                title=f"Anomalia detectada em {reading.metadata.sensor_id}",
                description=f"Sensor {reading.metadata.sensor_id} detectou valor anormal: {reading.value} {reading.unit} (score: {reading.anomaly_score:.2f})",
                machine_id=reading.metadata.machine_id,
                device_id=reading.metadata.device_id,
                sensor_id=reading.metadata.sensor_id,
                reading_id=reading.id,
                value=reading.value,
                unit=reading.unit,
                anomaly_score=reading.anomaly_score,
                triggered_at=datetime.utcnow(),
                sla_response_time=30 if reading.anomaly_score > 0.8 else 60,
                sla_resolution_time=120 if reading.anomaly_score > 0.8 else 240,
                recommended_actions=[
                    "Verificar sensor e equipamento",
                    "Coletar mais dados para analise",
                    "Avaliar necessidade de manutencao"
                ],
                notification_channels=['email', 'sms'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.alert_service.create_alert(alert)
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta de anomalia: {e}")
            return None
    
    # ==================== Armazenamento ====================
    
    def _store_reading(self, reading: Reading) -> bool:
        """Armazena uma leitura no Timestream"""
        try:
            return self.timestream_service.write_reading(reading)
            
        except Exception as e:
            logger.error(f"Erro ao armazenar leitura {reading.id}: {e}")
            return False
    
    def _store_reading_batch(self, batch: ReadingBatch) -> bool:
        """Armazena um batch de leituras no Timestream"""
        try:
            return self.timestream_service.write_reading_batch(batch)
            
        except Exception as e:
            logger.error(f"Erro ao armazenar batch {batch.id}: {e}")
            return False
    
    # ==================== Dados Historicos ====================
    
    def _get_historical_data(self, sensor_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Obtem dados historicos de um sensor"""
        try:
            readings = self.timestream_service.query_readings(
                sensor_id=sensor_id,
                start_time=start_time,
                end_time=end_time,
                limit=1000
            )
            
            return readings
            
        except Exception as e:
            logger.error(f"Erro ao obter dados historicos para sensor {sensor_id}: {e}")
            return []
    
    def get_readings(self, sensor_id: Optional[str] = None, machine_id: Optional[str] = None,
                     start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                     limit: int = 100) -> List[Dict]:
        """Obtem leituras com filtros"""
        try:
            if sensor_id:
                if start_time and end_time:
                    return self.timestream_service.query_readings(
                        sensor_id=sensor_id,
                        start_time=start_time,
                        end_time=end_time,
                        limit=limit
                    )
                else:
                    # Obter ultimas leituras
                    return self.timestream_service.query_readings(
                        sensor_id=sensor_id,
                        start_time=datetime.utcnow() - timedelta(days=1),
                        end_time=datetime.utcnow(),
                        limit=limit
                    )
            elif machine_id:
                if start_time and end_time:
                    return self.timestream_service.query_machine_readings(
                        machine_id=machine_id,
                        start_time=start_time,
                        end_time=end_time,
                        limit=limit
                    )
                else:
                    return self.timestream_service.query_machine_readings(
                        machine_id=machine_id,
                        start_time=datetime.utcnow() - timedelta(days=1),
                        end_time=datetime.utcnow(),
                        limit=limit
                    )
            else:
                return []
            
        except Exception as e:
            logger.error(f"Erro ao obter leituras: {e}")
            return []
    
    def get_aggregated_readings(self, machine_id: str, start_time: datetime, end_time: datetime,
                               aggregation: str = 'AVG', interval: str = '1h') -> List[Dict]:
        """Obtem leituras agregadas de uma maquina"""
        try:
            return self.timestream_service.query_aggregated_readings(
                machine_id=machine_id,
                start_time=start_time,
                end_time=end_time,
                aggregation=aggregation,
                interval=interval
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter leituras agregadas: {e}")
            return []
    
    # ==================== Utilitarios ====================
    
    def _get_sensor_type(self, sensor_id: str) -> str:
        """Obtem o tipo do sensor a partir do ID"""
        if '-' in sensor_id:
            return sensor_id.split('-')[0]
        return 'vibration'
    
    def _get_sensor_thresholds(self, sensor_type: str) -> Dict:
        """Obtem os thresholds para um tipo de sensor"""
        # Verificar cache
        if sensor_type in self.sensor_thresholds:
            return self.sensor_thresholds[sensor_type]
        
        # Thresholds padrao
        thresholds = {
            'vibration': {
                'min_value': -10,
                'max_value': 10,
                'threshold_critical': 8.0,
                'threshold_high': 5.0,
                'threshold_medium': 3.0,
                'threshold_low': 1.0
            },
            'temperature': {
                'min_value': -50,
                'max_value': 200,
                'threshold_critical': 150,
                'threshold_high': 120,
                'threshold_medium': 100,
                'threshold_low': 50
            },
            'pressure': {
                'min_value': 0,
                'max_value': 1000,
                'threshold_critical': 900,
                'threshold_high': 800,
                'threshold_medium': 700,
                'threshold_low': 100
            },
            'current': {
                'min_value': 0,
                'max_value': 1000,
                'threshold_critical': 950,
                'threshold_high': 900,
                'threshold_medium': 850,
                'threshold_low': 100
            },
            'voltage': {
                'min_value': 0,
                'max_value': 1000,
                'threshold_critical': 950,
                'threshold_high': 900,
                'threshold_medium': 850,
                'threshold_low': 100
            },
            'humidity': {
                'min_value': 0,
                'max_value': 100,
                'threshold_critical': 90,
                'threshold_high': 80,
                'threshold_medium': 70,
                'threshold_low': 30
            }
        }
        
        return thresholds.get(sensor_type, thresholds['vibration'])
    
    def _update_threshold_cache(self, reading: Reading) -> None:
        """Atualiza o cache de thresholds"""
        sensor_type = self._get_sensor_type(reading.metadata.sensor_id)
        if sensor_type not in self.sensor_thresholds:
            self.sensor_thresholds[sensor_type] = self._get_sensor_thresholds(sensor_type)
    
    # ==================== Analises ====================
    
    def get_sensor_statistics(self, sensor_id: str, start_time: datetime, end_time: datetime) -> Dict:
        """Obtem estatisticas de um sensor"""
        try:
            readings = self._get_historical_data(sensor_id, start_time, end_time)
            
            if not readings:
                return {}
            
            values = [r.get('value', 0) for r in readings if 'value' in r]
            
            if not values:
                return {}
            
            return {
                'sensor_id': sensor_id,
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': sum(values) / len(values),
                'std': (sum((v - sum(values) / len(values)) ** 2 for v in values) / len(values)) ** 0.5,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatisticas para sensor {sensor_id}: {e}")
            return {}
    
    def get_machine_health_score(self, machine_id: str, start_time: datetime, end_time: datetime) -> float:
        """Calcula o score de saude de uma maquina"""
        try:
            # Obter leituras agregadas
            aggregated = self.get_aggregated_readings(
                machine_id=machine_id,
                start_time=start_time,
                end_time=end_time,
                aggregation='AVG',
                interval='1h'
            )
            
            if not aggregated:
                return 100.0
            
            # Calcular score com base em thresholds
            score = 100.0
            
            for data in aggregated:
                sensor_type = data.get('sensor_type', '')
                value = data.get('value', 0)
                
                thresholds = self._get_sensor_thresholds(sensor_type)
                
                # Penalizar por valores altos
                if value >= thresholds.get('threshold_critical', float('inf')):
                    score -= 40
                elif value >= thresholds.get('threshold_high', float('inf')):
                    score -= 20
                elif value >= thresholds.get('threshold_medium', float('inf')):
                    score -= 10
                
                # Penalizar por valores baixos
                if value <= thresholds.get('threshold_low', float('-inf')):
                    score -= 10
            
            # Verificar alertas ativos
            active_alerts = self.alert_service.list_alerts(
                machine_id=machine_id,
                status='active'
            )
            
            score -= len(active_alerts) * 5
            
            # Garantir que o score esta entre 0 e 100
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de saude para maquina {machine_id}: {e}")
            return 100.0
    
    def detect_trends(self, sensor_id: str, start_time: datetime, end_time: datetime) -> Dict:
        """Detecta tendencias em dados de sensor"""
        try:
            readings = self._get_historical_data(sensor_id, start_time, end_time)
            
            if not readings or len(readings) < 2:
                return {'trend': 'stable', 'slope': 0.0}
            
            # Extrair valores e timestamps
            values = [r.get('value', 0) for r in readings if 'value' in r]
            timestamps = [r.get('timestamp', '') for r in readings if 'timestamp' in r]
            
            if len(values) < 2:
                return {'trend': 'stable', 'slope': 0.0}
            
            # Calcular tendencia (regressao linear simples)
            x = list(range(len(values)))
            y = values
            
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi ** 2 for xi in x)
            
            # Calcular inclinação (slope)
            numerator = n * sum_xy - sum_x * sum_y
            denominator = n * sum_x2 - sum_x ** 2
            
            if denominator == 0:
                slope = 0.0
            else:
                slope = numerator / denominator
            
            # Determinar tendencia
            if slope > 0.1:
                trend = 'increasing'
            elif slope < -0.1:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'sensor_id': sensor_id,
                'trend': trend,
                'slope': float(slope),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'data_points': len(values)
            }
            
        except Exception as e:
            logger.error(f"Erro ao detectar tendencias para sensor {sensor_id}: {e}")
            return {'trend': 'error', 'slope': 0.0}
