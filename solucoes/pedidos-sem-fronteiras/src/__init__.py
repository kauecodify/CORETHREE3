"""
CORETHREE3 - Pedidos Sem Fronteiras
Pacote Principal

Este pacote contem todos os modulos do sistema Pedidos Sem Fronteiras.
"""

from .models import (
    Order,
    OrderStatus,
    OrderPriority,
    Customer,
    Product,
    Shipment,
    ShipmentStatus,
    Address,
    Inventory,
    Route,
    Waypoint
)

from .services import (
    OrderService,
    CustomerService,
    ProductService,
    ShipmentService,
    TrackingService,
    InventoryService,
    RoutingService
)

from .handlers import (
    OrderHandler,
    TrackingHandler,
    InventoryHandler,
    RoutingHandler
)

from .config import (
    aws_config,
    database_config
)

__all__ = [
    # Modelos
    "Order",
    "OrderStatus",
    "OrderPriority",
    "Customer",
    "Product",
    "Shipment",
    "ShipmentStatus",
    "Address",
    "Inventory",
    "Route",
    "Waypoint",
    
    # Servicos
    "OrderService",
    "CustomerService",
    "ProductService",
    "ShipmentService",
    "TrackingService",
    "InventoryService",
    "RoutingService",
    
    # Handlers
    "OrderHandler",
    "TrackingHandler",
    "InventoryHandler",
    "RoutingHandler",
    
    # Configuracoes
    "aws_config",
    "database_config"
]
