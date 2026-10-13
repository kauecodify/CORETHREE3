"""
CORETHREE3 - DNA de Maquinas
Handler de Alertas

Handler para processamento e gerenciamento de alertas.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from ..models.reading import Reading
from ..models.prediction import Prediction, PredictionType
from ..services.alert_service import AlertService
from ..services.sagemaker_service import SageMakerService
from ..services.iot_service import IoTService

logger = logging.getLogger(__name__)


class AlertHandler:
    """
    Handler de Alertas para gerenciamento de notificacoes e escalonamento.
    
    Responsabilidades:
    - Processamento de mensagens de alerta
    - Gerenciamento de ciclo de vida de alertas
    - Escalonamento de alertas
    - Integracao com servicos de notificacao
    - Monitoramento de SLA
    """
    
    def __init__(self):
        """Inicializa o handler de alertas"""
        self.alert_service = AlertService()
        self.sagemaker_service = SageMakerService()
        self.iot_service = IoTService()
    
    # ==================== Processamento de Mensagens ====================
    
    def process_alert_message(self, message: Dict) -> bool:
        """Processa uma mensagem de alerta"""
        try:
            logger.info(f"Processando mensagem de alerta: {message.get('id')}")
            
            # Parse do alerta
            alert = self._parse_alert(message)
            if alert is None:
                logger.warning("Mensagem de alerta invalida")
                return False
            
            # Criar alerta
            alert = self.alert_service.create_alert(alert)
            
            # Processar alerta
            self._process_alert(alert)
            
            logger.info(f"Mensagem de alerta {alert.id} processada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de alerta: {e}")
            return False
    
    def _parse_alert(self, message: Dict) -> Optional[Alert]:
        """Analisa um alerta a partir de uma mensagem"""
        try:
            alert = Alert(
                id=message.get('id', f"alert-{datetime.utcnow().isoformat()}"),
                alert_type=AlertType(message.get('alert_type', 'anomaly')),
                severity=AlertSeverity(message.get('severity', 'medium')),
                status=AlertStatus(message.get('status', 'active')),
                title=message.get('title', ''),
                description=message.get('description', ''),
                machine_id=message.get('machine_id'),
                device_id=message.get('device_id'),
                sensor_id=message.get('sensor_id'),
                reading_id=message.get('reading_id'),
                value=message.get('value'),
                unit=message.get('unit'),
                threshold=message.get('threshold'),
                threshold_type=message.get('threshold_type'),
                triggered_at=datetime.fromisoformat(message.get('triggered_at'))
                    if message.get('triggered_at') else datetime.utcnow(),
                acknowledged_at=datetime.fromisoformat(message.get('acknowledged_at'))
                    if message.get('acknowledged_at') else None,
                acknowledged_by=message.get('acknowledged_by'),
                resolved_at=datetime.fromisoformat(message.get('resolved_at'))
                    if message.get('resolved_at') else None,
                resolved_by=message.get('resolved_by'),
                failure_probability=message.get('failure_probability', 0.0),
                anomaly_score=message.get('anomaly_score'),
                prediction_id=message.get('prediction_id'),
                recommended_actions=message.get('recommended_actions', []),
                notification_channels=message.get('notification_channels', []),
                notified_users=message.get('notified_users', []),
                sla_response_time=message.get('sla_response_time', 0),
                sla_resolution_time=message.get('sla_resolution_time', 0),
                tags=message.get('tags', []),
                created_at=datetime.fromisoformat(message.get('created_at'))
                    if message.get('created_at') else datetime.utcnow(),
                updated_at=datetime.fromisoformat(message.get('updated_at'))
                    if message.get('updated_at') else datetime.utcnow()
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao analisar alerta: {e}")
            return None
    
    def _process_alert(self, alert: Alert) -> bool:
        """Processa um alerta recem-criado"""
        try:
            # Verificar se e necessario escalonamento imediato
            if self._should_escalate_immediately(alert):
                self.alert_service.escalate_alert(alert)
            
            # Verificar SLA
            self._check_alert_sla(alert)
            
            # Notificar usuarios
            self._notify_users(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar alerta {alert.id}: {e}")
            return False
    
    def _should_escalate_immediately(self, alert: Alert) -> bool:
        """Determina se um alerta deve ser escalado imediatamente"""
        # Alertas criticos sao escalados imediatamente
        if alert.severity == AlertSeverity.CRITICAL:
            return True
        
        # Alertas com alta probabilidade de falha
        if alert.failure_probability > 0.8:
            return True
        
        # Alertas de anomalias com score alto
        if alert.anomaly_score and alert.anomaly_score > 0.9:
            return True
        
        return False
    
    # ==================== Gerenciamento de Alertas ====================
    
    def create_alert(self, alert_data: Dict) -> Optional[Alert]:
        """Cria um novo alerta"""
        try:
            # Parse do alerta
            alert = self._parse_alert(alert_data)
            if alert is None:
                return None
            
            # Criar alerta
            alert = self.alert_service.create_alert(alert)
            
            # Processar alerta
            self._process_alert(alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {e}")
            return None
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Obtem um alerta pelo ID"""
        return self.alert_service.get_alert(alert_id)
    
    def list_alerts(self, machine_id: Optional[str] = None, device_id: Optional[str] = None,
                   severity: Optional[AlertSeverity] = None, status: Optional[AlertStatus] = None,
                   limit: int = 100) -> List[Alert]:
        """Lista alertas com filtros"""
        return self.alert_service.list_alerts(
            machine_id=machine_id,
            device_id=device_id,
            severity=severity,
            status=status,
            limit=limit
        )
    
    def update_alert(self, alert_id: str, update_data: Dict) -> Optional[Alert]:
        """Atualiza um alerta"""
        try:
            alert = self.alert_service.get_alert(alert_id)
            if alert is None:
                return None
            
            # Aplicar atualizacoes
            if 'severity' in update_data:
                alert.severity = AlertSeverity(update_data['severity'])
            if 'status' in update_data:
                alert.status = AlertStatus(update_data['status'])
            if 'title' in update_data:
                alert.title = update_data['title']
            if 'description' in update_data:
                alert.description = update_data['description']
            if 'failure_probability' in update_data:
                alert.failure_probability = update_data['failure_probability']
            if 'anomaly_score' in update_data:
                alert.anomaly_score = update_data['anomaly_score']
            
            alert.updated_at = datetime.utcnow()
            
            # Atualizar alerta
            alert = self.alert_service.update_alert(alert)
            
            # Processar atualizacao
            self._process_alert_update(alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao atualizar alerta {alert_id}: {e}")
            return None
    
    def _process_alert_update(self, alert: Alert) -> bool:
        """Processa uma atualizacao de alerta"""
        try:
            # Se o alerta foi resolvido
            if alert.status == AlertStatus.RESOLVED:
                self._handle_resolved_alert(alert)
            
            # Se o alerta foi fechado
            if alert.status == AlertStatus.CLOSED:
                self._handle_closed_alert(alert)
            
            # Verificar SLA
            self._check_alert_sla(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar atualizacao do alerta {alert.id}: {e}")
            return False
    
    def _handle_resolved_alert(self, alert: Alert) -> bool:
        """Processa um alerta resolvido"""
        try:
            # Notificar usuarios sobre a resolucao
            self._notify_resolution(alert)
            
            # Atualizar metricas
            self._update_alert_metrics(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar alerta resolvido {alert.id}: {e}")
            return False
    
    def _handle_closed_alert(self, alert: Alert) -> bool:
        """Processa um alerta fechado"""
        try:
            # Armazenar para auditoria
            self._archive_alert(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar alerta fechado {alert.id}: {e}")
            return False
    
    # ==================== Acoes de Alerta ====================
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Reconhece um alerta"""
        return self.alert_service.acknowledge_alert(alert_id, user_id)
    
    def resolve_alert(self, alert_id: str, user_id: str, notes: Optional[str] = None) -> bool:
        """Resolve um alerta"""
        return self.alert_service.resolve_alert(alert_id, user_id, notes)
    
    def close_alert(self, alert_id: str, user_id: str, notes: Optional[str] = None) -> bool:
        """Fecha um alerta"""
        return self.alert_service.close_alert(alert_id, user_id, notes)
    
    def escalate_alert(self, alert_id: str) -> bool:
        """Escalona um alerta"""
        return self.alert_service.escalate_alert(alert_id)
    
    # ==================== Notificacoes ====================
    
    def _notify_users(self, alert: Alert) -> bool:
        """Notifica usuarios sobre um alerta"""
        try:
            # Determinar usuarios a notificar
            users_to_notify = self._get_users_to_notify(alert)
            
            if not users_to_notify:
                return False
            
            # Preparar mensagem
            message = self._prepare_notification_message(alert)
            
            # Notificar via SNS (ja feito no AlertService)
            # Notificar via Email
            self._send_email_notification(users_to_notify, message)
            
            # Notificar via SMS (para alertas criticos)
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                self._send_sms_notification(users_to_notify, message)
            
            # Atualizar lista de usuarios notificados
            alert.notified_users = list(set(alert.notified_users + users_to_notify))
            self.alert_service.update_alert(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao notificar usuarios sobre alerta {alert.id}: {e}")
            return False
    
    def _notify_resolution(self, alert: Alert) -> bool:
        """Notifica usuarios sobre a resolucao de um alerta"""
        try:
            # Notificar usuarios que foram notificados originalmente
            if not alert.notified_users:
                return False
            
            message = self._prepare_resolution_message(alert)
            
            # Notificar via Email
            self._send_email_notification(alert.notified_users, message)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao notificar resolucao do alerta {alert.id}: {e}")
            return False
    
    def _get_users_to_notify(self, alert: Alert) -> List[str]:
        """Determina quais usuarios notificar"""
        # Para simplificacao, notificar usuarios padroes
        # Em um sistema real, isso viria de uma base de dados
        
        # Usuarios padroes por severidade
        users_by_severity = {
            AlertSeverity.CRITICAL: ['admin@empresa.com', 'gerente@empresa.com', 'manutencao@empresa.com'],
            AlertSeverity.HIGH: ['gerente@empresa.com', 'manutencao@empresa.com'],
            AlertSeverity.MEDIUM: ['manutencao@empresa.com'],
            AlertSeverity.LOW: ['manutencao@empresa.com'],
            AlertSeverity.INFO: []
        }
        
        # Usuarios padroes por tipo de maquina
        users_by_machine = {
            'motor': ['manutencao@empresa.com', 'eletrica@empresa.com'],
            'bomb': ['manutencao@empresa.com', 'hidraulica@empresa.com'],
            'compressor': ['manutencao@empresa.com', 'pneumatica@empresa.com'],
            'forno': ['manutencao@empresa.com', 'termica@empresa.com'],
            'caldeira': ['manutencao@empresa.com', 'seguranca@empresa.com']
        }
        
        users = set()
        
        # Adicionar usuarios por severidade
        users.update(users_by_severity.get(alert.severity, []))
        
        # Adicionar usuarios por tipo de maquina
        if alert.machine_id:
            # Obter tipo da maquina (simplificado)
            machine_type = alert.machine_id.split('-')[0] if '-' in alert.machine_id else 'generic'
            users.update(users_by_machine.get(machine_type, []))
        
        # Adicionar usuarios especificos do alerta
        users.update(alert.notified_users)
        
        return list(users)
    
    def _prepare_notification_message(self, alert: Alert) -> Dict:
        """Prepara a mensagem de notificacao"""
        return {
            'alert_id': alert.id,
            'type': alert.alert_type.value,
            'severity': alert.severity.value.upper(),
            'status': alert.status.value,
            'title': alert.title,
            'description': alert.description,
            'machine_id': alert.machine_id,
            'device_id': alert.device_id,
            'sensor_id': alert.sensor_id,
            'value': alert.value,
            'unit': alert.unit,
            'threshold': alert.threshold,
            'triggered_at': alert.triggered_at.isoformat(),
            'recommended_actions': alert.recommended_actions,
            'sla_response_time': alert.sla_response_time,
            'sla_resolution_time': alert.sla_resolution_time
        }
    
    def _prepare_resolution_message(self, alert: Alert) -> Dict:
        """Prepara a mensagem de resolucao"""
        message = self._prepare_notification_message(alert)
        message.update({
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else '',
            'resolved_by': alert.resolved_by or '',
            'resolution_notes': alert.notes or ''
        })
        return message
    
    def _send_email_notification(self, users: List[str], message: Dict) -> bool:
        """Envía notificacao por email"""
        try:
            # Em um sistema real, isso usaria SES ou um servico de email
            logger.info(f"Enviando email para {users} sobre alerta {message.get('alert_id')}")
            
            # Simular envio de email
            for user in users:
                logger.info(f"Email enviado para {user}: {message.get('title')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def _send_sms_notification(self, users: List[str], message: Dict) -> bool:
        """Envía notificacao por SMS"""
        try:
            # Em um sistema real, isso usaria SNS SMS ou um servico de SMS
            logger.info(f"Enviando SMS para {users} sobre alerta {message.get('alert_id')}")
            
            # Simular envio de SMS
            for user in users:
                logger.info(f"SMS enviado para {user}: {message.get('title')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return False
    
    # ==================== SLA ====================
    
    def _check_alert_sla(self, alert: Alert) -> bool:
        """Verifica o SLA do alerta"""
        try:
            # Verificar se o SLA foi violado
            if alert.is_sla_violated():
                logger.warning(f"SLA violado para alerta {alert.id}")
                
                # Escalar alerta
                self.alert_service.escalate_alert(alert)
                
                # Notificar sobre violacao de SLA
                self._notify_sla_violation(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar SLA do alerta {alert.id}: {e}")
            return False
    
    def _notify_sla_violation(self, alert: Alert) -> bool:
        """Notifica sobre violacao de SLA"""
        try:
            # Notificar gerencia
            message = {
                'alert_id': alert.id,
                'type': 'sla_violation',
                'severity': alert.severity.value,
                'title': f"SLA Violado: {alert.title}",
                'description': f"O SLA de resposta foi violado para o alerta {alert.id}",
                'response_time': alert.get_response_time(),
                'sla_response_time': alert.sla_response_time
            }
            
            # Notificar gerencia
            management_users = ['admin@empresa.com', 'gerente@empresa.com']
            self._send_email_notification(management_users, message)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao notificar violacao de SLA: {e}")
            return False
    
    # ==================== Metricas ====================
    
    def get_alert_metrics(self) -> Dict:
        """Obtem metricas de alertas"""
        return self.alert_service.get_alert_metrics()
    
    def get_alert_statistics(self, start_time: datetime, end_time: datetime) -> Dict:
        """Obtem estatisticas de alertas em um periodo"""
        try:
            alerts = self.alert_service.list_alerts(limit=1000)
            
            # Filtrar por periodo
            filtered_alerts = [
                a for a in alerts 
                if start_time <= a.triggered_at <= end_time
            ]
            
            # Contar por severidade
            severity_counts = {}
            for severity in AlertSeverity:
                severity_counts[severity.value] = sum(
                    1 for a in filtered_alerts if a.severity == severity
                )
            
            # Contar por tipo
            type_counts = {}
            for alert_type in AlertType:
                type_counts[alert_type.value] = sum(
                    1 for a in filtered_alerts if a.alert_type == alert_type
                )
            
            # Contar por status
            status_counts = {}
            for status in AlertStatus:
                status_counts[status.value] = sum(
                    1 for a in filtered_alerts if a.status == status
                )
            
            # Tempo medio de resposta
            response_times = [
                a.get_response_time() for a in filtered_alerts 
                if a.get_response_time() is not None
            ]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Tempo medio de resolucao
            resolution_times = [
                a.get_resolution_time() for a in filtered_alerts 
                if a.get_resolution_time() is not None
            ]
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            # SLA violado
            sla_violated = sum(1 for a in filtered_alerts if a.is_sla_violated())
            
            return {
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'total_alerts': len(filtered_alerts),
                'by_severity': severity_counts,
                'by_type': type_counts,
                'by_status': status_counts,
                'avg_response_time_minutes': avg_response_time,
                'avg_resolution_time_minutes': avg_resolution_time,
                'sla_violated': sla_violated
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatisticas de alertas: {e}")
            return {}
    
    def _update_alert_metrics(self, alert: Alert) -> bool:
        """Atualiza metricas do alerta"""
        try:
            # Em um sistema real, isso atualizaria um painel de metricas
            logger.info(f"Atualizando metricas para alerta {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar metricas do alerta {alert.id}: {e}")
            return False
    
    def _archive_alert(self, alert: Alert) -> bool:
        """Arquiva um alerta"""
        try:
            # Em um sistema real, isso moveria o alerta para uma tabela de auditoria
            logger.info(f"Arquivando alerta {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao arquivar alerta {alert.id}: {e}")
            return False
    
    # ==================== Alertas a partir de Predicoes ====================
    
    def create_alert_from_prediction(self, prediction: Prediction) -> Optional[Alert]:
        """Cria um alerta a partir de uma predicao"""
        try:
            # Determinar severidade com base na predicao
            severity = self._get_severity_from_prediction(prediction)
            
            # Criar alerta
            alert = Alert(
                id=f"alert-pred-{prediction.id}",
                alert_type=AlertType.PREDICTION,
                severity=severity,
                status=AlertStatus.ACTIVE,
                title=f"Predicao: {prediction.prediction_type.value.replace('_', ' ').title()}",
                description=self._get_alert_description_from_prediction(prediction),
                machine_id=prediction.machine_id,
                device_id=prediction.device_id,
                sensor_ids=prediction.sensor_ids,
                prediction_id=prediction.id,
                triggered_at=datetime.utcnow(),
                failure_probability=prediction.failure_probability,
                remaining_useful_life=prediction.remaining_useful_life,
                anomaly_score=prediction.anomaly_score,
                sla_response_time=self._get_sla_response_time(severity),
                sla_resolution_time=self._get_sla_resolution_time(severity),
                recommended_actions=prediction.recommended_actions,
                notification_channels=['email', 'sms'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.alert_service.create_alert(alert)
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta a partir da predicao {prediction.id}: {e}")
            return None
    
    def _get_severity_from_prediction(self, prediction: Prediction) -> AlertSeverity:
        """Determina a severidade com base na predicao"""
        if prediction.failure_probability >= 0.8:
            return AlertSeverity.CRITICAL
        elif prediction.failure_probability >= 0.6:
            return AlertSeverity.HIGH
        elif prediction.failure_probability >= 0.4:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _get_alert_description_from_prediction(self, prediction: Prediction) -> str:
        """Gera a descricao do alerta a partir da predicao"""
        if prediction.prediction_type == PredictionType.FAILURE_PREDICTION:
            days = prediction.get_days_until_failure()
            if days:
                return f"Falha prevista em {days:.1f} dias com probabilidade de {prediction.failure_probability:.1%}"
            return f"Falha prevista com probabilidade de {prediction.failure_probability:.1%}"
        elif prediction.prediction_type == PredictionType.REMAINING_USEFUL_LIFE:
            if prediction.remaining_useful_life:
                return f"Vida util restante estimada em {prediction.remaining_useful_life:.1f} dias"
            return "Vida util restante baixa"
        elif prediction.prediction_type == PredictionType.ANOMALY_DETECTION:
            return f"Anomalia detectada com score de {prediction.anomaly_score:.2f}"
        else:
            return prediction.interpretation or "Predicao do sistema"
    
    def _get_sla_response_time(self, severity: AlertSeverity) -> int:
        """Obtem o tempo de resposta SLA para uma severidade"""
        sla_map = {
            AlertSeverity.CRITICAL: 15,
            AlertSeverity.HIGH: 30,
            AlertSeverity.MEDIUM: 60,
            AlertSeverity.LOW: 120,
            AlertSeverity.INFO: 240
        }
        return sla_map.get(severity, 60)
    
    def _get_sla_resolution_time(self, severity: AlertSeverity) -> int:
        """Obtem o tempo de resolucao SLA para uma severidade"""
        sla_map = {
            AlertSeverity.CRITICAL: 120,
            AlertSeverity.HIGH: 240,
            AlertSeverity.MEDIUM: 480,
            AlertSeverity.LOW: 1440,
            AlertSeverity.INFO: 2880
        }
        return sla_map.get(severity, 480)
    
    # ==================== Monitoramento ====================
    
    def check_active_alerts(self) -> List[Alert]:
        """Verifica alertas ativos"""
        return self.alert_service.list_alerts(status=AlertStatus.ACTIVE)
    
    def check_unacknowledged_alerts(self) -> List[Alert]:
        """Verifica alertas nao reconhecidos"""
        return self.alert_service.list_alerts(status=AlertStatus.ACTIVE)
    
    def check_sla_violations(self) -> List[Alert]:
        """Verifica alertas com SLA violado"""
        return self.alert_service.check_sla_violations()
    
    def get_alert_summary(self) -> Dict:
        """Obtem um resumo dos alertas"""
        try:
            metrics = self.get_alert_metrics()
            active_alerts = self.check_active_alerts()
            unacknowledged = self.check_unacknowledged_alerts()
            sla_violated = self.check_sla_violations()
            
            return {
                'metrics': metrics,
                'active_alerts_count': len(active_alerts),
                'unacknowledged_alerts_count': len(unacknowledged),
                'sla_violated_count': len(sla_violated),
                'critical_alerts': metrics.get('by_severity', {}).get('critical', 0),
                'high_alerts': metrics.get('by_severity', {}).get('high', 0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de alertas: {e}")
            return {}
