"""
CORETHREE3 - Autoatendimento Inteligente
Configuracoes do Amazon Lex
"""

import os
from typing import Dict, List, Any


class LexConfig:
    """Configuracoes do Amazon Lex para autoatendimento"""
    
    # Nome do bot
    BOT_NAME: str = os.getenv("LEX_BOT_NAME", "CORETHREE3-Autoatendimento")
    BOT_DESCRIPTION: str = "Chatbot de autoatendimento inteligente do CORETHREE3"
    BOT_ALIAS: str = os.getenv("LEX_BOT_ALIAS", "prod")
    
    # Configuracoes do bot
    BOT_LOCALE: str = os.getenv("LEX_BOT_LOCALE", "pt_BR")
    BOT_VOICE: str = os.getenv("LEX_BOT_VOICE", "Vitoria")  # Voz para TTS
    BOT_TIMEOUT: int = 10  # Segundos
    BOT_MAX_LENGTH: int = 200  # Caracteres
    
    # Configuracoes de sessao
    SESSION_TIMEOUT: int = 300  # Segundos (5 minutos)
    SESSION_MAX_LENGTH: int = 1000  # Caracteres
    
    # Intencoes padrao
    DEFAULT_INTENTS: List[str] = [
        "Saudacao",
        "Despedida",
        "Ajuda",
        "StatusPedido",
        "AgendarServico",
        "CancelarPedido",
        "FalarComHumano",
        "PesquisaSatisfacao",
    ]
    
    # Slots padrao
    DEFAULT_SLOTS: Dict[str, Dict[str, Any]] = {
        "numeroPedido": {
            "type": "AMAZON.NUMBER",
            "description": "Numero do pedido",
            "required": True,
        },
        "data": {
            "type": "AMAZON.DATE",
            "description": "Data do agendamento",
            "required": True,
        },
        "horario": {
            "type": "AMAZON.TIME",
            "description": "Horario do agendamento",
            "required": True,
        },
        "tipoServico": {
            "type": "AMAZON.AlphaNumeric",
            "description": "Tipo de servico",
            "required": True,
            "enumerationValues": ["manutencao", "suporte", "consulta", "reclamacao"],
        },
        "nota": {
            "type": "AMAZON.NUMBER",
            "description": "Nota de satisfacao (1-5)",
            "required": True,
            "minValue": 1,
            "maxValue": 5,
        },
    }
    
    # Configuracoes de NLP
    NLP_ENGINE: str = os.getenv("NLP_ENGINE", "LEX")  # LEX, COMPREHEND, BEDROCK
    NLP_CONFIDENCE_THRESHOLD: float = 0.7  # 70% de confianca minima
    NLP_MAX_ALTERNATIVES: int = 3  # Numero maximo de alternativas
    
    # Configuracoes de fallback
    FALLBACK_INTENT: str = "FallbackIntent"
    FALLBACK_RESPONSE: str = "Desculpe, nao entendi. Poderia reformular?"
    FALLBACK_MAX_ATTEMPTS: int = 3
    
    # Configuracoes de escalonamento
    ESCALATION_INTENT: str = "FalarComHumano"
    ESCALATION_THRESHOLD: int = 3  # Tentativas antes de escalar
    ESCALATION_CHANNEL: str = "chat"  # chat, email, telefone
    
    # Configuracoes de personalizacao
    CUSTOM_VOCABULARY: str = os.getenv("LEX_CUSTOM_VOCABULARY", "")
    CUSTOM_INTENT_CLASSIFIER: str = os.getenv("LEX_CUSTOM_CLASSIFIER", "")
    
    # Configuracoes de logging
    LOG_CONVERSATIONS: bool = True
    LOG_INTENTS: bool = True
    LOG_SLOTS: bool = True
    
    @classmethod
    def get_intent_config(cls, intent_name: str) -> Dict[str, Any]:
        """Obter configuracao de uma intencao"""
        intents_config = {
            "Saudacao": {
                "description": "Intencao de saudacao inicial",
                "samples": [
                    "Ola",
                    "Bom dia",
                    "Boa tarde",
                    "Boa noite",
                    "E ai",
                    "Tudo bem?",
                ],
                "response": "Ola! Como posso te ajudar hoje?",
                "slots": [],
            },
            "Despedida": {
                "description": "Intencao de despedida",
                "samples": [
                    "Tchau",
                    "Adeus",
                    "Ate mais",
                    "Fui",
                    "Obrigado",
                    "Agradeco",
                ],
                "response": "Obrigado por entrar em contato! Tenha um otimo dia!",
                "slots": [],
            },
            "Ajuda": {
                "description": "Intencao de ajuda",
                "samples": [
                    "Ajuda",
                    "Socorro",
                    "Nao sei o que fazer",
                    "Preciso de ajuda",
                    "O que voce pode fazer?",
                ],
                "response": "Posso te ajudar com: status de pedidos, agendamento de servicos, cancelamento de pedidos, entre outros. O que voce precisa?",
                "slots": [],
            },
            "StatusPedido": {
                "description": "Consultar status de pedido",
                "samples": [
                    "Onde esta meu pedido?",
                    "Qual o status do meu pedido?",
                    "Meu pedido ainda nao chegou",
                    "Como esta meu pedido {numeroPedido}?",
                ],
                "response": "Vou verificar o status do seu pedido {numeroPedido}.",
                "slots": ["numeroPedido"],
                "fulfillment": "lambda:CORETHREE3-Autoatendimento-StatusPedido",
            },
            "AgendarServico": {
                "description": "Agendar servico",
                "samples": [
                    "Preciso agendar uma manutencao",
                    "Gostaria de marcar um servico",
                    "Quero agendar {tipoServico} para {data} as {horario}",
                    "Como faço para agendar?",
                ],
                "response": "Vou agendar um {tipoServico} para voce. Qual data e horario preferem?",
                "slots": ["tipoServico", "data", "horario"],
                "fulfillment": "lambda:CORETHREE3-Autoatendimento-AgendarServico",
            },
        }
        return intents_config.get(intent_name, {})


# Instancia das configuracoes
lex_config = LexConfig()
