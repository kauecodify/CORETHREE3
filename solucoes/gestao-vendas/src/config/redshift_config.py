"""
CORETHREE3 - Gestao de Vendas Avancada
Configuracoes do Amazon Redshift
"""

import os
from typing import Dict, List, Any


class RedshiftConfig:
    """Configuracoes do Amazon Redshift para Data Warehouse"""
    
    # Configuracoes gerais
    ENABLE_REDSHIFT: bool = os.getenv("ENABLE_REDSHIFT", "True").lower() == "true"
    REDSHIFT_REGION: str = os.getenv("REDSHIFT_REGION", "us-east-1")
    
    # Cluster
    CLUSTER_NAME: str = os.getenv("REDSHIFT_CLUSTER_NAME", "corethree3-gestao-vendas")
    CLUSTER_TYPE: str = os.getenv("REDSHIFT_CLUSTER_TYPE", "multi-node")  # single-node, multi-node
    NODE_TYPE: str = os.getenv("REDSHIFT_NODE_TYPE", "dc2.large")
    NODE_COUNT: int = int(os.getenv("REDSHIFT_NODE_COUNT", "2"))
    
    # Banco de dados
    DATABASE_NAME: str = os.getenv("REDSHIFT_DATABASE_NAME", "gestao_vendas")
    DATABASE_USER: str = os.getenv("REDSHIFT_DATABASE_USER", "admin")
    DATABASE_PASSWORD: str = os.getenv("REDSHIFT_DATABASE_PASSWORD", "")
    DATABASE_PORT: int = int(os.getenv("REDSHIFT_DATABASE_PORT", "5439"))
    
    # Schema
    SCHEMA_NAME: str = "public"
    
    # Tabelas
    TABLES: Dict[str, Dict[str, Any]] = {
        "sales": {
            "name": "sales",
            "description": "Tabela de vendas",
            "columns": {
                "id": "VARCHAR(255) PRIMARY KEY",
                "product_id": "VARCHAR(255) NOT NULL",
                "customer_id": "VARCHAR(255)",
                "quantity": "INTEGER NOT NULL",
                "unit_price": "DECIMAL(10,2) NOT NULL",
                "total_price": "DECIMAL(10,2) NOT NULL",
                "sale_date": "TIMESTAMP NOT NULL",
                "channel": "VARCHAR(50)",
                "region": "VARCHAR(50)",
                "salesperson_id": "VARCHAR(255)",
                "status": "VARCHAR(50)",
                "created_at": "TIMESTAMP DEFAULT GETDATE()",
                "updated_at": "TIMESTAMP DEFAULT GETDATE()"
            },
            "distkey": "product_id",
            "sortkey": "sale_date",
            "indexes": [
                "CREATE INDEX idx_sales_customer ON sales(customer_id)",
                "CREATE INDEX idx_sales_date ON sales(sale_date)",
                "CREATE INDEX idx_sales_region ON sales(region)"
            ]
        },
        "products": {
            "name": "products",
            "description": "Tabela de produtos",
            "columns": {
                "id": "VARCHAR(255) PRIMARY KEY",
                "name": "VARCHAR(255) NOT NULL",
                "description": "TEXT",
                "category": "VARCHAR(100)",
                "subcategory": "VARCHAR(100)",
                "brand": "VARCHAR(100)",
                "unit_price": "DECIMAL(10,2) NOT NULL",
                "cost_price": "DECIMAL(10,2)",
                "sku": "VARCHAR(100) UNIQUE",
                "barcode": "VARCHAR(100) UNIQUE",
                "is_active": "BOOLEAN DEFAULT TRUE",
                "created_at": "TIMESTAMP DEFAULT GETDATE()",
                "updated_at": "TIMESTAMP DEFAULT GETDATE()"
            },
            "distkey": "id",
            "sortkey": "name",
            "indexes": [
                "CREATE INDEX idx_products_category ON products(category)",
                "CREATE INDEX idx_products_brand ON products(brand)"
            ]
        },
        "customers": {
            "name": "customers",
            "description": "Tabela de clientes",
            "columns": {
                "id": "VARCHAR(255) PRIMARY KEY",
                "name": "VARCHAR(255) NOT NULL",
                "email": "VARCHAR(255)",
                "phone": "VARCHAR(50)",
                "cpf_cnpj": "VARCHAR(50) UNIQUE",
                "address": "TEXT",
                "city": "VARCHAR(100)",
                "state": "VARCHAR(50)",
                "zip_code": "VARCHAR(20)",
                "country": "VARCHAR(50)",
                "segment": "VARCHAR(100)",
                "rfm_score": "INTEGER",
                "lifetime_value": "DECIMAL(12,2)",
                "first_purchase_date": "TIMESTAMP",
                "last_purchase_date": "TIMESTAMP",
                "purchase_count": "INTEGER",
                "is_active": "BOOLEAN DEFAULT TRUE",
                "created_at": "TIMESTAMP DEFAULT GETDATE()",
                "updated_at": "TIMESTAMP DEFAULT GETDATE()"
            },
            "distkey": "id",
            "sortkey": "name",
            "indexes": [
                "CREATE INDEX idx_customers_segment ON customers(segment)",
                "CREATE INDEX idx_customers_rfm ON customers(rfm_score)",
                "CREATE INDEX idx_customers_city ON customers(city)"
            ]
        },
        "stock": {
            "name": "stock",
            "description": "Tabela de estoque",
            "columns": {
                "id": "VARCHAR(255) PRIMARY KEY",
                "product_id": "VARCHAR(255) NOT NULL",
                "location_id": "VARCHAR(255) NOT NULL",
                "quantity": "INTEGER NOT NULL",
                "reserved_quantity": "INTEGER DEFAULT 0",
                "min_quantity": "INTEGER DEFAULT 0",
                "max_quantity": "INTEGER",
                "last_updated": "TIMESTAMP DEFAULT GETDATE()",
                "created_at": "TIMESTAMP DEFAULT GETDATE()"
            },
            "distkey": "product_id",
            "sortkey": "location_id",
            "indexes": [
                "CREATE INDEX idx_stock_location ON stock(location_id)",
                "CREATE INDEX idx_stock_quantity ON stock(quantity)"
            ]
        },
        "forecasts": {
            "name": "forecasts",
            "description": "Tabela de previsoes",
            "columns": {
                "id": "VARCHAR(255) PRIMARY KEY",
                "product_id": "VARCHAR(255) NOT NULL",
                "location_id": "VARCHAR(255)",
                "forecast_date": "DATE NOT NULL",
                "forecast_value": "DECIMAL(10,2) NOT NULL",
                "confidence_interval_lower": "DECIMAL(10,2)",
                "confidence_interval_upper": "DECIMAL(10,2)",
                "model_version": "VARCHAR(50)",
                "created_at": "TIMESTAMP DEFAULT GETDATE()"
            },
            "distkey": "product_id",
            "sortkey": "forecast_date",
            "indexes": [
                "CREATE INDEX idx_forecasts_location ON forecasts(location_id)",
                "CREATE INDEX idx_forecasts_date ON forecasts(forecast_date)"
            ]
        },
        "customer_segmentation": {
            "name": "customer_segmentation",
            "description": "Tabela de segmentacao de clientes",
            "columns": {
                "id": "VARCHAR(255) PRIMARY KEY",
                "customer_id": "VARCHAR(255) NOT NULL",
                "segment": "VARCHAR(100) NOT NULL",
                "cluster": "INTEGER NOT NULL",
                "recency": "DECIMAL(10,2)",
                "frequency": "DECIMAL(10,2)",
                "monetary": "DECIMAL(12,2)",
                "rfm_score": "INTEGER",
                "probability": "DECIMAL(5,4)",
                "model_version": "VARCHAR(50)",
                "created_at": "TIMESTAMP DEFAULT GETDATE()",
                "updated_at": "TIMESTAMP DEFAULT GETDATE()"
            },
            "distkey": "customer_id",
            "sortkey": "segment",
            "indexes": [
                "CREATE INDEX idx_customer_segmentation_segment ON customer_segmentation(segment)",
                "CREATE INDEX idx_customer_segmentation_cluster ON customer_segmentation(cluster)"
            ]
        }
    }
    
    # Configuracoes de conexao
    CONNECTION_POOL_ENABLED: bool = True
    CONNECTION_POOL_SIZE: int = 10
    CONNECTION_TIMEOUT: int = 30  # segundos
    
    # Configuracoes de query
    QUERY_TIMEOUT: int = 60  # segundos
    MAX_QUERY_LENGTH: int = 100000  # caracteres
    
    # Configuracoes de WLM (Workload Management)
    WLM_QUERY_QUEUE_ENABLED: bool = True
    WLM_QUERY_QUEUE_NAME: str = "gestao-vendas-queue"
    WLM_QUERY_QUEUE_CONCURRENCY: int = 5
    WLM_QUERY_QUEUE_MEMORY: int = 100  # MB
    
    # Configuracoes de VACUUM
    VACUUM_ENABLED: bool = True
    VACUUM_SCHEDULE: str = "0 2 * * *"  # 2 AM todos os dias
    
    # Configuracoes de ANALYZE
    ANALYZE_ENABLED: bool = True
    ANALYZE_SCHEDULE: str = "0 3 * * *"  # 3 AM todos os dias
    
    # Configuracoes de backup
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 1 * * *"  # 1 AM todos os dias
    BACKUP_RETENTION: int = 7  # dias
    
    # Configuracoes de monitoramento
    MONITOR_ENABLED: bool = True
    MONITOR_INTERVAL: int = 300  # 5 minutos
    
    # Configuracoes de logging
    LOG_QUERIES: bool = False  # Logar queries (apenas para debug)
    LOG_SLOW_QUERIES: bool = True
    SLOW_QUERY_THRESHOLD: int = 1000  # milissegundos
    
    @classmethod
    def get_table_config(cls, table_name: str) -> Dict[str, Any]:
        """Obter configuracao de uma tabela"""
        return cls.TABLES.get(table_name, {})
    
    @classmethod
    def get_table_columns(cls, table_name: str) -> Dict[str, str]:
        """Obter colunas de uma tabela"""
        table_config = cls.get_table_config(table_name)
        return table_config.get("columns", {})
    
    @classmethod
    def get_table_ddl(cls, table_name: str) -> str:
        """Gerar DDL para uma tabela"""
        table_config = cls.get_table_config(table_name)
        if not table_config:
            return ""
        
        columns = table_config.get("columns", {})
        distkey = table_config.get("distkey")
        sortkey = table_config.get("sortkey")
        
        # Criar colunas
        column_defs = []
        for col_name, col_type in columns.items():
            column_defs.append(f"    {col_name} {col_type}")
        
        # Criar DDL
        ddl = f"CREATE TABLE {table_name} (\n"
        ddl += ",\n".join(column_defs)
        ddl += "\n)"
        
        # Adicionar DISTKEY
        if distkey:
            ddl += f"\nDISTKEY({distkey})"
        
        # Adicionar SORTKEY
        if sortkey:
            ddl += f"\nSORTKEY({sortkey})"
        
        return ddl
    
    @classmethod
    def get_all_tables_ddl(cls) -> str:
        """Gerar DDL para todas as tabelas"""
        ddl_statements = []
        for table_name in cls.TABLES:
            ddl = cls.get_table_ddl(table_name)
            if ddl:
                ddl_statements.append(ddl)
                
                # Adicionar indexes
                table_config = cls.get_table_config(table_name)
                for index in table_config.get("indexes", []):
                    ddl_statements.append(index)
        
        return ";\n\n".join(ddl_statements)


# Instancia das configuracoes
redshift_config = RedshiftConfig()
