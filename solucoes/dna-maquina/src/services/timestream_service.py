"""
CORETHREE3 - DNA de Maquinas
Servico de Timestream

Servico para gerenciamento de dados de series temporais usando AWS Timestream.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import boto3
from botocore.exceptions import ClientError

from ..config.aws_config import aws_config
from ..config.timestream_config import TimestreamConfig, timestream_config
from ..models.reading import Reading, ReadingBatch
from ..models.sensor import SensorType

logger = logging.getLogger(__name__)


class TimestreamService:
    """
    Servico de Timestream para armazenamento e consultas de series temporais.
    
    Responsabilidades:
    - Armazenamento de leituras de sensores
    - Consultas de dados historicos
    - Agregacoes e analises temporais
    - Gerenciamento de tabelas
    """
    
    def __init__(self):
        """Inicializa o servico de Timestream"""
        self.timestream_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente AWS Timestream"""
        try:
            self.timestream_client = boto3.client(
                'timestream-write',
                region_name=aws_config.REGION,
                aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY
            )
            
            # Cliente para consultas
            self.timestream_query_client = boto3.client(
                'timestream-query',
                region_name=aws_config.REGION,
                aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY
            )
            
            logger.info("Clientes AWS Timestream inicializados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar clientes AWS Timestream: {e}")
            raise
    
    def get_write_client(self):
        """Retorna o cliente de escrita do Timestream"""
        if self.timestream_client is None:
            self._initialize_client()
        return self.timestream_client
    
    def get_query_client(self):
        """Retorna o cliente de consulta do Timestream"""
        if self.timestream_query_client is None:
            self._initialize_client()
        return self.timestream_query_client
    
    # ==================== Gerenciamento de Tabelas ====================
    
    def create_database(self, database_name: str = None) -> bool:
        """Cria o banco de dados do Timestream"""
        db_name = database_name or timestream_config.DATABASE_NAME
        
        try:
            self.get_write_client().create_database(
                DatabaseName=db_name
            )
            
            logger.info(f"Banco de dados {db_name} criado com sucesso")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                logger.info(f"Banco de dados {db_name} ja existe")
                return True
            logger.error(f"Erro ao criar banco de dados {db_name}: {e}")
            return False
    
    def create_table(self, table_name: str) -> bool:
        """Cria uma tabela no Timestream"""
        try:
            table_config = timestream_config.get_table_config(table_name)
            if table_config is None:
                logger.error(f"Configuracao da tabela {table_name} nao encontrada")
                return False
            
            self.get_write_client().create_table(
                DatabaseName=timestream_config.DATABASE_NAME,
                TableName=table_name,
                RetentionProperties={
                    'MemoryStoreRetentionPeriodInHours': table_config.get('retention_hours', 24 * 365),
                    'MagneticStoreRetentionPeriodInDays': table_config.get('retention_days', 365)
                }
            )
            
            logger.info(f"Tabela {table_name} criada com sucesso")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                logger.info(f"Tabela {table_name} ja existe")
                return True
            logger.error(f"Erro ao criar tabela {table_name}: {e}")
            return False
    
    def create_all_tables(self) -> Dict[str, bool]:
        """Cria todas as tabelas configuradas"""
        results = {}
        
        for table_name in timestream_config.TABLES.keys():
            results[table_name] = self.create_table(table_name)
        
        return results
    
    def delete_table(self, table_name: str) -> bool:
        """Remove uma tabela do Timestream"""
        try:
            self.get_write_client().delete_table(
                DatabaseName=timestream_config.DATABASE_NAME,
                TableName=table_name
            )
            
            logger.info(f"Tabela {table_name} removida com sucesso")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao remover tabela {table_name}: {e}")
            return False
    
    def list_tables(self) -> List[str]:
        """Lista todas as tabelas do banco de dados"""
        try:
            response = self.get_query_client().list_tables(
                DatabaseName=timestream_config.DATABASE_NAME
            )
            
            return [table['TableName'] for table in response['Tables']]
            
        except ClientError as e:
            logger.error(f"Erro ao listar tabelas: {e}")
            return []
    
    # ==================== Armazenamento de Dados ====================
    
    def write_reading(self, reading: Reading) -> bool:
        """Escreve uma leitura no Timestream"""
        try:
            # Determinar a tabela com base no tipo do sensor
            sensor_type = reading.metadata.sensor_id.split('-')[0] if '-' in reading.metadata.sensor_id else 'vibration'
            table_name = self._get_table_name_for_sensor(sensor_type)
            
            # Preparar registro
            record = self._prepare_record(reading, table_name)
            
            # Escrever no Timestream
            self.get_write_client().write_records(
                DatabaseName=timestream_config.DATABASE_NAME,
                TableName=table_name,
                Records=[record],
                CommonAttributes={}
            )
            
            logger.info(f"Leitura {reading.id} escrita na tabela {table_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao escrever leitura {reading.id}: {e}")
            return False
    
    def write_reading_batch(self, batch: ReadingBatch) -> bool:
        """Escreve um batch de leituras no Timestream"""
        try:
            # Agrupar leituras por tabela
            records_by_table: Dict[str, List[Dict]] = {}
            
            for reading in batch.readings:
                sensor_type = reading.metadata.sensor_id.split('-')[0] if '-' in reading.metadata.sensor_id else 'vibration'
                table_name = self._get_table_name_for_sensor(sensor_type)
                
                if table_name not in records_by_table:
                    records_by_table[table_name] = []
                
                records_by_table[table_name].append(self._prepare_record(reading, table_name))
            
            # Escrever em cada tabela
            for table_name, records in records_by_table.items():
                self.get_write_client().write_records(
                    DatabaseName=timestream_config.DATABASE_NAME,
                    TableName=table_name,
                    Records=records,
                    CommonAttributes={}
                )
            
            logger.info(f"Batch {batch.id} com {len(batch.readings)} leituras escrito no Timestream")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao escrever batch {batch.id}: {e}")
            return False
    
    def _get_table_name_for_sensor(self, sensor_type: str) -> str:
        """Obtem o nome da tabela para um tipo de sensor"""
        sensor_table_map = {
            'vibration': 'vibration',
            'temperature': 'temperature',
            'pressure': 'pressure',
            'current': 'current',
            'voltage': 'voltage',
            'humidity': 'humidity',
            'rotation': 'rotation'
        }
        
        return sensor_table_map.get(sensor_type, 'vibration')
    
    def _prepare_record(self, reading: Reading, table_name: str) -> Dict:
        """Prepara um registro para escrita no Timestream"""
        # Obter configuracao da tabela
        table_config = timestream_config.get_table_config(table_name)
        if table_config is None:
            raise ValueError(f"Configuracao da tabela {table_name} nao encontrada")
        
        # Criar registro
        record = {
            'Time': reading.metadata.timestamp.isoformat(),
            'TimeUnit': 'SECONDS'
        }
        
        # Adicionar dimensoes
        dimensions = {
            'device_id': reading.metadata.device_id or '',
            'machine_id': reading.metadata.machine_id or '',
            'sensor_id': reading.metadata.sensor_id
        }
        
        if reading.metadata.axis:
            dimensions['axis'] = reading.metadata.axis
        
        if reading.metadata.location:
            dimensions['location'] = reading.metadata.location
        
        # Adicionar medidas
        measures = {
            'value': str(reading.value)
        }
        
        # Adicionar medidas adicionais
        if reading.rms is not None:
            measures['rms'] = str(reading.rms)
        if reading.peak is not None:
            measures['peak'] = str(reading.peak)
        if reading.frequency is not None:
            measures['frequency'] = str(reading.frequency)
        
        # Adicionar metadados
        measures['quality'] = reading.metadata.quality.value
        if reading.metadata.confidence is not None:
            measures['confidence'] = str(reading.metadata.confidence)
        
        # Adicionar flag de anomalia
        measures['is_anomaly'] = str(int(reading.is_anomaly))
        if reading.anomaly_score is not None:
            measures['anomaly_score'] = str(reading.anomaly_score)
        
        # Adicionar flag de threshold violado
        if reading.threshold_violated:
            measures['threshold_violated'] = reading.threshold_violated
            measures['threshold_value'] = str(reading.threshold_value or '')
        
        # Adicionar a dimensao
        record['Dimensions'] = [
            {'Name': name, 'Value': value} for name, value in dimensions.items()
        ]
        
        # Adicionar medidas
        record['MeasureName'] = table_name
        record['MeasureValues'] = [
            {'Name': name, 'Value': value, 'Type': 'DOUBLE'} for name, value in measures.items()
        ]
        
        return record
    
    # ==================== Consultas ====================
    
    def query_readings(self, sensor_id: str, start_time: datetime, end_time: datetime, 
                      limit: int = 1000) -> List[Dict]:
        """Consulta leituras de um sensor em um intervalo de tempo"""
        try:
            # Determinar tabela
            sensor_type = sensor_id.split('-')[0] if '-' in sensor_id else 'vibration'
            table_name = self._get_table_name_for_sensor(sensor_type)
            
            # Executar consulta
            query = f"""
                SELECT * 
                FROM "{timestream_config.DATABASE_NAME}"."{table_name}"
                WHERE sensor_id = '{sensor_id}'
                AND time BETWEEN from_iso8601_timestamp('{start_time.isoformat()}') 
                             AND to_iso8601_timestamp('{end_time.isoformat()}')
                ORDER BY time DESC
                LIMIT {limit}
            """
            
            response = self.get_query_client().query(
                QueryString=query
            )
            
            # Processar resultados
            readings = []
            for row in response['Rows']:
                if 'DataPoints' in row:
                    for data_point in row['DataPoints']:
                        reading = self._parse_row(row, data_point)
                        readings.append(reading)
            
            return readings
            
        except ClientError as e:
            logger.error(f"Erro ao consultar leituras para sensor {sensor_id}: {e}")
            return []
    
    def query_machine_readings(self, machine_id: str, start_time: datetime, end_time: datetime,
                              sensor_type: Optional[str] = None, limit: int = 1000) -> List[Dict]:
        """Consulta leituras de uma maquina em um intervalo de tempo"""
        try:
            # Determinar tabela
            table_name = self._get_table_name_for_sensor(sensor_type or 'vibration')
            
            # Executar consulta
            sensor_filter = f"AND sensor_type = '{sensor_type}'" if sensor_type else ""
            
            query = f"""
                SELECT * 
                FROM "{timestream_config.DATABASE_NAME}"."{table_name}"
                WHERE machine_id = '{machine_id}'
                {sensor_filter}
                AND time BETWEEN from_iso8601_timestamp('{start_time.isoformat()}') 
                             AND to_iso8601_timestamp('{end_time.isoformat()}')
                ORDER BY time DESC
                LIMIT {limit}
            """
            
            response = self.get_query_client().query(
                QueryString=query
            )
            
            # Processar resultados
            readings = []
            for row in response['Rows']:
                if 'DataPoints' in row:
                    for data_point in row['DataPoints']:
                        reading = self._parse_row(row, data_point)
                        readings.append(reading)
            
            return readings
            
        except ClientError as e:
            logger.error(f"Erro ao consultar leituras para maquina {machine_id}: {e}")
            return []
    
    def query_aggregated_readings(self, machine_id: str, start_time: datetime, end_time: datetime,
                                 aggregation: str = 'AVG', interval: str = '1h') -> List[Dict]:
        """Consulta leituras agregadas de uma maquina"""
        try:
            # Consultar todas as tabelas de sensores
            aggregated_data = []
            
            for table_name in timestream_config.TABLES.keys():
                query = f"""
                    SELECT 
                        machine_id,
                        sensor_id,
                        {aggregation}(value) as value,
                        {aggregation}(rms) as rms_avg,
                        {aggregation}(peak) as peak_avg,
                        COUNT(*) as count,
                        MAX(time) as last_timestamp
                    FROM "{timestream_config.DATABASE_NAME}"."{table_name}"
                    WHERE machine_id = '{machine_id}'
                    AND time BETWEEN from_iso8601_timestamp('{start_time.isoformat()}') 
                                 AND to_iso8601_timestamp('{end_time.isoformat()}')
                    GROUP BY machine_id, sensor_id, bin(time, {interval})
                    ORDER BY last_timestamp DESC
                """
                
                response = self.get_query_client().query(
                    QueryString=query
                )
                
                # Processar resultados
                for row in response['Rows']:
                    if 'DataPoints' in row:
                        for data_point in row['DataPoints']:
                            aggregated_data.append(self._parse_aggregated_row(row, data_point, table_name))
            
            return aggregated_data
            
        except ClientError as e:
            logger.error(f"Erro ao consultar leituras agregadas para maquina {machine_id}: {e}")
            return []
    
    def query_anomalies(self, machine_id: str, start_time: datetime, end_time: datetime,
                       threshold: float = 0.8) -> List[Dict]:
        """Consulta anomalias detectadas"""
        try:
            # Consultar tabela de alerts ou usar flag de anomalia
            query = f"""
                SELECT 
                    time,
                    device_id,
                    machine_id,
                    sensor_id,
                    value,
                    anomaly_score,
                    threshold_violated
                FROM "{timestream_config.DATABASE_NAME}"."vibration"
                WHERE machine_id = '{machine_id}'
                AND is_anomaly = '1'
                AND anomaly_score >= {threshold}
                AND time BETWEEN from_iso8601_timestamp('{start_time.isoformat()}') 
                             AND to_iso8601_timestamp('{end_time.isoformat()}')
                ORDER BY anomaly_score DESC
            """
            
            response = self.get_query_client().query(
                QueryString=query
            )
            
            # Processar resultados
            anomalies = []
            for row in response['Rows']:
                if 'DataPoints' in row:
                    for data_point in row['DataPoints']:
                        anomalies.append(self._parse_row(row, data_point))
            
            return anomalies
            
        except ClientError as e:
            logger.error(f"Erro ao consultar anomalias para maquina {machine_id}: {e}")
            return []
    
    def query_statistics(self, machine_id: str, start_time: datetime, end_time: datetime) -> Dict:
        """Consulta estatisticas de uma maquina"""
        try:
            stats = {
                'vibration': {},
                'temperature': {},
                'pressure': {},
                'current': {},
                'voltage': {}
            }
            
            for sensor_type in stats.keys():
                table_name = self._get_table_name_for_sensor(sensor_type)
                
                query = f"""
                    SELECT 
                        AVG(value) as avg_value,
                        MAX(value) as max_value,
                        MIN(value) as min_value,
                        STDDEV(value) as stddev_value,
                        COUNT(*) as count
                    FROM "{timestream_config.DATABASE_NAME}"."{table_name}"
                    WHERE machine_id = '{machine_id}'
                    AND time BETWEEN from_iso8601_timestamp('{start_time.isoformat()}') 
                                 AND to_iso8601_timestamp('{end_time.isoformat()}')
                """
                
                response = self.get_query_client().query(
                    QueryString=query
                )
                
                if response['Rows']:
                    row = response['Rows'][0]
                    for data_point in row.get('DataPoints', []):
                        for field in data_point.get('FieldList', []):
                            stats[sensor_type][field['FieldName']] = self._parse_value(field)
            
            return stats
            
        except ClientError as e:
            logger.error(f"Erro ao consultar estatisticas para maquina {machine_id}: {e}")
            return {}
    
    def _parse_row(self, row: Dict, data_point: Dict) -> Dict:
        """Analisa uma linha de resultado do Timestream"""
        reading = {}
        
        # Extrair timestamp
        for field in data_point.get('FieldList', []):
            if field['FieldName'] == 'time':
                reading['timestamp'] = field['FieldValue']
            else:
                reading[field['FieldName']] = self._parse_value(field)
        
        # Extrair dimensoes
        for dimension in row.get('Dimensions', []):
            reading[dimension['Name']] = dimension['Value']
        
        return reading
    
    def _parse_aggregated_row(self, row: Dict, data_point: Dict, table_name: str) -> Dict:
        """Analisa uma linha de resultado agregado"""
        aggregated = {'sensor_type': table_name}
        
        for field in data_point.get('FieldList', []):
            aggregated[field['FieldName']] = self._parse_value(field)
        
        # Extrair dimensoes
        for dimension in row.get('Dimensions', []):
            aggregated[dimension['Name']] = dimension['Value']
        
        return aggregated
    
    def _parse_value(self, field: Dict) -> Any:
        """Analisa um valor do Timestream"""
        field_type = field.get('FieldType', '')
        field_value = field.get('FieldValue')
        
        if field_value is None:
            return None
        
        if field_type == 'TIMESTAMP':
            return field_value
        elif field_type == 'DOUBLE':
            return float(field_value) if field_value else 0.0
        elif field_type == 'BIGINT':
            return int(field_value) if field_value else 0
        elif field_type == 'VARCHAR':
            return field_value
        elif field_type == 'BOOLEAN':
            return field_value.lower() == 'true'
        else:
            return field_value
    
    # ==================== Utilitarios ====================
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """Obtem informacoes sobre uma tabela"""
        try:
            response = self.get_query_client().describe_table(
                DatabaseName=timestream_config.DATABASE_NAME,
                TableName=table_name
            )
            
            return {
                'table_name': table_name,
                'database_name': timestream_config.DATABASE_NAME,
                'retention_properties': response.get('Table', {}).get('RetentionProperties', {})
            }
            
        except ClientError as e:
            logger.error(f"Erro ao obter informacoes da tabela {table_name}: {e}")
            return None
    
    def check_table_exists(self, table_name: str) -> bool:
        """Verifica se uma tabela existe"""
        tables = self.list_tables()
        return table_name in tables
    
    def initialize_database(self) -> bool:
        """Inicializa o banco de dados e tabelas"""
        try:
            # Criar banco de dados
            if not self.create_database():
                return False
            
            # Criar tabelas
            results = self.create_all_tables()
            
            # Verificar se todas as tabelas foram criadas
            all_success = all(results.values())
            
            if all_success:
                logger.info("Banco de dados e tabelas inicializados com sucesso")
            else:
                logger.warning("Algumas tabelas falharam ao ser criadas")
            
            return all_success
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            return False
