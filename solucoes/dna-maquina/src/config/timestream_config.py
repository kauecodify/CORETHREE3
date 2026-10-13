"""
CORETHREE3 - DNA de Maquinas
Configuracoes do Amazon Timestream
"""

import os
from typing import Dict, List, Any


class TimestreamConfig:
    """Configuracoes do Amazon Timestream para series temporais"""
    
    # Configuracoes gerais
    ENABLE_TIMESTREAM: bool = os.getenv("ENABLE_TIMESTREAM", "True").lower() == "true"
    TIMESTREAM_REGION: str = os.getenv("TIMESTREAM_REGION", "us-east-1")
    
    # Banco de dados
    DATABASE_NAME: str = os.getenv("TIMESTREAM_DATABASE_NAME", "DNAMaquinaDB")
    DATABASE_DESCRIPTION: str = "Banco de dados de series temporais para DNA de Maquinas"
    
    # Configuracoes de retencao
    RETENTION_DAYS: int = int(os.getenv("TIMESTREAM_RETENTION_DAYS", "365"))  # 1 ano
    RETENTION_MEMORY: int = int(os.getenv("TIMESTREAM_RETENTION_MEMORY", "30"))  # 30 dias em memoria
    RETENTION_MAGNETIC: int = int(os.getenv("TIMESTREAM_RETENTION_MAGNETIC", "365"))  # 1 ano em magnetic
    
    # Tabelas
    TABLES: Dict[str, Dict[str, Any]] = {
        "vibration": {
            "name": "vibration",
            "description": "Dados de vibracao de maquinas",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "sensor_id", "axis"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "rms", "type": "DOUBLE"},
                {"name": "peak", "type": "DOUBLE"},
                {"name": "frequency", "type": "DOUBLE"}
            ],
            "retention_days": 365,
            "memory_retention_days": 30,
            "magnetic_retention_days": 365
        },
        "temperature": {
            "name": "temperature",
            "description": "Dados de temperatura de maquinas",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "sensor_id", "unit"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "min", "type": "DOUBLE"},
                {"name": "max", "type": "DOUBLE"},
                {"name": "avg", "type": "DOUBLE"}
            ],
            "retention_days": 365,
            "memory_retention_days": 30,
            "magnetic_retention_days": 365
        },
        "pressure": {
            "name": "pressure",
            "description": "Dados de pressao de maquinas",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "sensor_id", "unit"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "min", "type": "DOUBLE"},
                {"name": "max", "type": "DOUBLE"}
            ],
            "retention_days": 365,
            "memory_retention_days": 30,
            "magnetic_retention_days": 365
        },
        "current": {
            "name": "current",
            "description": "Dados de corrente eletrica de maquinas",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "sensor_id", "phase"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "rms", "type": "DOUBLE"},
                {"name": "peak", "type": "DOUBLE"}
            ],
            "retention_days": 365,
            "memory_retention_days": 30,
            "magnetic_retention_days": 365
        },
        "voltage": {
            "name": "voltage",
            "description": "Dados de tensao eletrica de maquinas",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "sensor_id", "phase"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "rms", "type": "DOUBLE"},
                {"name": "min", "type": "DOUBLE"},
                {"name": "max", "type": "DOUBLE"}
            ],
            "retention_days": 365,
            "memory_retention_days": 30,
            "magnetic_retention_days": 365
        },
        "humidity": {
            "name": "humidity",
            "description": "Dados de umidade de maquinas",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "sensor_id"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "min", "type": "DOUBLE"},
                {"name": "max", "type": "DOUBLE"}
            ],
            "retention_days": 365,
            "memory_retention_days": 30,
            "magnetic_retention_days": 365
        },
        "generic": {
            "name": "generic",
            "description": "Dados genericos de sensores",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "sensor_id", "sensor_type"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "raw_value", "type": "DOUBLE"},
                {"name": "quality", "type": "DOUBLE"}
            ],
            "retention_days": 365,
            "memory_retention_days": 30,
            "magnetic_retention_days": 365
        },
        "alerts": {
            "name": "alerts",
            "description": "Alertas gerados pelo sistema",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "alert_type", "severity"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "threshold", "type": "DOUBLE"},
                {"name": "confidence", "type": "DOUBLE"}
            ],
            "retention_days": 90,
            "memory_retention_days": 7,
            "magnetic_retention_days": 90
        },
        "predictions": {
            "name": "predictions",
            "description": "Previsoes de falhas e RUL",
            "time_column": "time",
            "dimension_columns": ["device_id", "machine_id", "prediction_type", "model_version"],
            "measure_columns": [
                {"name": "value", "type": "DOUBLE"},
                {"name": "confidence", "type": "DOUBLE"},
                {"name": "horizon", "type": "BIGINT"}
            ],
            "retention_days": 180,
            "memory_retention_days": 30,
            "magnetic_retention_days": 180
        }
    }
    
    # Configuracoes de query
    QUERY_TIMEOUT: int = 30  # segundos
    MAX_QUERY_LENGTH: int = 100000  # caracteres
    MAX_QUERY_RESULTS: int = 10000  # resultados maximos
    
    # Configuracoes de paginacao
    DEFAULT_PAGE_SIZE: int = 1000
    MAX_PAGE_SIZE: int = 10000
    
    # Configuracoes de agregacao
    AGGREGATION_GRANULARITY: str = "1m"  # 1 minuto
    AGGREGATION_WINDOWS: List[str] = ["1m", "5m", "15m", "1h", "1d", "1w"]
    
    # Configuracoes de downsampling
    DOWNSAMPLING_ENABLED: bool = True
    DOWNSAMPLING_INTERVAL: str = "1h"  # 1 hora
    DOWNSAMPLING_FUNCTION: str = "avg"  # avg, sum, min, max, count
    
    # Configuracoes de compressao
    COMPRESSION_ENABLED: bool = True
    COMPRESSION_TYPE: str = "GZIP"
    
    # Configuracoes de monitoramento
    MONITOR_ENABLED: bool = True
    MONITOR_INTERVAL: int = 300  # 5 minutos
    MONITOR_METRICS: List[str] = [
        "ingestion_rate",
        "ingestion_latency",
        "query_rate",
        "query_latency",
        "storage_used",
        "storage_capacity"
    ]
    
    # Configuracoes de logging
    LOG_QUERIES: bool = False  # Logar queries (apenas para debug)
    LOG_SLOW_QUERIES: bool = True
    SLOW_QUERY_THRESHOLD: int = 1000  # milissegundos
    
    # Configuracoes de cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutos
    
    # Configuracoes de retry
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 0.5  # segundos
    
    @classmethod
    def get_table_config(cls, table_name: str) -> Dict[str, Any]:
        """Obter configuracao de uma tabela"""
        return cls.TABLES.get(table_name, {})
    
    @classmethod
    def get_table_ddl(cls, table_name: str) -> str:
        """Gerar DDL para uma tabela"""
        table_config = cls.get_table_config(table_name)
        if not table_config:
            return ""
        
        table_name_full = table_config.get("name", table_name)
        time_column = table_config.get("time_column", "time")
        dimension_columns = table_config.get("dimension_columns", [])
        measure_columns = table_config.get("measure_columns", [])
        
        # Criar colunas de dimensao
        dimension_defs = []
        for col in dimension_columns:
            dimension_defs.append(f"    {col} VARCHAR(255)")
        
        # Criar colunas de medida
        measure_defs = []
        for col in measure_columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "DOUBLE")
            measure_defs.append(f"    {col_name} {col_type}")
        
        # Criar DDL
        ddl = f"CREATE TABLE {table_name_full} (
"
        ddl += f"    {time_column} TIMESTAMP,
"
        ddl += ",\n".join(dimension_defs)
        if dimension_defs and measure_defs:
            ddl += ",\n"
        ddl += ",\n".join(measure_defs)
        ddl += "\n)"
        
        return ddl
    
    @classmethod
    def get_all_tables_ddl(cls) -> str:
        """Gerar DDL para todas as tabelas"""
        ddl_statements = []
        for table_name in cls.TABLES:
            ddl = cls.get_table_ddl(table_name)
            if ddl:
                ddl_statements.append(ddl)
        
        return ";\n\n".join(ddl_statements)
    
    @classmethod
    def get_query_for_last_values(cls, table_name: str, device_id: str, 
                                  hours: int = 24) -> str:
        """Gerar query para obter ultimos valores"""
        table_config = cls.get_table_config(table_name)
        if not table_config:
            return ""
        
        time_column = table_config.get("time_column", "time")
        measure_columns = table_config.get("measure_columns", [])
        
        # Selecionar colunas
        select_columns = [time_column]
        for col in measure_columns:
            select_columns.append(col.get("name", ""))
        
        select_str = ", ".join(select_columns)
        
        # Query
        query = f"""
        SELECT {select_str}
        FROM {table_name}
        WHERE device_id = '{device_id}'
        AND {time_column} >= ago({hours}h)
        ORDER BY {time_column} DESC
        LIMIT 1000
        """
        return query
    
    @classmethod
    def get_query_for_aggregation(cls, table_name: str, device_id: str,
                                  start_time: str, end_time: str,
                                  granularity: str = "1h") -> str:
        """Gerar query para agregacao"""
        table_config = cls.get_table_config(table_name)
        if not table_config:
            return ""
        
        time_column = table_config.get("time_column", "time")
        measure_columns = table_config.get("measure_columns", [])
        
        # Selecionar colunas de agregacao
        select_parts = []
        for col in measure_columns:
            col_name = col.get("name", "")
            select_parts.append(f"avg({col_name}) as avg_{col_name}")
            select_parts.append(f"min({col_name}) as min_{col_name}")
            select_parts.append(f"max({col_name}) as max_{col_name}")
        
        select_str = ", ".join(select_parts)
        
        # Query
        query = f"""
        SELECT 
            bin({time_column}, {granularity}) as time_bin,
            {select_str}
        FROM {table_name}
        WHERE device_id = '{device_id}'
        AND {time_column} BETWEEN '{start_time}' AND '{end_time}'
        GROUP BY bin({time_column}, {granularity})
        ORDER BY time_bin
        """
        return query


# Instancia das configuracoes
timestream_config = TimestreamConfig()
