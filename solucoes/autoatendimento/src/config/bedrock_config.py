"""
CORETHREE3 - Autoatendimento Inteligente
Configuracoes do Amazon Bedrock
"""

import os
from typing import Dict, List, Any


class BedrockConfig:
    """Configuracoes do Amazon Bedrock para IA generativa"""
    
    # Configuracoes gerais
    ENABLE_BEDROCK: bool = os.getenv("ENABLE_BEDROCK", "True").lower() == "true"
    BEDROCK_REGION: str = os.getenv("BEDROCK_REGION", "us-east-1")
    
    # Modelos disponiveis
    AVAILABLE_MODELS: List[str] = [
        "anthropic.claude-v2",
        "anthropic.claude-v2:1",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "amazon.titan-text-express-v1",
        "amazon.titan-text-lite-v1",
        "amazon.titan-embed-text-v1",
        "ai21.j2-mid-v1",
        "ai21.j2-ultra-v1",
        "cohere.command-text-v14",
        "cohere.command-light-text-v14",
        "meta.llama2-13b-chat-v1",
        "meta.llama2-70b-chat-v1",
        "stability.stable-diffusion-xl-v1",
    ]
    
    # Modelo padrao
    DEFAULT_MODEL: str = os.getenv("BEDROCK_DEFAULT_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
    
    # Configuracoes do modelo
    MODEL_CONFIG: Dict[str, Any] = {
        "anthropic.claude-v2": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 250,
        },
        "anthropic.claude-3-sonnet-20240229-v1:0": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 250,
        },
        "amazon.titan-text-express-v1": {
            "maxTokenCount": 4096,
            "temperature": 0.7,
            "topP": 0.9,
        },
        "amazon.titan-text-lite-v1": {
            "maxTokenCount": 4096,
            "temperature": 0.7,
            "topP": 0.9,
        },
    }
    
    # Configuracoes de prompt
    PROMPT_TEMPLATE: str = """
    Voce e um assistente de autoatendimento inteligente do CORETHREE3.
    
    Regras:
    1. Responda em portugues do Brasil
    2. Seja claro, objetivo e direto
    3. Se nao souber a resposta, diga que nao sabe
    4. Nao invente informacoes
    5. Use o contexto fornecido para personalizar a resposta
    
    Contexto:
    {context}
    
    Historico da conversa:
    {history}
    
    Usuario: {input}
    
    Assistente:
    """
    
    # Configuracoes de contexto
    CONTEXT_WINDOW: int = 5  # Numero de mensagens anteriores a considerar
    MAX_CONTEXT_LENGTH: int = 4000  # Tokens
    
    # Configuracoes de seguranca
    CONTENT_POLICY: str = "BLOCK"  # BLOCK, FILTER, ALLOW
    CONTENT_POLICY_NAME: str = os.getenv("BEDROCK_CONTENT_POLICY", "corethree3-policy")
    
    # Configuracoes de logging
    LOG_INPUTS: bool = True
    LOG_OUTPUTS: bool = True
    LOG_METRICS: bool = True
    
    # Configuracoes de cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # Segundos
    
    # Configuracoes de rate limiting
    RATE_LIMIT_REQUESTS: int = 100  # Requests por minuto
    RATE_LIMIT_TOKENS: int = 100000  # Tokens por minuto
    
    # Configuracoes de timeout
    TIMEOUT: int = 30  # Segundos
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: float = 1.0  # Segundos
    
    # Configuracoes de embeddings
    EMBEDDING_MODEL: str = os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v1")
    EMBEDDING_DIMENSION: int = 1536  # Dimensoes do embedding
    
    # Configuracoes de base de conhecimento
    KNOWLEDGE_BASE_BUCKET: str = os.getenv("KNOWLEDGE_BASE_BUCKET", "corethree3-knowledge")
    KNOWLEDGE_BASE_PREFIX: str = "autoatendimento"
    KNOWLEDGE_INDEX_NAME: str = "autoatendimento-knowledge-index"
    
    # Configuracoes de busca
    SEARCH_TOP_K: int = 5  # Numero de resultados
    SEARCH_SIMILARITY_THRESHOLD: float = 0.7  # Similaridade minima
    
    @classmethod
    def get_model_config(cls, model_id: str) -> Dict[str, Any]:
        """Obter configuracao de um modelo"""
        return cls.MODEL_CONFIG.get(model_id, cls.MODEL_CONFIG[cls.DEFAULT_MODEL])
    
    @classmethod
    def get_prompt(cls, input_text: str, context: str = "", history: List[str] = None) -> str:
        """Gerar prompt formatado"""
        history_text = "\n".join(history or [])
        return cls.PROMPT_TEMPLATE.format(
            context=context,
            history=history_text,
            input=input_text
        )


# Instancia das configuracoes
bedrock_config = BedrockConfig()
