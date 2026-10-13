"""
CORETHREE3 - DNA de Maquinas
Handler de IoT

Handler para gerenciamento de dispositivos IoT e comunicacao MQTT.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..config.iot_config import iot_config
from ..models.device import Device, DeviceStatus, DeviceType
from ..models.sensor import Sensor, SensorStatus, SensorType
from ..models.reading import Reading, ReadingBatch, ReadingMetadata, ReadingQuality
from ..services.iot_service import IoTService

logger = logging.getLogger(__name__)


class IoTHandler:
    """
    Handler de IoT para processamento de mensagens MQTT e gerenciamento de dispositivos.
    
    Responsabilidades:
    - Processamento de mensagens MQTT de dispositivos
    - Gerenciamento de conexoes de dispositivos
    - Processamento de comandos
    - Sincronizacao de estado
    """
    
    def __init__(self):
        """Inicializa o handler de IoT"""
        self.iot_service = IoTService()
        self.device_cache: Dict[str, Device] = {}
        self.sensor_cache: Dict[str, Sensor] = {}
    
    # ==================== Processamento de Mensagens MQTT ====================
    
    def process_message(self, topic: str, message: Dict) -> bool:
        """Processa uma mensagem MQTT"""
        try:
            logger.info(f"Processando mensagem do topico {topic}")
            
            # Determinar tipo da mensagem com base no topico
            if 'data' in topic:
                return self.process_data_message(message)
            elif 'alerts' in topic:
                return self.process_alert_message(message)
            elif 'commands' in topic:
                return self.process_command_message(message)
            elif 'status' in topic:
                return self.process_status_message(message)
            elif 'heartbeat' in topic:
                return self.process_heartbeat_message(message)
            elif 'shadow' in topic:
                return self.process_shadow_message(message)
            else:
                logger.warning(f"Topico desconhecido: {topic}")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem do topico {topic}: {e}")
            return False
    
    def process_data_message(self, message: Dict) -> bool:
        """Processa uma mensagem de dados de sensor"""
        try:
            # Verificar se e um batch ou leitura individual
            if 'readings' in message:
                return self.process_reading_batch(message)
            else:
                return self.process_single_reading(message)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de dados: {e}")
            return False
    
    def process_single_reading(self, message: Dict) -> bool:
        """Processa uma leitura individual"""
        try:
            # Parse da leitura
            reading = self._parse_reading(message)
            if reading is None:
                return False
            
            # Validar leitura
            if not self._validate_reading(reading):
                logger.warning(f"Leitura invalida: {reading.id}")
                return False
            
            # Atualizar dispositivo e sensor
            if reading.metadata.device_id:
                self._update_device_last_data(reading.metadata.device_id)
            if reading.metadata.sensor_id:
                self._update_sensor_last_reading(reading.metadata.sensor_id)
            
            # Processar leitura (passar para o DataHandler)
            from .data_handler import DataHandler
            data_handler = DataHandler()
            return data_handler.process_reading(reading)
            
        except Exception as e:
            logger.error(f"Erro ao processar leitura {message.get('id')}: {e}")
            return False
    
    def process_reading_batch(self, message: Dict) -> bool:
        """Processa um batch de leituras"""
        try:
            # Parse do batch
            batch = self._parse_reading_batch(message)
            if batch is None:
                return False
            
            # Atualizar dispositivo
            if batch.device_id:
                self._update_device_last_data(batch.device_id)
            
            # Processar batch (passar para o DataHandler)
            from .data_handler import DataHandler
            data_handler = DataHandler()
            return data_handler.process_reading_batch(batch)
            
        except Exception as e:
            logger.error(f"Erro ao processar batch {message.get('id')}: {e}")
            return False
    
    def _parse_reading(self, message: Dict) -> Optional[Reading]:
        """Analisa uma leitura a partir de uma mensagem"""
        try:
            # Extrair metadados
            metadata = ReadingMetadata(
                sensor_id=message.get('sensor_id', ''),
                device_id=message.get('device_id', ''),
                machine_id=message.get('machine_id', ''),
                timestamp=datetime.fromisoformat(message.get('timestamp'))
                    if message.get('timestamp') else datetime.utcnow(),
                received_at=datetime.utcnow(),
                quality=ReadingQuality(message.get('quality', 'good')),
                confidence=message.get('confidence'),
                batch_id=message.get('batch_id'),
                sequence_number=message.get('sequence_number', 0),
                axis=message.get('axis'),
                location=message.get('location'),
                is_calibrated=message.get('is_calibrated', True),
                calibration_factor=message.get('calibration_factor')
            )
            
            # Criar leitura
            reading = Reading(
                id=message.get('id', f"reading-{datetime.utcnow().isoformat()}"),
                value=message.get('value', 0.0),
                unit=message.get('unit', ''),
                metadata=metadata,
                additional_values=message.get('additional_values', {}),
                rms=message.get('rms'),
                peak=message.get('peak'),
                frequency=message.get('frequency'),
                threshold_violated=message.get('threshold_violated'),
                threshold_value=message.get('threshold_value'),
                is_processed=False,
                is_anomaly=message.get('is_anomaly', False),
                anomaly_score=message.get('anomaly_score'),
                created_at=datetime.utcnow()
            )
            
            return reading
            
        except Exception as e:
            logger.error(f"Erro ao analisar leitura: {e}")
            return None
    
    def _parse_reading_batch(self, message: Dict) -> Optional[ReadingBatch]:
        """Analisa um batch de leituras a partir de uma mensagem"""
        try:
            readings = []
            for reading_data in message.get('readings', []):
                reading = self._parse_reading(reading_data)
                if reading:
                    readings.append(reading)
            
            if not readings:
                return None
            
            # Criar batch
            batch = ReadingBatch(
                id=message.get('id', f"batch-{datetime.utcnow().isoformat()}"),
                device_id=message.get('device_id', ''),
                machine_id=message.get('machine_id', ''),
                readings=readings,
                timestamp=datetime.fromisoformat(message.get('timestamp'))
                    if message.get('timestamp') else datetime.utcnow(),
                received_at=datetime.utcnow(),
                is_compressed=message.get('is_compressed', False),
                compression_ratio=message.get('compression_ratio'),
                original_size=message.get('original_size'),
                compressed_size=message.get('compressed_size'),
                is_processed=False,
                created_at=datetime.utcnow()
            )
            
            return batch
            
        except Exception as e:
            logger.error(f"Erro ao analisar batch: {e}")
            return None
    
    def _validate_reading(self, reading: Reading) -> bool:
        """Valida uma leitura"""
        if reading.value is None:
            return False
        if reading.metadata.sensor_id is None:
            return False
        if reading.metadata.timestamp is None:
            return False
        return True
    
    def process_alert_message(self, message: Dict) -> bool:
        """Processa uma mensagem de alerta"""
        try:
            # Passar para o AlertHandler
            from .alert_handler import AlertHandler
            alert_handler = AlertHandler()
            return alert_handler.process_alert_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de alerta: {e}")
            return False
    
    def process_command_message(self, message: Dict) -> bool:
        """Processa uma mensagem de comando"""
        try:
            device_id = message.get('device_id')
            command = message.get('command')
            
            if not device_id or not command:
                logger.warning("Mensagem de comando invalida")
                return False
            
            # Executar comando no dispositivo
            return self.execute_command(device_id, command, message.get('parameters', {}))
            
        except Exception as e:
            logger.error(f"Erro ao processar comando para {device_id}: {e}")
            return False
    
    def process_status_message(self, message: Dict) -> bool:
        """Processa uma mensagem de status"""
        try:
            device_id = message.get('device_id')
            status = message.get('status')
            
            if not device_id or not status:
                logger.warning("Mensagem de status invalida")
                return False
            
            # Atualizar status do dispositivo
            device = self.iot_service.get_device(device_id)
            if device is None:
                logger.warning(f"Dispositivo {device_id} nao encontrado")
                return False
            
            # Atualizar status
            try:
                new_status = DeviceStatus(status)
                device.status = new_status
                device.last_heartbeat = datetime.utcnow()
                
                self.iot_service.update_device(device)
                
                logger.info(f"Status do dispositivo {device_id} atualizado para {status}")
                return True
                
            except ValueError as e:
                logger.warning(f"Status invalido: {status}")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao processar status para {device_id}: {e}")
            return False
    
    def process_heartbeat_message(self, message: Dict) -> bool:
        """Processa uma mensagem de heartbeat"""
        try:
            device_id = message.get('device_id')
            
            if not device_id:
                logger.warning("Mensagem de heartbeat invalida")
                return False
            
            # Atualizar heartbeat do dispositivo
            device = self.iot_service.get_device(device_id)
            if device is None:
                logger.warning(f"Dispositivo {device_id} nao encontrado")
                return False
            
            device.last_heartbeat = datetime.utcnow()
            device.last_connection = datetime.utcnow()
            
            # Se o dispositivo estava offline, atualizar status
            if device.status != DeviceStatus.ONLINE:
                device.status = DeviceStatus.ONLINE
            
            self.iot_service.update_device(device)
            
            logger.info(f"Heartbeat do dispositivo {device_id} processado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar heartbeat para {device_id}: {e}")
            return False
    
    def process_shadow_message(self, message: Dict) -> bool:
        """Processa uma mensagem de shadow"""
        try:
            device_id = message.get('device_id')
            shadow_state = message.get('state')
            
            if not device_id or not shadow_state:
                logger.warning("Mensagem de shadow invalida")
                return False
            
            # Atualizar shadow do dispositivo
            device = self.iot_service.get_device(device_id)
            if device is None:
                logger.warning(f"Dispositivo {device_id} nao encontrado")
                return False
            
            # Atualizar shadow
            self.iot_service.update_thing_shadow(device_id, shadow_state)
            
            logger.info(f"Shadow do dispositivo {device_id} atualizado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar shadow para {device_id}: {e}")
            return False
    
    # ==================== Gerenciamento de Dispositivos ====================
    
    def register_device(self, device_data: Dict) -> Optional[Device]:
        """Registra um novo dispositivo"""
        try:
            # Parse do dispositivo
            device = self._parse_device(device_data)
            if device is None:
                return None
            
            # Criar dispositivo no IoT Core
            device = self.iot_service.create_device(device)
            
            # Cache
            self.device_cache[device.id] = device
            
            logger.info(f"Dispositivo {device.id} registrado com sucesso")
            return device
            
        except Exception as e:
            logger.error(f"Erro ao registrar dispositivo: {e}")
            return None
    
    def _parse_device(self, data: Dict) -> Optional[Device]:
        """Analisa um dispositivo a partir de dados"""
        try:
            # Parse de metadados
            metadata = {
                'manufacturer': data.get('manufacturer', ''),
                'model': data.get('model', ''),
                'serial_number': data.get('serial_number', ''),
                'firmware_version': data.get('firmware_version', '1.0.0'),
                'hardware_version': data.get('hardware_version', '1.0'),
                'location': data.get('location', ''),
                'installation_date': datetime.fromisoformat(data.get('installation_date'))
                    if data.get('installation_date') else None
            }
            
            # Criar dispositivo
            device = Device(
                id=data.get('id', f"device-{datetime.utcnow().isoformat()}"),
                name=data.get('name', ''),
                device_type=DeviceType(data.get('device_type', 'generic')),
                status=DeviceStatus(data.get('status', 'offline')),
                machine_id=data.get('machine_id'),
                parent_device_id=data.get('parent_device_id'),
                child_device_ids=data.get('child_device_ids', []),
                metadata=metadata,
                sampling_rate=data.get('sampling_rate', 10),
                batch_interval=data.get('batch_interval', 60),
                sensor_ids=data.get('sensor_ids', []),
                critical_sensors=data.get('critical_sensors', []),
                iot_thing_name=data.get('iot_thing_name', f"{iot_config.IOT_THING_NAME_PREFIX}{data.get('id', '')}"),
                iot_endpoint=aws_config.IOT_ENDPOINT,
                last_heartbeat=datetime.utcnow() if data.get('is_online', False) else None,
                last_data_received=datetime.utcnow() if data.get('is_online', False) else None,
                last_connection=datetime.utcnow() if data.get('is_online', False) else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return device
            
        except Exception as e:
            logger.error(f"Erro ao analisar dispositivo: {e}")
            return None
    
    def register_sensor(self, sensor_data: Dict) -> Optional[Sensor]:
        """Registra um novo sensor"""
        try:
            # Parse do sensor
            sensor = self._parse_sensor(sensor_data)
            if sensor is None:
                return None
            
            # Criar sensor
            sensor = self.iot_service.create_sensor(sensor)
            
            # Cache
            self.sensor_cache[sensor.id] = sensor
            
            # Adicionar sensor ao dispositivo
            if sensor.device_id:
                device = self.iot_service.get_device(sensor.device_id)
                if device and sensor.id not in device.sensor_ids:
                    device.sensor_ids.append(sensor.id)
                    self.iot_service.update_device(device)
            
            logger.info(f"Sensor {sensor.id} registrado com sucesso")
            return sensor
            
        except Exception as e:
            logger.error(f"Erro ao registrar sensor: {e}")
            return None
    
    def _parse_sensor(self, data: Dict) -> Optional[Sensor]:
        """Analisa um sensor a partir de dados"""
        try:
            # Parse de calibracao
            calibration = {
                'last_calibration': datetime.fromisoformat(data.get('calibration', {}).get('last_calibration'))
                    if data.get('calibration', {}).get('last_calibration') else None,
                'next_calibration': datetime.fromisoformat(data.get('calibration', {}).get('next_calibration'))
                    if data.get('calibration', {}).get('next_calibration') else None,
                'calibration_certificate': data.get('calibration', {}).get('calibration_certificate'),
                'calibration_technician': data.get('calibration', {}).get('calibration_technician'),
                'calibration_notes': data.get('calibration', {}).get('calibration_notes'),
                'offset': data.get('calibration', {}).get('offset'),
                'gain': data.get('calibration', {}).get('gain'),
                'scale_factor': data.get('calibration', {}).get('scale_factor'),
                'is_calibrated': data.get('calibration', {}).get('is_calibrated', False),
                'calibration_accuracy': data.get('calibration', {}).get('calibration_accuracy')
            }
            
            # Criar sensor
            sensor = Sensor(
                id=data.get('id', f"sensor-{datetime.utcnow().isoformat()}"),
                name=data.get('name', ''),
                sensor_type=SensorType(data.get('sensor_type', 'vibration')),
                status=SensorStatus(data.get('status', 'inactive')),
                device_id=data.get('device_id'),
                machine_id=data.get('machine_id'),
                manufacturer=data.get('manufacturer', ''),
                model=data.get('model', ''),
                serial_number=data.get('serial_number', ''),
                units=data.get('units', []),
                primary_unit=data.get('primary_unit', ''),
                sampling_rate=data.get('sampling_rate', 10),
                batch_interval=data.get('batch_interval', 60),
                min_value=data.get('min_value'),
                max_value=data.get('max_value'),
                threshold_critical=data.get('threshold_critical'),
                threshold_high=data.get('threshold_high'),
                threshold_medium=data.get('threshold_medium'),
                threshold_low=data.get('threshold_low'),
                accuracy=data.get('accuracy'),
                resolution=data.get('resolution'),
                calibration=calibration,
                location=data.get('location', ''),
                axis=data.get('axis'),
                interface_type=data.get('interface_type'),
                connection_status=data.get('connection_status', False),
                last_reading=datetime.utcnow() if data.get('is_active', False) else None,
                total_readings=data.get('total_readings', 0),
                failed_readings=data.get('failed_readings', 0),
                last_value=data.get('last_value'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return sensor
            
        except Exception as e:
            logger.error(f"Erro ao analisar sensor: {e}")
            return None
    
    # ==================== Execucao de Comandos ====================
    
    def execute_command(self, device_id: str, command: str, parameters: Dict) -> bool:
        """Executa um comando em um dispositivo"""
        try:
            # Obter dispositivo
            device = self.iot_service.get_device(device_id)
            if device is None:
                logger.warning(f"Dispositivo {device_id} nao encontrado")
                return False
            
            # Validar comando
            if not self._validate_command(command):
                logger.warning(f"Comando invalido: {command}")
                return False
            
            # Preparar mensagem de comando
            command_message = {
                'device_id': device_id,
                'command': command,
                'parameters': parameters,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Publicar comando no MQTT
            topic = iot_config.get_mqtt_topic("commands")
            
            # Usar IoT Service para publicar
            self.iot_service.publish_command(device_id, command_message)
            
            logger.info(f"Comando {command} executado no dispositivo {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar comando {command} em {device_id}: {e}")
            return False
    
    def _validate_command(self, command: str) -> bool:
        """Valida um comando"""
        valid_commands = [
            'start',
            'stop',
            'restart',
            'calibrate',
            'reset',
            'update_firmware',
            'set_sampling_rate',
            'set_batch_interval',
            'enable_sensor',
            'disable_sensor',
            'get_status',
            'get_readings',
            'get_diagnostics'
        ]
        
        return command in valid_commands
    
    # ==================== Atualizacoes de Estado ====================
    
    def _update_device_last_data(self, device_id: str) -> bool:
        """Atualiza o timestamp da ultima leitura de um dispositivo"""
        try:
            device = self.iot_service.get_device(device_id)
            if device is None:
                return False
            
            device.last_data_received = datetime.utcnow()
            device.updated_at = datetime.utcnow()
            
            # Se o dispositivo estava offline, atualizar status
            if device.status != DeviceStatus.ONLINE:
                device.status = DeviceStatus.ONLINE
            
            self.iot_service.update_device(device)
            
            # Cache
            self.device_cache[device_id] = device
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar ultima leitura do dispositivo {device_id}: {e}")
            return False
    
    def _update_sensor_last_reading(self, sensor_id: str) -> bool:
        """Atualiza o timestamp da ultima leitura de um sensor"""
        try:
            sensor = self.iot_service.get_sensor(sensor_id)
            if sensor is None:
                return False
            
            sensor.last_reading = datetime.utcnow()
            sensor.total_readings += 1
            sensor.updated_at = datetime.utcnow()
            
            # Se o sensor estava inativo, atualizar status
            if sensor.status != SensorStatus.ACTIVE:
                sensor.status = SensorStatus.ACTIVE
            
            self.iot_service.update_sensor(sensor)
            
            # Cache
            self.sensor_cache[sensor_id] = sensor
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar ultima leitura do sensor {sensor_id}: {e}")
            return False
    
    # ==================== Monitoramento ====================
    
    def check_device_health(self, device_id: str) -> Dict:
        """Verifica a saude de um dispositivo"""
        try:
            device = self.iot_service.get_device(device_id)
            if device is None:
                return {'status': 'error', 'message': 'Dispositivo nao encontrado'}
            
            # Verificar status
            if device.status != DeviceStatus.ONLINE:
                return {
                    'status': 'offline',
                    'last_heartbeat': device.last_heartbeat,
                    'last_connection': device.last_connection
                }
            
            # Verificar heartbeat
            now = datetime.utcnow()
            heartbeat_age = (now - device.last_heartbeat).total_seconds() / 60 if device.last_heartbeat else None
            
            if heartbeat_age is None or heartbeat_age > 10:  # 10 minutos
                return {
                    'status': 'heartbeat_timeout',
                    'heartbeat_age_minutes': heartbeat_age
                }
            
            # Verificar dados
            data_age = (now - device.last_data_received).total_seconds() / 60 if device.last_data_received else None
            
            if data_age is None or data_age > 30:  # 30 minutos
                return {
                    'status': 'data_timeout',
                    'data_age_minutes': data_age
                }
            
            # Verificar erros
            error_rate = device.get_error_rate()
            if error_rate > 0.1:  # 10% de erros
                return {
                    'status': 'high_error_rate',
                    'error_rate': error_rate
                }
            
            return {
                'status': 'healthy',
                'heartbeat_age_minutes': heartbeat_age,
                'data_age_minutes': data_age,
                'error_rate': error_rate
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar saude do dispositivo {device_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def check_sensor_health(self, sensor_id: str) -> Dict:
        """Verifica a saude de um sensor"""
        try:
            sensor = self.iot_service.get_sensor(sensor_id)
            if sensor is None:
                return {'status': 'error', 'message': 'Sensor nao encontrado'}
            
            # Verificar status
            if sensor.status != SensorStatus.ACTIVE:
                return {'status': 'inactive'}
            
            # Verificar conexao
            if not sensor.connection_status:
                return {'status': 'disconnected'}
            
            # Verificar calibracao
            if sensor.needs_calibration():
                return {'status': 'needs_calibration'}
            
            # Verificar taxa de falhas
            if sensor.total_readings > 0:
                failure_rate = sensor.failed_readings / sensor.total_readings
                if failure_rate > 0.1:  # 10% de falhas
                    return {
                        'status': 'high_failure_rate',
                        'failure_rate': failure_rate
                    }
            
            return {'status': 'healthy'}
            
        except Exception as e:
            logger.error(f"Erro ao verificar saude do sensor {sensor_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_system_status(self) -> Dict:
        """Obtem o status do sistema"""
        try:
            # Obter metricas do IoT
            iot_metrics = self.iot_service.get_system_metrics()
            
            # Obter metricas de alertas
            from .alert_handler import AlertHandler
            alert_handler = AlertHandler()
            alert_metrics = alert_handler.get_alert_metrics()
            
            return {
                'iot': iot_metrics,
                'alerts': alert_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do sistema: {e}")
            return {'status': 'error', 'message': str(e)}
