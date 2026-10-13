"""
CORETHREE3 - DNA de Maquinas
Handler de Manutencao

Handler para gerenciamento de manutencao preditiva e preventiva.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models.maintenance import Maintenance, MaintenanceType, MaintenanceStatus, MaintenancePriority
from ..models.prediction import Prediction, PredictionType
from ..models.alert import Alert, AlertSeverity, AlertStatus
from ..models.machine import Machine, MachineStatus
from ..services.sagemaker_service import SageMakerService
from ..services.timestream_service import TimestreamService
from ..services.alert_service import AlertService
from ..services.iot_service import IoTService
from ..handlers.prediction_handler import PredictionHandler
from ..handlers.alert_handler import AlertHandler

logger = logging.getLogger(__name__)


class MaintenanceHandler:
    """
    Handler de Manutencao para gerenciamento de ordens de servico e manutencao preditiva.
    
    Responsabilidades:
    - Criacao e gerenciamento de ordens de manutencao
    - Agendamento de manutencao com base em predicoes
    - Integracao com alertas e predicoes
    - Monitoramento de manutencao
    """
    
    def __init__(self):
        """Inicializa o handler de manutencao"""
        self.iot_service = IoTService()
        self.timestream_service = TimestreamService()
        self.alert_service = AlertService()
        self.prediction_handler = PredictionHandler()
        self.alert_handler = AlertHandler()
        self.maintenance_cache: Dict[str, Maintenance] = {}
    
    # ==================== Gerenciamento de Manutencao ====================
    
    def create_maintenance(self, maintenance_data: Dict) -> Optional[Maintenance]:
        """Cria uma nova ordem de manutencao"""
        try:
            # Parse da manutencao
            maintenance = self._parse_maintenance(maintenance_data)
            if maintenance is None:
                return None
            
            # Validar manutencao
            if not self._validate_maintenance(maintenance):
                raise ValueError("Dados de manutencao invalidos")
            
            # Associar predicoes e alertas
            self._associate_predictions_and_alerts(maintenance)
            
            # Salvar no cache
            self.maintenance_cache[maintenance.id] = maintenance
            
            # Notificar sobre nova manutencao
            self._notify_maintenance_created(maintenance)
            
            logger.info(f"Manutencao {maintenance.id} criada com sucesso")
            return maintenance
            
        except Exception as e:
            logger.error(f"Erro ao criar manutencao: {e}")
            return None
    
    def _parse_maintenance(self, data: Dict) -> Optional[Maintenance]:
        """Analisa uma manutencao a partir de dados"""
        try:
            maintenance = Maintenance(
                id=data.get('id', f"maintenance-{datetime.utcnow().isoformat()}"),
                maintenance_type=MaintenanceType(data.get('maintenance_type', 'preventive')),
                status=MaintenanceStatus(data.get('status', 'scheduled')),
                priority=MaintenancePriority(data.get('priority', 'medium')),
                device_id=data.get('device_id'),
                machine_id=data.get('machine_id'),
                sensor_ids=data.get('sensor_ids', []),
                scheduled_start=datetime.fromisoformat(data.get('scheduled_start'))
                    if data.get('scheduled_start') else datetime.utcnow() + timedelta(days=7),
                scheduled_end=datetime.fromisoformat(data.get('scheduled_end'))
                    if data.get('scheduled_end') else datetime.utcnow() + timedelta(days=7, hours=4),
                actual_start=datetime.fromisoformat(data.get('actual_start'))
                    if data.get('actual_start') else None,
                actual_end=datetime.fromisoformat(data.get('actual_end'))
                    if data.get('actual_end') else None,
                estimated_duration=data.get('estimated_duration', 4.0),
                actual_duration=data.get('actual_duration'),
                assigned_to=data.get('assigned_to'),
                assigned_team=data.get('assigned_team'),
                supervisor=data.get('supervisor'),
                title=data.get('title', ''),
                description=data.get('description', ''),
                actions_performed=data.get('actions_performed', []),
                parts_replaced=data.get('parts_replaced', []),
                tools_used=data.get('tools_used', []),
                materials_used=data.get('materials_used', []),
                labor_cost=data.get('labor_cost'),
                material_cost=data.get('material_cost'),
                total_cost=data.get('total_cost'),
                prediction_id=data.get('prediction_id'),
                alert_ids=data.get('alert_ids', []),
                root_cause=data.get('root_cause'),
                effectiveness=data.get('effectiveness'),
                notes=data.get('notes'),
                work_order_number=data.get('work_order_number'),
                invoice_number=data.get('invoice_number'),
                attachments=data.get('attachments', []),
                source=data.get('source', 'system'),
                tags=data.get('tags', []),
                created_at=datetime.fromisoformat(data.get('created_at'))
                    if data.get('created_at') else datetime.utcnow(),
                updated_at=datetime.fromisoformat(data.get('updated_at'))
                    if data.get('updated_at') else datetime.utcnow()
            )
            
            return maintenance
            
        except Exception as e:
            logger.error(f"Erro ao analisar manutencao: {e}")
            return None
    
    def _validate_maintenance(self, maintenance: Maintenance) -> bool:
        """Valida uma manutencao"""
        if not maintenance.id:
            return False
        if not maintenance.title:
            return False
        if not maintenance.scheduled_start:
            return False
        if maintenance.scheduled_start < datetime.utcnow():
            return False  # Data agendada no passado
        return True
    
    def _associate_predictions_and_alerts(self, maintenance: Maintenance) -> bool:
        """Associa predicoes e alertas a manutencao"""
        try:
            # Se nao ha predicao associada, procurar predicoes relacionadas
            if not maintenance.prediction_id and maintenance.machine_id:
                predictions = self.prediction_handler.list_predictions(
                    machine_id=maintenance.machine_id,
                    limit=5
                )
                
                # Encontrar predicao mais relevante
                relevant_prediction = None
                for prediction in predictions:
                    if prediction.failure_probability > 0.5:
                        relevant_prediction = prediction
                        break
                
                if relevant_prediction:
                    maintenance.prediction_id = relevant_prediction.id
            
            # Se nao ha alertas associados, procurar alertas relacionados
            if not maintenance.alert_ids and maintenance.machine_id:
                alerts = self.alert_service.list_alerts(
                    machine_id=maintenance.machine_id,
                    status=AlertStatus.ACTIVE,
                    limit=10
                )
                
                # Adicionar alertas ativos
                maintenance.alert_ids = [alert.id for alert in alerts]
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao associar predicoes e alertas: {e}")
            return False
    
    def get_maintenance(self, maintenance_id: str) -> Optional[Maintenance]:
        """Obtem uma manutencao pelo ID"""
        # Verificar cache
        if maintenance_id in self.maintenance_cache:
            return self.maintenance_cache[maintenance_id]
        
        # Em um sistema real, buscar no banco de dados
        return None
    
    def list_maintenances(self, machine_id: Optional[str] = None, device_id: Optional[str] = None,
                          maintenance_type: Optional[MaintenanceType] = None,
                          status: Optional[MaintenanceStatus] = None, 
                          priority: Optional[MaintenancePriority] = None,
                          limit: int = 100) -> List[Maintenance]:
        """Lista manutencoes com filtros"""
        try:
            # Filtrar cache
            maintenances = list(self.maintenance_cache.values())
            
            if machine_id:
                maintenances = [m for m in maintenances if m.machine_id == machine_id]
            if device_id:
                maintenances = [m for m in maintenances if m.device_id == device_id]
            if maintenance_type:
                maintenances = [m for m in maintenances if m.maintenance_type == maintenance_type]
            if status:
                maintenances = [m for m in maintenances if m.status == status]
            if priority:
                maintenances = [m for m in maintenances if m.priority == priority]
            
            # Ordenar por data agendada
            maintenances.sort(key=lambda m: m.scheduled_start, reverse=True)
            
            return maintenances[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao listar manutencoes: {e}")
            return []
    
    def update_maintenance(self, maintenance_id: str, update_data: Dict) -> Optional[Maintenance]:
        """Atualiza uma manutencao"""
        try:
            maintenance = self.get_maintenance(maintenance_id)
            if maintenance is None:
                return None
            
            # Aplicar atualizacoes
            if 'status' in update_data:
                maintenance.status = MaintenanceStatus(update_data['status'])
            if 'priority' in update_data:
                maintenance.priority = MaintenancePriority(update_data['priority'])
            if 'assigned_to' in update_data:
                maintenance.assigned_to = update_data['assigned_to']
            if 'assigned_team' in update_data:
                maintenance.assigned_team = update_data['assigned_team']
            if 'scheduled_start' in update_data:
                maintenance.scheduled_start = datetime.fromisoformat(update_data['scheduled_start'])
            if 'scheduled_end' in update_data:
                maintenance.scheduled_end = datetime.fromisoformat(update_data['scheduled_end'])
            if 'actual_start' in update_data:
                maintenance.actual_start = datetime.fromisoformat(update_data['actual_start'])
            if 'actual_end' in update_data:
                maintenance.actual_end = datetime.fromisoformat(update_data['actual_end'])
            if 'actions_performed' in update_data:
                maintenance.actions_performed = update_data['actions_performed']
            if 'parts_replaced' in update_data:
                maintenance.parts_replaced = update_data['parts_replaced']
            if 'root_cause' in update_data:
                maintenance.root_cause = update_data['root_cause']
            if 'effectiveness' in update_data:
                maintenance.effectiveness = update_data['effectiveness']
            if 'notes' in update_data:
                maintenance.notes = update_data['notes']
            
            maintenance.updated_at = datetime.utcnow()
            
            # Atualizar cache
            self.maintenance_cache[maintenance_id] = maintenance
            
            # Processar atualizacao
            self._process_maintenance_update(maintenance)
            
            return maintenance
            
        except Exception as e:
            logger.error(f"Erro ao atualizar manutencao {maintenance_id}: {e}")
            return None
    
    def _process_maintenance_update(self, maintenance: Maintenance) -> bool:
        """Processa uma atualizacao de manutencao"""
        try:
            # Se a manutencao foi concluida
            if maintenance.status == MaintenanceStatus.COMPLETED:
                self._handle_completed_maintenance(maintenance)
            
            # Se a manutencao foi cancelada
            if maintenance.status == MaintenanceStatus.CANCELLED:
                self._handle_cancelled_maintenance(maintenance)
            
            # Notificar sobre atualizacao
            self._notify_maintenance_updated(maintenance)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar atualizacao da manutencao {maintenance.id}: {e}")
            return False
    
    def _handle_completed_maintenance(self, maintenance: Maintenance) -> bool:
        """Processa uma manutencao concluida"""
        try:
            # Atualizar status da maquina
            if maintenance.machine_id:
                self._update_machine_status_after_maintenance(maintenance.machine_id)
            
            # Fechar alertas relacionados
            for alert_id in maintenance.alert_ids:
                self.alert_handler.close_alert(alert_id, 'system', f"Resolvido pela manutencao {maintenance.id}")
            
            # Notificar sobre conclusao
            self._notify_maintenance_completed(maintenance)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar manutencao concluida {maintenance.id}: {e}")
            return False
    
    def _handle_cancelled_maintenance(self, maintenance: Maintenance) -> bool:
        """Processa uma manutencao cancelada"""
        try:
            # Reabrir alertas relacionados se eles foram fechados
            for alert_id in maintenance.alert_ids:
                alert = self.alert_service.get_alert(alert_id)
                if alert and alert.status == AlertStatus.CLOSED:
                    alert.status = AlertStatus.ACTIVE
                    alert.updated_at = datetime.utcnow()
                    self.alert_service.update_alert(alert)
            
            # Notificar sobre cancelamento
            self._notify_maintenance_cancelled(maintenance)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar manutencao cancelada {maintenance.id}: {e}")
            return False
    
    def delete_maintenance(self, maintenance_id: str) -> bool:
        """Remove uma manutencao"""
        try:
            if maintenance_id in self.maintenance_cache:
                del self.maintenance_cache[maintenance_id]
            
            # Em um sistema real, remover do banco de dados
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover manutencao {maintenance_id}: {e}")
            return False
    
    # ==================== Agendamento de Manutencao ====================
    
    def schedule_maintenance_from_prediction(self, prediction: Prediction) -> Optional[Maintenance]:
        """Agenda manutencao com base em uma predicao"""
        try:
            # Determinar tipo e prioridade da manutencao
            maintenance_type = self._get_maintenance_type_from_prediction(prediction)
            priority = self._get_priority_from_prediction(prediction)
            
            # Determinar data de agendamento
            scheduled_start = self._get_scheduled_start_from_prediction(prediction)
            
            # Criar manutencao
            maintenance_data = {
                'maintenance_type': maintenance_type.value,
                'priority': priority.value,
                'machine_id': prediction.machine_id,
                'device_id': prediction.device_id,
                'sensor_ids': prediction.sensor_ids,
                'prediction_id': prediction.id,
                'scheduled_start': scheduled_start.isoformat(),
                'scheduled_end': (scheduled_start + timedelta(hours=4)).isoformat(),
                'title': f"Manutencao preditiva - {prediction.prediction_type.value.replace('_', ' ').title()}",
                'description': self._get_maintenance_description_from_prediction(prediction),
                'estimated_duration': 4.0,
                'recommended_actions': prediction.recommended_actions,
                'source': 'prediction',
                'tags': ['predictive', prediction.prediction_type.value]
            }
            
            maintenance = self.create_maintenance(maintenance_data)
            
            # Associar manutencao a predicao
            if maintenance:
                prediction.maintenance_id = maintenance.id
            
            return maintenance
            
        except Exception as e:
            logger.error(f"Erro ao agendar manutencao a partir da predicao {prediction.id}: {e}")
            return None
    
    def _get_maintenance_type_from_prediction(self, prediction: Prediction) -> MaintenanceType:
        """Determina o tipo de manutencao com base na predicao"""
        if prediction.prediction_type == PredictionType.FAILURE_PREDICTION:
            return MaintenanceType.PREDICTIVE
        elif prediction.prediction_type == PredictionType.REMAINING_USEFUL_LIFE:
            return MaintenanceType.PREDICTIVE
        elif prediction.prediction_type == PredictionType.ANOMALY_DETECTION:
            return MaintenanceType.CORRECTIVE
        else:
            return MaintenanceType.PREVENTIVE
    
    def _get_priority_from_prediction(self, prediction: Prediction) -> MaintenancePriority:
        """Determina a prioridade com base na predicao"""
        if prediction.failure_probability >= 0.8:
            return MaintenancePriority.CRITICAL
        elif prediction.failure_probability >= 0.6:
            return MaintenancePriority.HIGH
        elif prediction.failure_probability >= 0.4:
            return MaintenancePriority.MEDIUM
        else:
            return MaintenancePriority.LOW
    
    def _get_scheduled_start_from_prediction(self, prediction: Prediction) -> datetime:
        """Determina a data de inicio com base na predicao"""
        # Se ha data de falha prevista, agendar antes
        if prediction.predicted_failure_date:
            # Agendar 3 dias antes da falha prevista
            return prediction.predicted_failure_date - timedelta(days=3)
        
        # Se ha RUL, agendar quando RUL for baixo
        if prediction.remaining_useful_life is not None:
            if prediction.remaining_useful_life <= 30:
                return datetime.utcnow() + timedelta(days=1)
            elif prediction.remaining_useful_life <= 60:
                return datetime.utcnow() + timedelta(days=7)
            else:
                return datetime.utcnow() + timedelta(days=30)
        
        # Padrao: agendar para amanha
        return datetime.utcnow() + timedelta(days=1)
    
    def _get_maintenance_description_from_prediction(self, prediction: Prediction) -> str:
        """Gera a descricao da manutencao com base na predicao"""
        if prediction.prediction_type == PredictionType.FAILURE_PREDICTION:
            days = prediction.get_days_until_failure()
            if days:
                return f"Manutencao preditiva baseada em previsao de falha em {days:.1f} dias (probabilidade: {prediction.failure_probability:.1%})"
            return f"Manutencao preditiva baseada em previsao de falha (probabilidade: {prediction.failure_probability:.1%})"
        elif prediction.prediction_type == PredictionType.REMAINING_USEFUL_LIFE:
            if prediction.remaining_useful_life:
                return f"Manutencao preditiva baseada em vida util restante de {prediction.remaining_useful_life:.1f} dias"
            return "Manutencao preditiva baseada em vida util restante"
        elif prediction.prediction_type == PredictionType.ANOMALY_DETECTION:
            return f"Manutencao corretiva baseada em deteccao de anomalia (score: {prediction.anomaly_score:.2f})"
        else:
            return prediction.interpretation or "Manutencao preditiva"
    
    def schedule_maintenance_from_alert(self, alert: Alert) -> Optional[Maintenance]:
        """Agenda manutencao com base em um alerta"""
        try:
            # Determinar tipo e prioridade da manutencao
            maintenance_type = self._get_maintenance_type_from_alert(alert)
            priority = self._get_priority_from_alert(alert)
            
            # Determinar data de agendamento
            scheduled_start = self._get_scheduled_start_from_alert(alert)
            
            # Criar manutencao
            maintenance_data = {
                'maintenance_type': maintenance_type.value,
                'priority': priority.value,
                'machine_id': alert.machine_id,
                'device_id': alert.device_id,
                'sensor_ids': [alert.sensor_id] if alert.sensor_id else [],
                'alert_ids': [alert.id],
                'scheduled_start': scheduled_start.isoformat(),
                'scheduled_end': (scheduled_start + timedelta(hours=4)).isoformat(),
                'title': f"Manutencao corretiva - {alert.alert_type.value.replace('_', ' ').title()}",
                'description': f"Manutencao agendada a partir do alerta: {alert.title}",
                'estimated_duration': 4.0,
                'recommended_actions': alert.recommended_actions,
                'source': 'alert',
                'tags': ['corrective', alert.alert_type.value]
            }
            
            maintenance = self.create_maintenance(maintenance_data)
            
            # Associar manutencao a alerta
            if maintenance:
                alert.maintenance_id = maintenance.id
                self.alert_service.update_alert(alert)
            
            return maintenance
            
        except Exception as e:
            logger.error(f"Erro ao agendar manutencao a partir do alerta {alert.id}: {e}")
            return None
    
    def _get_maintenance_type_from_alert(self, alert: Alert) -> MaintenanceType:
        """Determina o tipo de manutencao com base no alerta"""
        if alert.alert_type in [AlertType.VIBRATION, AlertType.TEMPERATURE, AlertType.PRESSURE,
                               AlertType.CURRENT, AlertType.VOLTAGE, AlertType.ANOMALY]:
            return MaintenanceType.CORRECTIVE
        elif alert.alert_type == AlertType.DEVICE_OFFLINE:
            return MaintenanceType.CORRECTIVE
        elif alert.alert_type == AlertType.CALIBRATION_DUE:
            return MaintenanceType.CALIBRATION
        elif alert.alert_type == AlertType.MAINTENANCE_DUE:
            return MaintenanceType.PREVENTIVE
        else:
            return MaintenanceType.INSPECTION
    
    def _get_priority_from_alert(self, alert: Alert) -> MaintenancePriority:
        """Determina a prioridade com base no alerta"""
        if alert.severity == AlertSeverity.CRITICAL:
            return MaintenancePriority.CRITICAL
        elif alert.severity == AlertSeverity.HIGH:
            return MaintenancePriority.HIGH
        elif alert.severity == AlertSeverity.MEDIUM:
            return MaintenancePriority.MEDIUM
        else:
            return MaintenancePriority.LOW
    
    def _get_scheduled_start_from_alert(self, alert: Alert) -> datetime:
        """Determina a data de inicio com base no alerta"""
        # Para alertas criticos, agendar para agora
        if alert.severity == AlertSeverity.CRITICAL:
            return datetime.utcnow()
        
        # Para alertas altos, agendar para hoje
        if alert.severity == AlertSeverity.HIGH:
            return datetime.utcnow()
        
        # Para outros alertas, agendar para amanha
        return datetime.utcnow() + timedelta(days=1)
    
    # ==================== Agendamento Automatico ====================
    
    def schedule_predictive_maintenance(self, machine_id: str) -> List[Maintenance]:
        """Agenda manutencao preditiva para uma maquina"""
        try:
            logger.info(f"Agendando manutencao preditiva para maquina {machine_id}")
            
            # Executar predicoes
            failure_predictions = self.prediction_handler.predict_failures(machine_id)
            rul_predictions = self.prediction_handler.predict_rul(machine_id)
            anomaly_predictions = self.prediction_handler.detect_anomalies(machine_id)
            
            # Agendar manutencao para cada predicao
            maintenances = []
            
            for prediction in failure_predictions + rul_predictions + anomaly_predictions:
                maintenance = self.schedule_maintenance_from_prediction(prediction)
                if maintenance:
                    maintenances.append(maintenance)
            
            logger.info(f"Manutencoes preditivas agendadas para maquina {machine_id}: {len(maintenances)}")
            return maintenances
            
        except Exception as e:
            logger.error(f"Erro ao agendar manutencao preditiva para maquina {machine_id}: {e}")
            return []
    
    def schedule_preventive_maintenance(self, machine_id: str) -> Optional[Maintenance]:
        """Agenda manutencao preventiva para uma maquina"""
        try:
            logger.info(f"Agendando manutencao preventiva para maquina {machine_id}")
            
            # Obter dados da maquina (simplificado)
            # Em um sistema real, buscar informacoes da maquina
            
            # Criar manutencao preventiva
            maintenance_data = {
                'maintenance_type': MaintenanceType.PREVENTIVE.value,
                'priority': MaintenancePriority.MEDIUM.value,
                'machine_id': machine_id,
                'scheduled_start': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'scheduled_end': (datetime.utcnow() + timedelta(days=30, hours=4)).isoformat(),
                'title': f"Manutencao preventiva - {machine_id}",
                'description': "Manutencao preventiva agendada para verificacao geral do equipamento",
                'estimated_duration': 4.0,
                'recommended_actions': [
                    "Verificar nivel de oleo e lubrificacao",
                    "Inspecionar componentes criticos",
                    "Testar sistemas de seguranca",
                    "Calibrar sensores se necessario"
                ],
                'source': 'preventive',
                'tags': ['preventive', 'scheduled']
            }
            
            maintenance = self.create_maintenance(maintenance_data)
            
            logger.info(f"Manutencao preventiva agendada para maquina {machine_id}")
            return maintenance
            
        except Exception as e:
            logger.error(f"Erro ao agendar manutencao preventiva para maquina {machine_id}: {e}")
            return None
    
    # ==================== Execucao de Manutencao ====================
    
    def start_maintenance(self, maintenance_id: str, user_id: str) -> bool:
        """Inicia uma manutencao"""
        try:
            maintenance = self.get_maintenance(maintenance_id)
            if maintenance is None:
                return False
            
            # Atualizar status
            maintenance.status = MaintenanceStatus.IN_PROGRESS
            maintenance.actual_start = datetime.utcnow()
            maintenance.assigned_to = user_id
            maintenance.updated_at = datetime.utcnow()
            
            # Atualizar manutencao
            self.update_maintenance(maintenance_id, {
                'status': MaintenanceStatus.IN_PROGRESS.value,
                'actual_start': maintenance.actual_start.isoformat(),
                'assigned_to': user_id
            })
            
            # Atualizar status da maquina
            if maintenance.machine_id:
                self._update_machine_status_during_maintenance(maintenance.machine_id)
            
            logger.info(f"Manutencao {maintenance_id} iniciada por {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar manutencao {maintenance_id}: {e}")
            return False
    
    def complete_maintenance(self, maintenance_id: str, user_id: str, 
                            actions_performed: List[str], parts_replaced: List[str],
                            materials_used: List[str], labor_cost: Optional[float] = None,
                            material_cost: Optional[float] = None, root_cause: Optional[str] = None,
                            effectiveness: Optional[float] = None, notes: Optional[str] = None) -> bool:
        """Conclui uma manutencao"""
        try:
            maintenance = self.get_maintenance(maintenance_id)
            if maintenance is None:
                return False
            
            # Atualizar dados da manutencao
            maintenance.status = MaintenanceStatus.COMPLETED
            maintenance.actual_end = datetime.utcnow()
            maintenance.actual_duration = (maintenance.actual_end - maintenance.actual_start).total_seconds() / 3600
            maintenance.actions_performed = actions_performed
            maintenance.parts_replaced = parts_replaced
            maintenance.materials_used = materials_used
            maintenance.labor_cost = labor_cost
            maintenance.material_cost = material_cost
            maintenance.total_cost = (labor_cost or 0) + (material_cost or 0)
            maintenance.root_cause = root_cause
            maintenance.effectiveness = effectiveness
            maintenance.notes = notes
            maintenance.updated_at = datetime.utcnow()
            
            # Atualizar manutencao
            update_data = {
                'status': MaintenanceStatus.COMPLETED.value,
                'actual_end': maintenance.actual_end.isoformat(),
                'actions_performed': actions_performed,
                'parts_replaced': parts_replaced,
                'materials_used': materials_used
            }
            
            if labor_cost is not None:
                update_data['labor_cost'] = labor_cost
            if material_cost is not None:
                update_data['material_cost'] = material_cost
            if root_cause:
                update_data['root_cause'] = root_cause
            if effectiveness is not None:
                update_data['effectiveness'] = effectiveness
            if notes:
                update_data['notes'] = notes
            
            self.update_maintenance(maintenance_id, update_data)
            
            logger.info(f"Manutencao {maintenance_id} concluida por {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao concluir manutencao {maintenance_id}: {e}")
            return False
    
    def cancel_maintenance(self, maintenance_id: str, user_id: str, reason: Optional[str] = None) -> bool:
        """Cancela uma manutencao"""
        try:
            maintenance = self.get_maintenance(maintenance_id)
            if maintenance is None:
                return False
            
            # Atualizar status
            maintenance.status = MaintenanceStatus.CANCELLED
            maintenance.updated_at = datetime.utcnow()
            
            if reason:
                maintenance.notes = reason
            
            # Atualizar manutencao
            update_data = {
                'status': MaintenanceStatus.CANCELLED.value
            }
            if reason:
                update_data['notes'] = reason
            
            self.update_maintenance(maintenance_id, update_data)
            
            logger.info(f"Manutencao {maintenance_id} cancelada por {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cancelar manutencao {maintenance_id}: {e}")
            return False
    
    # ==================== Atualizacao de Status ====================
    
    def _update_machine_status_after_maintenance(self, machine_id: str) -> bool:
        """Atualiza o status da maquina apos manutencao"""
        try:
            # Em um sistema real, atualizar status no IoT
            # Para simplificacao, apenas log
            logger.info(f"Atualizando status da maquina {machine_id} apos manutencao")
            
            # Obter maquina (simplificado)
            # machine = self.iot_service.get_machine(machine_id)
            # if machine:
            #     machine.status = MachineStatus.OPERATIONAL
            #     self.iot_service.update_machine(machine)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status da maquina {machine_id} apos manutencao: {e}")
            return False
    
    def _update_machine_status_during_maintenance(self, machine_id: str) -> bool:
        """Atualiza o status da maquina durante manutencao"""
        try:
            logger.info(f"Atualizando status da maquina {machine_id} para manutencao")
            
            # Em um sistema real, atualizar status no IoT
            # machine = self.iot_service.get_machine(machine_id)
            # if machine:
            #     machine.status = MachineStatus.MAINTENANCE
            #     self.iot_service.update_machine(machine)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status da maquina {machine_id} durante manutencao: {e}")
            return False
    
    # ==================== Notificacoes ====================
    
    def _notify_maintenance_created(self, maintenance: Maintenance) -> bool:
        """Notifica sobre criacao de manutencao"""
        try:
            # Notificar equipe de manutencao
            logger.info(f"Notificando sobre criacao da manutencao {maintenance.id}")
            
            # Em um sistema real, enviar email ou notificacao
            # self._send_email_notification(
            #     users=['manutencao@empresa.com'],
            #     message={'type': 'maintenance_created', 'maintenance': maintenance.to_dict()}
            # )
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao notificar sobre criacao da manutencao {maintenance.id}: {e}")
            return False
    
    def _notify_maintenance_updated(self, maintenance: Maintenance) -> bool:
        """Notifica sobre atualizacao de manutencao"""
        try:
            logger.info(f"Notificando sobre atualizacao da manutencao {maintenance.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao notificar sobre atualizacao da manutencao {maintenance.id}: {e}")
            return False
    
    def _notify_maintenance_completed(self, maintenance: Maintenance) -> bool:
        """Notifica sobre conclusao de manutencao"""
        try:
            logger.info(f"Notificando sobre conclusao da manutencao {maintenance.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao notificar sobre conclusao da manutencao {maintenance.id}: {e}")
            return False
    
    def _notify_maintenance_cancelled(self, maintenance: Maintenance) -> bool:
        """Notifica sobre cancelamento de manutencao"""
        try:
            logger.info(f"Notificando sobre cancelamento da manutencao {maintenance.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao notificar sobre cancelamento da manutencao {maintenance.id}: {e}")
            return False
    
    # ==================== Metricas ====================
    
    def get_maintenance_metrics(self) -> Dict:
        """Obtem metricas de manutencao"""
        try:
            maintenances = list(self.maintenance_cache.values())
            
            # Contar por tipo
            type_counts = {}
            for maintenance_type in MaintenanceType:
                type_counts[maintenance_type.value] = sum(
                    1 for m in maintenances if m.maintenance_type == maintenance_type
                )
            
            # Contar por status
            status_counts = {}
            for status in MaintenanceStatus:
                status_counts[status.value] = sum(
                    1 for m in maintenances if m.status == status
                )
            
            # Contar por prioridade
            priority_counts = {}
            for priority in MaintenancePriority:
                priority_counts[priority.value] = sum(
                    1 for m in maintenances if m.priority == priority
                )
            
            # Contar por maquina
            machine_counts = {}
            for m in maintenances:
                if m.machine_id:
                    machine_counts[m.machine_id] = machine_counts.get(m.machine_id, 0) + 1
            
            # Manutencoes concluidas
            completed_maintenances = [m for m in maintenances if m.status == MaintenanceStatus.COMPLETED]
            
            # Tempo medio de manutencao
            durations = [
                m.actual_duration for m in completed_maintenances 
                if m.actual_duration is not None
            ]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Custo medio de manutencao
            costs = [
                m.total_cost for m in completed_maintenances 
                if m.total_cost is not None
            ]
            avg_cost = sum(costs) / len(costs) if costs else 0
            
            return {
                'total_maintenances': len(maintenances),
                'by_type': type_counts,
                'by_status': status_counts,
                'by_priority': priority_counts,
                'by_machine': machine_counts,
                'completed_count': len(completed_maintenances),
                'avg_duration_hours': avg_duration,
                'avg_cost_brl': avg_cost,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter metricas de manutencao: {e}")
            return {}
    
    def get_maintenance_summary(self, machine_id: str) -> Dict:
        """Obtem um resumo de manutencao para uma maquina"""
        try:
            maintenances = self.list_maintenances(machine_id=machine_id, limit=50)
            
            if not maintenances:
                return {
                    'machine_id': machine_id,
                    'total_maintenances': 0
                }
            
            # Obter proxima manutencao
            next_maintenance = None
            for m in maintenances:
                if m.status == MaintenanceStatus.SCHEDULED:
                    if next_maintenance is None or m.scheduled_start < next_maintenance.scheduled_start:
                        next_maintenance = m
            
            # Obter ultima manutencao concluida
            last_completed = None
            for m in maintenances:
                if m.status == MaintenanceStatus.COMPLETED:
                    if last_completed is None or m.actual_end > last_completed.actual_end:
                        last_completed = m
            
            # Calcular tempo desde a ultima manutencao
            time_since_last = None
            if last_completed and last_completed.actual_end:
                time_since_last = (datetime.utcnow() - last_completed.actual_end).total_seconds() / (24 * 3600)
            
            # Calcular tempo ate a proxima manutencao
            time_until_next = None
            if next_maintenance and next_maintenance.scheduled_start:
                time_until_next = (next_maintenance.scheduled_start - datetime.utcnow()).total_seconds() / (24 * 3600)
            
            return {
                'machine_id': machine_id,
                'total_maintenances': len(maintenances),
                'next_maintenance': {
                    'id': next_maintenance.id,
                    'type': next_maintenance.maintenance_type.value if next_maintenance else None,
                    'priority': next_maintenance.priority.value if next_maintenance else None,
                    'scheduled_start': next_maintenance.scheduled_start.isoformat() if next_maintenance else None,
                    'days_until_next': time_until_next
                } if next_maintenance else None,
                'last_completed': {
                    'id': last_completed.id,
                    'type': last_completed.maintenance_type.value if last_completed else None,
                    'actual_end': last_completed.actual_end.isoformat() if last_completed and last_completed.actual_end else None,
                    'days_since_last': time_since_last
                } if last_completed else None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de manutencao para maquina {machine_id}: {e}")
            return {}
    
    # ==================== Agendamento Automatico ====================
    
    def schedule_all_maintenance(self) -> bool:
        """Agenda manutencao para todas as maquinas"""
        try:
            logger.info("Agendando manutencao para todas as maquinas")
            
            # Em um sistema real, obter lista de maquinas
            # Para demonstracao, usar maquinas conhecidas
            machine_ids = ['machine-001', 'machine-002', 'machine-003']
            
            for machine_id in machine_ids:
                # Agendar manutencao preditiva
                self.schedule_predictive_maintenance(machine_id)
                
                # Agendar manutencao preventiva
                self.schedule_preventive_maintenance(machine_id)
            
            logger.info("Manutencoes agendadas para todas as maquinas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao agendar manutencoes: {e}")
            return False
