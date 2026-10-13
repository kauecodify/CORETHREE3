"""
CORETHREE3 - Autoatendimento Inteligente
Servico de Amazon Bedrock para IA Generativa

Este servico implementa integracao com Amazon Bedrock para
IA generativa, embeddings e modelos de linguagem avancados.
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import boto3
import numpy as np
from botocore.exceptions import ClientError, BotoCoreError

from ..config import bedrock_config, aws_config
from ..models import IntentDetectionResult
from ..utils.cache import cache
from ..utils.retry import retry

logger = logging.getLogger(__name__)


@dataclass
class BedrockResponse:
    """Resposta do Bedrock"""
    text: str
    model_id: str
    input_tokens: int
    output_tokens: int
    latency: float
    finish_reason: str
    metadata: Dict[str, Any]


@dataclass
class EmbeddingResult:
    """Resultado de embedding"""
    embedding: List[float]
    model_id: str
    dimension: int
    input_tokens: int
    latency: float
    metadata: Dict[str, Any]


class BedrockService:
    """Servico de Amazon Bedrock"""
    
    def __init__(self):
        """Inicializar servico de Bedrock"""
        self.bedrock_client = None
        self.bedrock_runtime_client = None
        self._initialized = False
        self._model_cache = {}
        
    def _initialize_clients(self):
        """Inicializar clientes AWS"""
        if self._initialized:
            return
            
        try:
            if bedrock_config.ENABLE_BEDROCK:
                self.bedrock_client = boto3.client(
                    'bedrock',
                    region_name=bedrock_config.BEDROCK_REGION
                )
                self.bedrock_runtime_client = boto3.client(
                    'bedrock-runtime',
                    region_name=bedrock_config.BEDROCK_REGION
                )
                self._initialized = True
                logger.info("Clientes Bedrock inicializados")
            else:
                logger.warning("Bedrock desabilitado")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar clientes Bedrock: {e}")
            raise
    
    def _get_model_config(self, model_id: str = None) -> Dict[str, Any]:
        """Obter configuracao do modelo"""
        model_id = model_id or bedrock_config.DEFAULT_MODEL
        return bedrock_config.get_model_config(model_id)
    
    @retry(max_attempts=3, delay=1.0)
    def list_models(self, by_provider: bool = False, 
                   by_customization_type: bool = False) -> List[Dict[str, Any]]:
        """
        Listar modelos disponiveis no Bedrock
        
        Args:
            by_provider: Agrupar por provedor
            by_customization_type: Agrupar por tipo de customizacao
            
        Returns:
            List[Dict[str, Any]]: Lista de modelos
        """
        self._initialize_clients()
        
        try:
            response = self.bedrock_client.list_foundation_models(
                byProvider=by_provider,
                byCustomizationType=by_customization_type
            )
            return response.get('modelSummaries', [])
            
        except ClientError as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao listar modelos: {e}")
            raise
    
    @retry(max_attempts=3, delay=1.0)
    def get_model_details(self, model_identifier: str) -> Dict[str, Any]:
        """
        Obter detalhes de um modelo
        
        Args:
            model_identifier: Identificador do modelo
            
        Returns:
            Dict[str, Any]: Detalhes do modelo
        """
        self._initialize_clients()
        
        try:
            response = self.bedrock_client.get_foundation_model(
                modelIdentifier=model_identifier
            )
            return response.get('modelDetails', {})
            
        except ClientError as e:
            logger.error(f"Erro ao obter detalhes do modelo {model_identifier}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro inesperado ao obter detalhes do modelo: {e}")
            raise
    
    @retry(max_attempts=3, delay=1.0)
    def generate_text(self, prompt: str, model_id: str = None,
                     config: Dict[str, Any] = None) -> BedrockResponse:
        """
        Gerar texto utilizando modelo de linguagem
        
        Args:
            prompt: Prompt de entrada
            model_id: ID do modelo
            config: Configuracoes adicionais
            
        Returns:
            BedrockResponse: Resposta gerada
        """
        self._initialize_clients()
        
        if not bedrock_config.ENABLE_BEDROCK:
            raise Exception("Bedrock esta desabilitado")
        
        model_id = model_id or bedrock_config.DEFAULT_MODEL
        model_config = self._get_model_config(model_id)
        
        # Mesclar configuracoes
        if config:
            model_config.update(config)
        
        start_time = time.time()
        
        try:
            # Preparar corpo da requisicao
            request_body = self._prepare_text_request(
                model_id, prompt, model_config
            )
            
            # Chamar Bedrock
            response = self.bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body).encode('utf-8'),
                contentType='application/json',
                accept='application/json'
            )
            
            # Processar resposta
            response_body = response['body'].read().decode('utf-8')
            response_data = json.loads(response_body)
            
            # Extrair texto
            text = self._extract_text_from_response(model_id, response_data)
            
            # Calcular latencia
            latency = (time.time() - start_time) * 1000
            
            # Criar resultado
            result = BedrockResponse(
                text=text,
                model_id=model_id,
                input_tokens=len(prompt.split()),
                output_tokens=len(text.split()),
                latency=latency,
                finish_reason=response_data.get('finish_reason', 'unknown'),
                metadata={
                    'model_config': model_config,
                    'raw_response': response_data
                }
            )
            
            logger.debug(f"Texto gerado: {text[:100]}...")
            return result
            
        except ClientError as e:
            logger.error(f"Erro ao gerar texto com Bedrock: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao gerar texto: {e}")
            raise
    
    def _prepare_text_request(self, model_id: str, prompt: str,
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """Preparar requisicao de texto para Bedrock"""
        
        # Configuracoes padrao para modelos Anthropic
        if model_id.startswith('anthropic.claude'):
            return {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": config.get('max_tokens', 4096),
                "temperature": config.get('temperature', 0.7),
                "top_p": config.get('top_p', 0.9),
                "top_k": config.get('top_k', 250),
            }
        
        # Configuracoes para modelos Amazon Titan
        elif model_id.startswith('amazon.titan'):
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": config.get('maxTokenCount', 4096),
                    "temperature": config.get('temperature', 0.7),
                    "topP": config.get('topP', 0.9),
                }
            }
        
        # Configuracoes para modelos AI21
        elif model_id.startswith('ai21.'):
            return {
                "prompt": prompt,
                "maxTokens": config.get('max_tokens', 4096),
                "temperature": config.get('temperature', 0.7),
                "topP": config.get('top_p', 0.9),
            }
        
        # Configuracoes para modelos Cohere
        elif model_id.startswith('cohere.'):
            return {
                "prompt": prompt,
                "max_tokens": config.get('max_tokens', 4096),
                "temperature": config.get('temperature', 0.7),
                "p": config.get('top_p', 0.9),
                "k": config.get('top_k', 250),
            }
        
        # Configuracoes para modelos Meta Llama
        elif model_id.startswith('meta.llama'):
            return {
                "prompt": prompt,
                "max_gen_len": config.get('max_tokens', 4096),
                "temperature": config.get('temperature', 0.7),
                "top_p": config.get('top_p', 0.9),
            }
        
        # Padrao
        return {"prompt": prompt}
    
    def _extract_text_from_response(self, model_id: str, 
                                    response_data: Dict[str, Any]) -> str:
        """Extrair texto da resposta do Bedrock"""
        
        # Modelos Anthropic
        if model_id.startswith('anthropic.claude'):
            return response_data.get('completion', '')
        
        # Modelos Amazon Titan
        elif model_id.startswith('amazon.titan'):
            return response_data.get('results', [{}])[0].get('outputText', '')
        
        # Modelos AI21
        elif model_id.startswith('ai21.'):
            return response_data.get('completions', [{}])[0].get('data', {}).get('text', '')
        
        # Modelos Cohere
        elif model_id.startswith('cohere.'):
            return response_data.get('generations', [{}])[0].get('text', '')
        
        # Modelos Meta Llama
        elif model_id.startswith('meta.llama'):
            return response_data.get('generation', '')
        
        # Padrao
        return str(response_data)
    
    @retry(max_attempts=3, delay=1.0)
    async def generate_text_async(self, prompt: str, model_id: str = None,
                                  config: Dict[str, Any] = None) -> BedrockResponse:
        """
        Gerar texto de forma assincrona
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate_text(prompt, model_id, config)
        )
    
    @retry(max_attempts=3, delay=1.0)
    @cache(ttl=300)
    def generate_embedding(self, text: str, model_id: str = None) -> EmbeddingResult:
        """
        Gerar embedding de um texto
        
        Args:
            text: Texto a ser processado
            model_id: ID do modelo de embedding
            
        Returns:
            EmbeddingResult: Resultado do embedding
        """
        self._initialize_clients()
        
        if not bedrock_config.ENABLE_BEDROCK:
            raise Exception("Bedrock esta desabilitado")
        
        model_id = model_id or bedrock_config.EMBEDDING_MODEL
        
        start_time = time.time()
        
        try:
            # Preparar requisicao
            request_body = {
                "inputText": text
            }
            
            # Chamar Bedrock
            response = self.bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body).encode('utf-8'),
                contentType='application/json',
                accept='application/json'
            )
            
            # Processar resposta
            response_body = response['body'].read().decode('utf-8')
            response_data = json.loads(response_body)
            
            # Extrair embedding
            embedding = response_data.get('embedding', [])
            dimension = len(embedding)
            
            # Calcular latencia
            latency = (time.time() - start_time) * 1000
            
            # Criar resultado
            result = EmbeddingResult(
                embedding=embedding,
                model_id=model_id,
                dimension=dimension,
                input_tokens=len(text.split()),
                latency=latency,
                metadata={
                    'raw_response': response_data
                }
            )
            
            return result
            
        except ClientError as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao gerar embedding: {e}")
            raise
    
    @retry(max_attempts=3, delay=1.0)
    def generate_embeddings(self, texts: List[str], model_id: str = None) -> List[EmbeddingResult]:
        """
        Gerar embeddings para multiplos textos
        
        Args:
            texts: Lista de textos
            model_id: ID do modelo
            
        Returns:
            List[EmbeddingResult]: Lista de resultados
        """
        results = []
        for text in texts:
            result = self.generate_embedding(text, model_id)
            results.append(result)
        return results
    
    @retry(max_attempts=3, delay=1.0)
    def compare_embeddings(self, embedding1: List[float], 
                         embedding2: List[float]) -> float:
        """
        Comparar dois embeddings (similaridade de cosseno)
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
            
        Returns:
            float: Similaridade (0-1)
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings devem ter a mesma dimensao")
        
        # Calcular similaridade de cosseno
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    @retry(max_attempts=3, delay=1.0)
    def find_similar_embeddings(self, query_embedding: List[float],
                               embeddings: List[List[float]],
                               top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Encontrar embeddings similares
        
        Args:
            query_embedding: Embedding da consulta
            embeddings: Lista de embeddings para comparar
            top_k: Numero de resultados
            
        Returns:
            List[Tuple[int, float]]: Lista de (indice, similaridade)
        """
        similarities = []
        for i, embedding in enumerate(embeddings):
            similarity = self.compare_embeddings(query_embedding, embedding)
            similarities.append((i, similarity))
        
        # Ordenar por similaridade (descendente)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    @retry(max_attempts=3, delay=1.0)
    def generate_response(self, prompt: str, session_id: str,
                        context: Optional[Dict[str, Any]] = None,
                        history: Optional[List[Dict[str, str]]] = None) -> BedrockResponse:
        """
        Gerar resposta para autoatendimento
        
        Args:
            prompt: Prompt do usuario
            session_id: ID da sessao
            context: Contexto adicional
            history: Historico da conversa
            
        Returns:
            BedrockResponse: Resposta gerada
        """
        # Gerar prompt formatado
        formatted_prompt = bedrock_config.get_prompt(
            input_text=prompt,
            context=json.dumps(context or {}),
            history=json.dumps(history or [])
        )
        
        # Gerar texto
        return self.generate_text(
            prompt=formatted_prompt,
            config={
                'temperature': 0.7,
                'max_tokens': 2000
            }
        )
    
    @retry(max_attempts=3, delay=1.0)
    def extract_intent_with_llm(self, text: str, session_id: str,
                             context: Optional[Dict[str, Any]] = None) -> IntentDetectionResult:
        """
        Extrair intencao utilizando LLM
        
        Args:
            text: Texto a ser analisado
            session_id: ID da sessao
            context: Contexto adicional
            
        Returns:
            IntentDetectionResult: Resultado da deteccao
        """
        # Prompt para extracao de intencao
        intent_prompt = f"""
        Voce e um especialista em classificacao de intencoes para autoatendimento.
        
        Tarefa: Classificar o texto a seguir em uma das intencoes disponiveis.
        
        Intencoes disponiveis:
        - Saudacao: Mensagens de saudacao ou cumprimento
        - Despedida: Mensagens de despedida
        - Ajuda: Pedidos de ajuda ou informacoes
        - StatusPedido: Consultas sobre status de pedidos
        - AgendarServico: Solicitacoes para agendar servicos
        - CancelarPedido: Pedidos para cancelar pedidos
        - FalarComHumano: Solicitacoes para falar com um humano
        - PesquisaSatisfacao: Feedback ou pesquisas de satisfacao
        - FallbackIntent: Qualquer outra intencao nao identificada
        
        Texto: "{text}"
        
        Responda apenas com o nome da intencao (uma palavra).
        """
        
        # Gerar resposta
        response = self.generate_text(
            prompt=intent_prompt,
            config={
                'temperature': 0.1,  # Baixa temperatura para classificacao
                'max_tokens': 50
            }
        )
        
        # Processar resposta
        intent_name = response.text.strip()
        
        # Validar intencao
        default_intents = [
            "Saudacao", "Despedida", "Ajuda", "StatusPedido",
            "AgendarServico", "CancelarPedido", "FalarComHumano",
            "PesquisaSatisfacao", "FallbackIntent"
        ]
        
        if intent_name not in default_intents:
            intent_name = "FallbackIntent"
        
        # Criar resultado
        return IntentDetectionResult(
            intent=intent_name,
            intent_id=intent_name,
            confidence=1.0,  # Confianca maxima para LLM
            slots={},
            alternatives=[],
            metadata={
                'source': 'llm',
                'model': bedrock_config.DEFAULT_MODEL
            }
        )


# Instancia do servico
bedrock_service = BedrockService()
