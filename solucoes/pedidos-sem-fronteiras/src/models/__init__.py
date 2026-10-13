"""
CORETHREE3 - Pedidos Sem Fronteiras
Modelos de Dados

Este modulo contem todos os modelos de dados Pydantic para o sistema Pedidos Sem Fronteiras.
"""

from .order import Order, OrderStatus, OrderPriority, OrderItem
from .customer import Customer, CustomerType
from .product import Product, ProductCategory, ProductStatus
from .shipment import Shipment, ShipmentStatus, ShipmentType
from .address import Address
from .inventory import Inventory
from .route import Route, Waypoint, RouteStatus

__all__ = [
    "Order",
    "OrderStatus",
    "OrderPriority",
    "OrderItem",
    "Customer",
    "CustomerType",
    "Product",
    "ProductCategory",
    "ProductStatus",
    "Shipment",
    "ShipmentStatus",
    "ShipmentType",
    "Address",
    "Inventory",
    "Route",
    "Waypoint",
    "RouteStatus"
]
