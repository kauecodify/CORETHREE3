"""
CORETHREE3 - Autoatendimento Inteligente
Modelos de Dados

Este modulo contem os modelos de dados utilizados no autoatendimento.
"""

from .intent import Intent, IntentType
from .slot import Slot, SlotType
from .conversation import Conversation, ConversationStatus
from .session import Session
from .message import Message, MessageType
from .user import User
from .knowledge import KnowledgeItem, KnowledgeCategory
from .response import Response, ResponseType
