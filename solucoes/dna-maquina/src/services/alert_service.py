"""
CORETHREE3 - DNA de Maquinas
Servico de Alertas

Servico para gerenciamento de alertas do sistema DNA de Maquinas.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import ClientError

from ..config.aws_config import aws_config
from ..config.iot_config import iot_config
from ..models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from ..models.reading import Reading
from ..models.sensor import SensorType

logger = logging.getLogger(__name__)


class AlertService:
    """
    Servico de Alertas para gerenciamento de notificacoes e alertas.
    
    Responsabilidades:
    - Criacao e gerenciamento de alertas
    - Notificacao via SNS, Email, SMS
    - Escalonamento de alertas
    - Gerenciamento de SLA
    """
    
    def __init__(self):
        """Inicializa o servico de alertas"""
        self.sns_client = None
        self.dynamodb_client = None
        self._initialize_clients()
        self.alert_cache: Dict[str, Alert] = {}
    
    def _initialize_clients(self):
        """Inicializa os clientes AWS"""
        try:
            self.sns_client = boto3.client(
                'sns',
                region_name=aws_config.REGION,
                aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY
            )
            
            self.dynamodb_client = boto3.client(
                'dynamodb',
                region_name=aws_config.REGION,
                aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY
            )
            
            logger.info("Clientes AWS SNS e DynamoDB inicializados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar clientes AWS: {e}")
            raise
    
    def get_sns_client(self):
        """Retorna o cliente SNS"""
        if self.sns_client is None:
            self._initialize_clients()
        return self.sns_client
    
    def get_dynamodb_client(self):
        """Retorna o cliente DynamoDB"""
        if self.dynamodb_client is None:
            self._initialize_clients()
        return self.dynamodb_client
    
    # ==================== Gerenciamento de Alertas ====================
    
    def create_alert(self, alert: Alert) -> Alert:
        """Cria um novo alerta"""
        try:
            # Validar alerta
            if not self._validate_alert(alert):
                raise ValueError("Alerta invalido")
            
            # Salvar no DynamoDB
            if not self._save_alert_to_dynamodb(alert):
                raise Exception("Falha ao salvar alerta no DynamoDB")
            
            # Cache
            self.alert_cache[alert.id] = alert
            
            # Publicar no SNS
            self._publish_alert_to_sns(alert)
            
            # Publicar no MQTT
            self._publish_alert_to_mqtt(alert)
            
            logger.info(f"Alerta {alert.id} criado com sucesso")
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta {alert.id}: {e}")
            raise
    
    def _validate_alert(self, alert: Alert) -> bool:
        """Valida um alerta"""
        if not alert.id:
            return False
        if not alert.title:
            return False
        if not alert.alert_type:
            return False
        if not alert.severity:
            return False
        return True
    
    def _save_alert_to_dynamodb(self, alert: Alert) -> bool:
        """Salva alerta no DynamoDB"""
        try:
            table_name = aws_config.DYNAMODB_TABLES.get('alerts', 'corethree3-alerts')
            
            item = {
                'id': {'S': alert.id},
                'alert_type': {'S': alert.alert_type.value},
                'severity': {'S': alert.severity.value},
                'status': {'S': alert.status.value},
                'title': {'S': alert.title},
                'description': {'S': alert.description},
                'machine_id': {'S': alert.machine_id or ''},
                'device_id': {'S': alert.device_id or ''},
                'sensor_id': {'S': alert.sensor_id or ''},
                'value': {'N': str(alert.value or 0)},
                'unit': {'S': alert.unit or ''},
                'threshold': {'N': str(alert.threshold or 0)},
                'threshold_type': {'S': alert.threshold_type or ''},
                'triggered_at': {'S': alert.triggered_at.isoformat()},
                'failure_probability': {'N': str(alert.failure_probability or 0)},
                'anomaly_score': {'N': str(alert.anomaly_score or 0)},
                'created_at': {'S': alert.created_at.isoformat()},
                'updated_at': {'S': alert.updated_at.isoformat()}
            }
            
            # Adicionar campos opcionais
            if alert.acknowledged_at:
                item['acknowledged_at'] = {'S': alert.acknowledged_at.isoformat()}
            if alert.acknowledged_by:
                item['acknowledged_by'] = {'S': alert.acknowledged_by}
            if alert.resolved_at:
                item['resolved_at'] = {'S': alert.resolved_at.isoformat()}
            if alert.resolved_by:
                item['resolved_by'] = {'S': alert.resolved_by}
            if alert.prediction_id:
                item['prediction_id'] = {'S': alert.prediction_id}
            
            self.get_dynamodb_client().put_item(
                TableName=table_name,
                Item=item
            )
            
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao salvar alerta no DynamoDB: {e}")
            return False
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Obtem um alerta pelo ID"""
        # Verificar cache
        if alert_id in self.alert_cache:
            return self.alert_cache[alert_id]
        
        try:
            table_name = aws_config.DYNAMODB_TABLES.get('alerts', 'corethree3-alerts')
            
            response = self.get_dynamodb_client().get_item(
                TableName=table_name,
                Key={'id': {'S': alert_id}}
            )
            
            if 'Item' not in response:
                return None
            
            alert = self._parse_alert_from_dynamodb(response['Item'])
            
            # Cache
            self.alert_cache[alert_id] = alert
            
            return alert
            
        except ClientError as e:
            logger.error(f"Erro ao obter alerta {alert_id}: {e}")
            return None
    
    def _parse_alert_from_dynamodb(self, item: Dict) -> Alert:
        """Analisa um alerta do DynamoDB"""
        return Alert(
            id=item.get('id', {}).get('S'),
            alert_type=AlertType(item.get('alert_type', {}).get('S', 'anomaly')),
            severity=AlertSeverity(item.get('severity', {}).get('S', 'medium')),
            status=AlertStatus(item.get('status', {}).get('S', 'active')),
            title=item.get('title', {}).get('S', ''),
            description=item.get('description', {}).get('S', ''),
            machine_id=item.get('machine_id', {}).get('S'),
            device_id=item.get('device_id', {}).get('S'),
            sensor_id=item.get('sensor_id', {}).get('S'),
            value=float(item.get('value', {}).get('N', 0)),
            unit=item.get('unit', {}).get('S'),
            threshold=float(item.get('threshold', {}).get('N', 0)),
            threshold_type=item.get('threshold_type', {}).get('S'),
            triggered_at=datetime.fromisoformat(item.get('triggered_at', {}).get('S'))
                if item.get('triggered_at', {}).get('S') else datetime.utcnow(),
            acknowledged_at=datetime.fromisoformat(item.get('acknowledged_at', {}).get('S'))
                if item.get('acknowledged_at', {}).get('S') else None,
            acknowledged_by=item.get('acknowledged_by', {}).get('S'),
            resolved_at=datetime.fromisoformat(item.get('resolved_at', {}).get('S'))
                if item.get('resolved_at', {}).get('S') else None,
            resolved_by=item.get('resolved_by', {}).get('S'),
            failure_probability=float(item.get('failure_probability', {}).get('N', 0)),
            anomaly_score=float(item.get('anomaly_score', {}).get('N', 0)),
            prediction_id=item.get('prediction_id', {}).get('S'),
            recommended_actions=item.get('recommended_actions', {}).get('SS', []),
            notification_channels=item.get('notification_channels', {}).get('SS', []),
            notified_users=item.get('notified_users', {}).get('SS', []),
            sla_response_time=int(item.get('sla_response_time', {}).get('N', 0)),
            sla_resolution_time=int(item.get('sla_resolution_time', {}).get('N', 0)),
            tags=item.get('tags', {}).get('SS', []),
            created_at=datetime.fromisoformat(item.get('created_at', {}).get('S'))
                if item.get('created_at', {}).get('S') else datetime.utcnow(),
            updated_at=datetime.fromisoformat(item.get('updated_at', {}).get('S'))
                if item.get('updated_at', {}).get('S') else datetime.utcnow()
        )
    
    def list_alerts(self, machine_id: Optional[str] = None, device_id: Optional[str] = None,
                   severity: Optional[AlertSeverity] = None, status: Optional[AlertStatus] = None,
                   limit: int = 100) -> List[Alert]:
        """Lista alertas com filtros"""
        try:
            table_name = aws_config.DYNAMODB_TABLES.get('alerts', 'corethree3-alerts')
            
            # Construir expressao de filtro
            filter_expression = None
            expression_attribute_values = {}
            
            if machine_id:
                filter_expression = "machine_id = :machine_id"
                expression_attribute_values[':machine_id'] = {'S': machine_id}
            
            if device_id:
                device_filter = "device_id = :device_id"
                expression_attribute_values[':device_id'] = {'S': device_id}
                filter_expression = device_filter if filter_expression is None else f"{filter_expression} AND {device_filter}"
            
            if severity:
                severity_filter = "severity = :severity"
                expression_attribute_values[':severity'] = {'S': severity.value}
                filter_expression = severity_filter if filter_expression is None else f"{filter_expression} AND {severity_filter}"
            
            if status:
                status_filter = "status = :status"
                expression_attribute_values[':status'] = {'S': status.value}
                filter_expression = status_filter if filter_expression is None else f"{filter_expression} AND {status_filter}"
            
            # Executar scan
            if filter_expression:
                response = self.get_dynamodb_client().scan(
                    TableName=table_name,
                    FilterExpression=filter_expression,
                    ExpressionAttributeValues=expression_attribute_values,
                    Limit=limit
                )
            else:
                response = self.get_dynamodb_client().scan(
                    TableName=table_name,
                    Limit=limit
                )
            
            alerts = []
            for item in response.get('Items', []):
                alert = self._parse_alert_from_dynamodb(item)
                alerts.append(alert)
            
            return alerts
            
        except ClientError as e:
            logger.error(f"Erro ao listar alertas: {e}")
            return []
    
    def update_alert(self, alert: Alert) -> Alert:
        """Atualiza um alerta"""
        try:
            # Salvar no DynamoDB
            if not self._save_alert_to_dynamodb(alert):
                raise Exception("Falha ao atualizar alerta no DynamoDB")
            
            # Cache
            self.alert_cache[alert.id] = alert
            
            # Publicar atualizacao no SNS
            self._publish_alert_update_to_sns(alert)
            
            logger.info(f"Alerta {alert.id} atualizado com sucesso")
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao atualizar alerta {alert.id}: {e}")
            raise
    
    def delete_alert(self, alert_id: str) -> bool:
        """Remove um alerta"""
        try:
            table_name = aws_config.DYNAMODB_TABLES.get('alerts', 'corethree3-alerts')
            
            self.get_dynamodb_client().delete_item(
                TableName=table_name,
                Key={'id': {'S': alert_id}}
            )
            
            # Remover do cache
            if alert_id in self.alert_cache:
                del self.alert_cache[alert_id]
            
            logger.info(f"Alerta {alert_id} removido com sucesso")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao remover alerta {alert_id}: {e}")
            return False
    
    # ==================== Acoes de Alerta ====================
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Reconhece um alerta"""
        try:
            alert = self.get_alert(alert_id)
            if alert is None:
                return False
            
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            alert.updated_at = datetime.utcnow()
            
            self.update_alert(alert)
            
            logger.info(f"Alerta {alert_id} reconhecido por {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reconhecer alerta {alert_id}: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, user_id: str, notes: Optional[str] = None) -> bool:
        """Resolve um alerta"""
        try:
            alert = self.get_alert(alert_id)
            if alert is None:
                return False
            
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_id
            alert.updated_at = datetime.utcnow()
            
            if notes:
                alert.notes = notes
            
            self.update_alert(alert)
            
            logger.info(f"Alerta {alert_id} resolvido por {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao resolver alerta {alert_id}: {e}")
            return False
    
    def close_alert(self, alert_id: str, user_id: str, notes: Optional[str] = None) -> bool:
        """Fecha um alerta"""
        try:
            alert = self.get_alert(alert_id)
            if alert is None:
                return False
            
            alert.status = AlertStatus.CLOSED
            alert.closed_at = datetime.utcnow()
            alert.closed_by = user_id
            alert.updated_at = datetime.utcnow()
            
            if notes:
                alert.notes = notes
            
            self.update_alert(alert)
            
            logger.info(f"Alerta {alert_id} fechado por {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fechar alerta {alert_id}: {e}")
            return False
    
    # ==================== Notificacoes ====================
    
    def _publish_alert_to_sns(self, alert: Alert) -> bool:
        """Publica um alerta no SNS"""
        try:
            # Determinar topico com base na severidade
            topic_arn = self._get_topic_arn_for_severity(alert.severity)
            if topic_arn is None:
                return False
            
            # Preparar mensagem
            message = self._prepare_alert_message(alert)
            
            # Publicar no SNS
            self.get_sns_client().publish(
                TopicArn=topic_arn,
                Message=json.dumps(message),
                Subject=f"[{alert.severity.value.upper()}] {alert.title}"
            )
            
            logger.info(f"Alerta {alert.id} publicado no SNS (topico: {topic_arn})")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao publicar alerta {alert.id} no SNS: {e}")
            return False
    
    def _publish_alert_update_to_sns(self, alert: Alert) -> bool:
        """Publica uma atualizacao de alerta no SNS"""
        try:
            # Determinar topico
            topic_arn = self._get_topic_arn_for_severity(alert.severity)
            if topic_arn is None:
                return False
            
            # Preparar mensagem de atualizacao
            message = self._prepare_alert_update_message(alert)
            
            # Publicar no SNS
            self.get_sns_client().publish(
                TopicArn=topic_arn,
                Message=json.dumps(message),
                Subject=f"[UPDATE] [{alert.severity.value.upper()}] {alert.title}"
            )
            
            logger.info(f"Atualizacao do alerta {alert.id} publicada no SNS")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao publicar atualizacao do alerta {alert.id} no SNS: {e}")
            return False
    
    def _publish_alert_to_mqtt(self, alert: Alert) -> bool:
        """Publica um alerta no MQTT"""
        try:
            # Obter topico
            topic = iot_config.get_mqtt_topic("alerts")
            
            # Preparar mensagem
            message = alert.to_dict()
            
            # Publicar no MQTT (usando IoT Service)
            from .iot_service import IoTService
            iot_service = IoTService()
            iot_service.publish_alert(message)
            
            logger.info(f"Alerta {alert.id} publicado no MQTT (topico: {topic})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar alerta {alert.id} no MQTT: {e}")
            return False
    
    def _get_topic_arn_for_severity(self, severity: AlertSeverity) -> Optional[str]:
        """Obtem o ARN do topico SNS para uma severidade"""
        severity_topic_map = {
            AlertSeverity.CRITICAL: aws_config.SNS_TOPICS.get('critical_alerts'),
            AlertSeverity.HIGH: aws_config.SNS_TOPICS.get('high_alerts'),
            AlertSeverity.MEDIUM: aws_config.SNS_TOPICS.get('medium_alerts'),
            AlertSeverity.LOW: aws_config.SNS_TOPICS.get('low_alerts'),
            AlertSeverity.INFO: aws_config.SNS_TOPICS.get('info_alerts')
        }
        
        return severity_topic_map.get(severity)
    
    def _prepare_alert_message(self, alert: Alert) -> Dict:
        """Prepara a mensagem do alerta para o SNS"""
        return {
            'alert_id': alert.id,
            'type': alert.alert_type.value,
            'severity': alert.severity.value,
            'status': alert.status.value,
            'title': alert.title,
            'description': alert.description,
            'machine_id': alert.machine_id,
            'device_id': alert.device_id,
            'sensor_id': alert.sensor_id,
            'value': alert.value,
            'unit': alert.unit,
            'threshold': alert.threshold,
            'threshold_type': alert.threshold_type,
            'triggered_at': alert.triggered_at.isoformat(),
            'failure_probability': alert.failure_probability,
            'anomaly_score': alert.anomaly_score,
            'recommended_actions': alert.recommended_actions,
            'sla_response_time': alert.sla_response_time,
            'sla_resolution_time': alert.sla_resolution_time
        }
    
    def _prepare_alert_update_message(self, alert: Alert) -> Dict:
        """Prepara a mensagem de atualizacao do alerta para o SNS"""
        message = self._prepare_alert_message(alert)
        message.update({
            'update_type': 'status_change',
            'previous_status': alert.status.value,
            'new_status': alert.status.value,
            'updated_at': alert.updated_at.isoformat(),
            'updated_by': alert.resolved_by or alert.acknowledged_by or ''
        })
        return message
    
    # ==================== Escalonamento ====================
    
    def escalate_alert(self, alert: Alert) -> bool:
        """Escalona um alerta para o proximo nivel"""
        try:
            # Determinar proximo nivel de escalonamento
            next_severity = self._get_next_escalation_level(alert)
            
            if next_severity == alert.severity:
                return False  # Ja esta no nivel maximo
            
            # Atualizar severidade
            alert.severity = next_severity
            alert.updated_at = datetime.utcnow()
            
            self.update_alert(alert)
            
            logger.info(f"Alerta {alert.id} escalonado para {next_severity.value}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao escalar alerta {alert.id}: {e}")
            return False
    
    def _get_next_escalation_level(self, alert: Alert) -> AlertSeverity:
        """Obtem o proximo nivel de escalonamento"""
        escalation_order = [
            AlertSeverity.INFO,
            AlertSeverity.LOW,
            AlertSeverity.MEDIUM,
            AlertSeverity.HIGH,
            AlertSeverity.CRITICAL
        ]
        
        current_index = escalation_order.index(alert.severity)
        
        if current_index < len(escalation_order) - 1:
            return escalation_order[current_index + 1]
        
        return alert.severity
    
    def check_sla_violations(self) -> List[Alert]:
        """Verifica alertas com SLA violado"""
        violated_alerts = []
        
        try:
            # Obter alertas ativos
            active_alerts = self.list_alerts(status=AlertStatus.ACTIVE)
            
            for alert in active_alerts:
                if alert.is_sla_violated():
                    violated_alerts.append(alert)
                    
                    # Escalar alerta
                    self.escalate_alert(alert)
            
            return violated_alerts
            
        except Exception as e:
            logger.error(f"Erro ao verificar violacoes de SLA: {e}")
            return []
    
    # ==================== Criacao de Alertas a partir de Leituras ====================
    
    def create_alert_from_reading(self, reading: Reading, threshold: float, 
                                  threshold_type: str, severity: AlertSeverity) -> Optional[Alert]:
        """Cria um alerta a partir de uma leitura que violou um threshold"""
        try:
            # Determinar tipo do alerta
            sensor_type = reading.metadata.sensor_id.split('-')[0] if '-' in reading.metadata.sensor_id else 'vibration'
            alert_type = self._get_alert_type_for_sensor(sensor_type)
            
            # Criar alerta
            alert = Alert(
                id=f"alert-{reading.id}",
                alert_type=alert_type,
                severity=severity,
                status=AlertStatus.ACTIVE,
                title=f"{sensor_type.upper()} {threshold_type} detectado em {reading.metadata.sensor_id}",
                description=f"Sensor {reading.metadata.sensor_id} ultrapassou o threshold {threshold_type} de {threshold} {reading.unit} com valor de {reading.value} {reading.unit}",
                machine_id=reading.metadata.machine_id,
                device_id=reading.metadata.device_id,
                sensor_id=reading.metadata.sensor_id,
                reading_id=reading.id,
                value=reading.value,
                unit=reading.unit,
                threshold=threshold,
                threshold_type=threshold_type,
                triggered_at=datetime.utcnow(),
                anomaly_score=reading.anomaly_score,
                is_anomaly=reading.is_anomaly,
                failure_probability=0.0,
                sla_response_time=self._get_sla_response_time(severity),
                sla_resolution_time=self._get_sla_resolution_time(severity),
                notification_channels=['email', 'sms'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Criar alerta
            self.create_alert(alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta a partir da leitura {reading.id}: {e}")
            return None
    
    def _get_alert_type_for_sensor(self, sensor_type: str) -> AlertType:
        """Obtem o tipo de alerta para um sensor"""
        sensor_alert_map = {
            'vibration': AlertType.VIBRATION,
            'temperature': AlertType.TEMPERATURE,
            'pressure': AlertType.PRESSURE,
            'current': AlertType.CURRENT,
            'voltage': AlertType.VOLTAGE,
            'humidity': AlertType.HUMIDITY
        }
        
        return sensor_alert_map.get(sensor_type, AlertType.THRESHOLD_VIOLATION)
    
    def _get_sla_response_time(self, severity: AlertSeverity) -> int:
        """Obtem o tempo de resposta SLA para uma severidade"""
        sla_map = {
            AlertSeverity.CRITICAL: 15,  # 15 minutos
            AlertSeverity.HIGH: 30,    # 30 minutos
            AlertSeverity.MEDIUM: 60,  # 1 hora
            AlertSeverity.LOW: 120,    # 2 horas
            AlertSeverity.INFO: 240     # 4 horas
        }
        
        return sla_map.get(severity, 60)
    
    def _get_sla_resolution_time(self, severity: AlertSeverity) -> int:
        """Obtem o tempo de resolucao SLA para uma severidade"""
        sla_map = {
            AlertSeverity.CRITICAL: 120,   # 2 horas
            AlertSeverity.HIGH: 240,      # 4 horas
            AlertSeverity.MEDIUM: 480,    # 8 horas
            AlertSeverity.LOW: 1440,      # 24 horas
            AlertSeverity.INFO: 2880      # 48 horas
        }
        
        return sla_map.get(severity, 480)
    
    # ==================== Monitoramento ====================
    
    def get_alert_metrics(self) -> Dict:
        """Obtem metricas de alertas"""
        try:
            alerts = self.list_alerts(limit=1000)
            
            # Contar por severidade
            severity_counts = {}
            for severity in AlertSeverity:
                severity_counts[severity.value] = sum(
                    1 for a in alerts if a.severity == severity
                )
            
            # Contar por status
            status_counts = {}
            for status in AlertStatus:
                status_counts[status.value] = sum(
                    1 for a in alerts if a.status == status
                )
            
            # Contar por tipo
            type_counts = {}
            for alert_type in AlertType:
                type_counts[alert_type.value] = sum(
                    1 for a in alerts if a.alert_type == alert_type
                )
            
            # Alertas com SLA violado
            sla_violated = sum(1 for a in alerts if a.is_sla_violated())
            
            # Tempo medio de resposta
            response_times = [
                a.get_response_time() for a in alerts 
                if a.get_response_time() is not None
            ]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            return {
                'total_alerts': len(alerts),
                'by_severity': severity_counts,
                'by_status': status_counts,
                'by_type': type_counts,
                'sla_violated': sla_violated,
                'avg_response_time_minutes': avg_response_time
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter metricas de alertas: {e}")
            return {}
