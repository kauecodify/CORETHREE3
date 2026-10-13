"""
CORETHREE3 - DNA de Maquinas
Servico de IoT

Servico para gerenciamento de dispositivos IoT e comunicacao com AWS IoT Core.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import ClientError

from ..config.aws_config import aws_config
from ..config.iot_config import IoTConfig, iot_config
from ..models.device import Device, DeviceStatus, DeviceType
from ..models.sensor import Sensor, SensorStatus, SensorType
from ..models.reading import Reading, ReadingBatch, ReadingMetadata, ReadingQuality

logger = logging.getLogger(__name__)


class IoTService:
    """
    Servico de IoT para gerenciamento de dispositivos e sensores.
    
    Responsabilidades:
    - Gerenciamento de dispositivos IoT
    - Gerenciamento de sensores
    - Publicacao e subscrição de mensagens MQTT
    - Gerenciamento de certificados e politicas
    """
    
    def __init__(self):
        """Inicializa o servico de IoT"""
        self.iot_client = None
        self._initialize_client()
        self.device_cache: Dict[str, Device] = {}
        self.sensor_cache: Dict[str, Sensor] = {}
    
    def _initialize_client(self):
        """Inicializa o cliente AWS IoT"""
        try:
            self.iot_client = boto3.client(
                'iot',
                region_name=aws_config.REGION,
                aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY
            )
            logger.info("Cliente AWS IoT inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente AWS IoT: {e}")
            raise
    
    def get_client(self):
        """Retorna o cliente AWS IoT"""
        if self.iot_client is None:
            self._initialize_client()
        return self.iot_client
    
    # ==================== Gerenciamento de Dispositivos ====================
    
    def create_device(self, device: Device) -> Device:
        """Cria um novo dispositivo IoT"""
        try:
            # Criar Thing no AWS IoT
            thing_name = device.iot_thing_name or f"{iot_config.IOT_THING_NAME_PREFIX}{device.id}"
            
            response = self.get_client().create_thing(
                thingName=thing_name,
                thingTypeName=iot_config.IOT_THING_TYPE,
                attributePayload={
                    'attributes': {
                        'device_id': device.id,
                        'device_type': device.device_type.value,
                        'machine_id': device.machine_id or '',
                        'name': device.name,
                        'status': device.status.value
                    }
                }
            )
            
            device.iot_thing_name = thing_name
            device.iot_thing_arn = response['thingArn']
            
            # Criar certificado
            cert_response = self.get_client().create_keys_and_certificate(
                setAsActive=True
            )
            
            device.iot_certificate_id = cert_response['certificateId']
            device.iot_endpoint = aws_config.IOT_ENDPOINT
            
            # Anexar certificado a Thing
            self.get_client().attach_thing_principal(
                thingName=thing_name,
                principal=cert_response['certificateArn']
            )
            
            # Anexar politica
            self.get_client().attach_policy(
                policyName=iot_config.DEFAULT_POLICY_NAME,
                target=cert_response['certificateArn']
            )
            
            # Cache
            self.device_cache[device.id] = device
            
            logger.info(f"Dispositivo {device.id} criado com sucesso no AWS IoT")
            return device
            
        except ClientError as e:
            logger.error(f"Erro ao criar dispositivo {device.id}: {e}")
            raise
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Obtem um dispositivo pelo ID"""
        # Verificar cache
        if device_id in self.device_cache:
            return self.device_cache[device_id]
        
        try:
            # Obter Thing do AWS IoT
            thing_name = f"{iot_config.IOT_THING_NAME_PREFIX}{device_id}"
            response = self.get_client().describe_thing(
                thingName=thing_name
            )
            
            attributes = response.get('attributes', {})
            device = Device(
                id=device_id,
                name=attributes.get('name', ''),
                device_type=DeviceType(attributes.get('device_type', 'generic')),
                status=DeviceStatus(attributes.get('status', 'offline')),
                machine_id=attributes.get('machine_id'),
                iot_thing_name=thing_name,
                iot_thing_arn=response['thingArn'],
                iot_endpoint=aws_config.IOT_ENDPOINT,
                created_at=datetime.fromtimestamp(response['thingCreateDate'])
            )
            
            # Cache
            self.device_cache[device_id] = device
            
            return device
            
        except ClientError as e:
            logger.error(f"Erro ao obter dispositivo {device_id}: {e}")
            return None
    
    def list_devices(self, limit: int = 100) -> List[Device]:
        """Lista todos os dispositivos"""
        try:
            response = self.get_client().list_things(
                maxResults=limit,
                thingTypeName=iot_config.IOT_THING_TYPE
            )
            
            devices = []
            for thing in response['things']:
                thing_name = thing['thingName']
                device_id = thing_name.replace(iot_config.IOT_THING_NAME_PREFIX, '')
                
                device = self.get_device(device_id)
                if device:
                    devices.append(device)
            
            return devices
            
        except ClientError as e:
            logger.error(f"Erro ao listar dispositivos: {e}")
            return []
    
    def update_device(self, device: Device) -> Device:
        """Atualiza um dispositivo"""
        try:
            thing_name = device.iot_thing_name or f"{iot_config.IOT_THING_NAME_PREFIX}{device.id}"
            
            self.get_client().update_thing_shadow(
                thingName=thing_name,
                payload=json.dumps({
                    'state': {
                        'desired': {
                            'status': device.status.value,
                            'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                            'last_data_received': device.last_data_received.isoformat() if device.last_data_received else None
                        }
                    }
                })
            )
            
            # Atualizar atributos
            self.get_client().update_thing_groups_for_thing(
                thingName=thing_name,
                thingGroupsToAdd=[],
                thingGroupsToRemove=[]
            )
            
            # Atualizar cache
            self.device_cache[device.id] = device
            
            logger.info(f"Dispositivo {device.id} atualizado com sucesso")
            return device
            
        except ClientError as e:
            logger.error(f"Erro ao atualizar dispositivo {device.id}: {e}")
            raise
    
    def delete_device(self, device_id: str) -> bool:
        """Remove um dispositivo"""
        try:
            device = self.get_device(device_id)
            if device is None:
                return False
            
            thing_name = device.iot_thing_name
            
            # Remover do cache
            if device_id in self.device_cache:
                del self.device_cache[device_id]
            
            # Remover Thing
            self.get_client().delete_thing(
                thingName=thing_name
            )
            
            logger.info(f"Dispositivo {device_id} removido com sucesso")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao remover dispositivo {device_id}: {e}")
            return False
    
    def update_device_status(self, device_id: str, status: DeviceStatus) -> bool:
        """Atualiza o status de um dispositivo"""
        try:
            device = self.get_device(device_id)
            if device is None:
                return False
            
            device.status = status
            device.updated_at = datetime.utcnow()
            
            # Atualizar shadow
            thing_name = device.iot_thing_name
            self.get_client().update_thing_shadow(
                thingName=thing_name,
                payload=json.dumps({
                    'state': {
                        'desired': {
                            'status': status.value
                        }
                    }
                })
            )
            
            # Atualizar cache
            self.device_cache[device_id] = device
            
            logger.info(f"Status do dispositivo {device_id} atualizado para {status.value}")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao atualizar status do dispositivo {device_id}: {e}")
            return False
    
    # ==================== Gerenciamento de Sensores ====================
    
    def create_sensor(self, sensor: Sensor) -> Sensor:
        """Cria um novo sensor"""
        try:
            # Validar dispositivo associado
            if sensor.device_id:
                device = self.get_device(sensor.device_id)
                if device is None:
                    raise ValueError(f"Dispositivo {sensor.device_id} nao encontrado")
            
            # Cache
            self.sensor_cache[sensor.id] = sensor
            
            logger.info(f"Sensor {sensor.id} criado com sucesso")
            return sensor
            
        except Exception as e:
            logger.error(f"Erro ao criar sensor {sensor.id}: {e}")
            raise
    
    def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        """Obtem um sensor pelo ID"""
        # Verificar cache
        if sensor_id in self.sensor_cache:
            return self.sensor_cache[sensor_id]
        
        # Implementar busca em banco de dados ou IoT
        return None
    
    def list_sensors(self, device_id: Optional[str] = None, machine_id: Optional[str] = None) -> List[Sensor]:
        """Lista sensores por dispositivo ou maquina"""
        if device_id:
            return [s for s in self.sensor_cache.values() if s.device_id == device_id]
        elif machine_id:
            return [s for s in self.sensor_cache.values() if s.machine_id == machine_id]
        else:
            return list(self.sensor_cache.values())
    
    def update_sensor(self, sensor: Sensor) -> Sensor:
        """Atualiza um sensor"""
        try:
            # Atualizar cache
            self.sensor_cache[sensor.id] = sensor
            
            logger.info(f"Sensor {sensor.id} atualizado com sucesso")
            return sensor
            
        except Exception as e:
            logger.error(f"Erro ao atualizar sensor {sensor.id}: {e}")
            raise
    
    def update_sensor_status(self, sensor_id: str, status: SensorStatus) -> bool:
        """Atualiza o status de um sensor"""
        try:
            sensor = self.get_sensor(sensor_id)
            if sensor is None:
                return False
            
            sensor.status = status
            sensor.updated_at = datetime.utcnow()
            
            # Atualizar cache
            self.sensor_cache[sensor_id] = sensor
            
            logger.info(f"Status do sensor {sensor_id} atualizado para {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do sensor {sensor_id}: {e}")
            return False
    
    # ==================== Publicacao de Mensagens ====================
    
    def publish_reading(self, reading: Reading) -> bool:
        """Publica uma leitura no topico MQTT"""
        try:
            # Obter topico
            topic = iot_config.get_mqtt_topic("data")
            
            # Preparar mensagem
            message = reading.to_dict()
            
            # Publicar no AWS IoT (usando MQTT via boto3)
            # Nota: Para producao, usar cliente MQTT dedicado
            logger.info(f"Publicando leitura {reading.id} no topico {topic}")
            
            # Atualizar status da leitura
            reading.metadata.received_at = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar leitura {reading.id}: {e}")
            return False
    
    def publish_reading_batch(self, batch: ReadingBatch) -> bool:
        """Publica um batch de leituras no topico MQTT"""
        try:
            # Obter topico
            topic = iot_config.get_mqtt_topic("data")
            
            # Preparar mensagem
            message = batch.to_dict()
            
            logger.info(f"Publicando batch {batch.id} com {len(batch.readings)} leituras no topico {topic}")
            
            # Atualizar status
            batch.received_at = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar batch {batch.id}: {e}")
            return False
    
    def publish_alert(self, alert: Dict) -> bool:
        """Publica um alerta no topico MQTT"""
        try:
            # Obter topico
            topic = iot_config.get_mqtt_topic("alerts")
            
            logger.info(f"Publicando alerta {alert.get('id')} no topico {topic}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar alerta: {e}")
            return False
    
    def publish_command(self, device_id: str, command: Dict) -> bool:
        """Publica um comando para um dispositivo"""
        try:
            # Obter topico
            topic = iot_config.get_mqtt_topic("commands")
            
            # Adicionar ID do dispositivo
            command['device_id'] = device_id
            command['timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Publicando comando para dispositivo {device_id} no topico {topic}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar comando para {device_id}: {e}")
            return False
    
    # ==================== Gerenciamento de Shadow ====================
    
    def get_thing_shadow(self, device_id: str) -> Optional[Dict]:
        """Obtem o shadow de uma Thing"""
        try:
            device = self.get_device(device_id)
            if device is None:
                return None
            
            thing_name = device.iot_thing_name
            
            response = self.get_client().get_thing_shadow(
                thingName=thing_name
            )
            
            if 'payload' in response:
                return json.loads(response['payload'])
            
            return None
            
        except ClientError as e:
            logger.error(f"Erro ao obter shadow da Thing {device_id}: {e}")
            return None
    
    def update_thing_shadow(self, device_id: str, shadow: Dict) -> bool:
        """Atualiza o shadow de uma Thing"""
        try:
            device = self.get_device(device_id)
            if device is None:
                return False
            
            thing_name = device.iot_thing_name
            
            self.get_client().update_thing_shadow(
                thingName=thing_name,
                payload=json.dumps(shadow)
            )
            
            logger.info(f"Shadow da Thing {device_id} atualizado")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao atualizar shadow da Thing {device_id}: {e}")
            return False
    
    # ==================== Gerenciamento de Certificados ====================
    
    def create_certificate(self, device_id: str) -> Optional[Dict]:
        """Cria um novo certificado para um dispositivo"""
        try:
            response = self.get_client().create_keys_and_certificate(
                setAsActive=True
            )
            
            # Anexar a Thing
            device = self.get_device(device_id)
            if device:
                self.get_client().attach_thing_principal(
                    thingName=device.iot_thing_name,
                    principal=response['certificateArn']
                )
                
                # Anexar politica
                self.get_client().attach_policy(
                    policyName=iot_config.DEFAULT_POLICY_NAME,
                    target=response['certificateArn']
                )
            
            logger.info(f"Certificado criado para dispositivo {device_id}")
            return response
            
        except ClientError as e:
            logger.error(f"Erro ao criar certificado para {device_id}: {e}")
            return None
    
    def list_certificates(self, device_id: str) -> List[Dict]:
        """Lista certificados de um dispositivo"""
        try:
            device = self.get_device(device_id)
            if device is None:
                return []
            
            response = self.get_client().list_thing_principals(
                thingName=device.iot_thing_name
            )
            
            certificates = []
            for principal in response['principals']:
                if 'certificate' in principal:
                    cert_response = self.get_client().describe_certificate(
                        certificateId=principal['certificate'].split('/')[-1]
                    )
                    certificates.append(cert_response)
            
            return certificates
            
        except ClientError as e:
            logger.error(f"Erro ao listar certificados para {device_id}: {e}")
            return []
    
    def revoke_certificate(self, certificate_id: str) -> bool:
        """Revoga um certificado"""
        try:
            self.get_client().update_certificate(
                certificateId=certificate_id,
                newStatus='REVOKED'
            )
            
            logger.info(f"Certificado {certificate_id} revogado")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao revogar certificado {certificate_id}: {e}")
            return False
    
    # ==================== Monitoramento ====================
    
    def get_device_metrics(self, device_id: str) -> Dict:
        """Obtem metricas de um dispositivo"""
        device = self.get_device(device_id)
        if device is None:
            return {}
        
        return {
            'device_id': device.id,
            'status': device.status.value,
            'last_heartbeat': device.last_heartbeat,
            'last_data_received': device.last_data_received,
            'messages_sent': device.messages_sent,
            'messages_received': device.messages_received,
            'errors': device.errors,
            'uptime': device.get_uptime(),
            'error_rate': device.get_error_rate()
        }
    
    def get_system_metrics(self) -> Dict:
        """Obtem metricas do sistema"""
        devices = self.list_devices()
        
        online_devices = sum(1 for d in devices if d.is_online())
        critical_devices = sum(1 for d in devices if d.is_critical())
        
        return {
            'total_devices': len(devices),
            'online_devices': online_devices,
            'critical_devices': critical_devices,
            'total_sensors': len(self.sensor_cache),
            'active_sensors': sum(1 for s in self.sensor_cache.values() if s.is_active())
        }
