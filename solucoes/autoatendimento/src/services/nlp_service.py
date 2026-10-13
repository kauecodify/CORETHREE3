"""
CORETHREE3 - Autoatendimento Inteligente
Servico de Processamento de Linguagem Natural (NLP)

Este servico implementa processamento de linguagem natural utilizando
Amazon Lex, Amazon Comprehend e Amazon Bedrock.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from ..config import lex_config, bedrock_config, aws_config
from ..models import IntentDetectionResult, SlotExtractionResult
from ..utils.cache import cache
from ..utils.retry import retry

logger = logging.getLogger(__name__)


@dataclass
class NLPExtractionResult:
    """Resultado completo da extracao NLP"""
    intent: Optional[IntentDetectionResult] = None
    slots: List[SlotExtractionResult] = None
    entities: Dict[str, Any] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    language: Optional[str] = None
    language_confidence: Optional[float] = None
    is_valid: bool = False
    error: Optional[str] = None


class NLPService:
    """Servico de NLP para autoatendimento"""
    
    def __init__(self):
        """Inicializar servico de NLP"""
        self.lex_client = None
        self.comprehend_client = None
        self.bedrock_client = None
        self.bedrock_runtime_client = None
        self._initialized = False
        
    def _initialize_clients(self):
        """Inicializar clientes AWS"""
        if self._initialized:
            return
            
        try:
            # Lex client
            if lex_config.ENABLE_BEDROCK or True:  # Lex sempre habilitado
                self.lex_client = boto3.client(
                    'lexv2-models',
                    region_name=aws_config.REGION
                )
                self.lex_runtime_client = boto3.client(
                    'lexv2-runtime',
                    region_name=aws_config.REGION
                )
            
            # Comprehend client
            self.comprehend_client = boto3.client(
                'comprehend',
                region_name=aws_config.REGION
            )
            
            # Bedrock clients
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
            logger.info("Clientes AWS de NLP inicializados")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar clientes AWS: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def detect_intent(self, text: str, session_id: str, 
                     bot_id: Optional[str] = None, 
                     bot_alias_id: Optional[str] = None) -> IntentDetectionResult:
        """
        Detectar intencao em um texto utilizando Amazon Lex
        
        Args:
            text: Texto a ser analisado
            session_id: ID da sessao
            bot_id: ID do bot (opcional)
            bot_alias_id: ID do alias do bot (opcional)
            
        Returns:
            IntentDetectionResult: Resultado da deteccao
        """
        self._initialize_clients()
        
        bot_id = bot_id or lex_config.BOT_NAME
        bot_alias_id = bot_alias_id or lex_config.BOT_ALIAS
        
        try:
            response = self.lex_runtime_client.recognize_text(
                botId=bot_id,
                botAliasId=bot_alias_id,
                localeId=lex_config.BOT_LOCALE,
                sessionId=session_id,
                text=text
            )
            
            # Processar resposta
            intent_name = response.get('intentId', '')
            intent_confidence = response.get('intentConfidence', 0.0)
            
            # Extrair slots
            slots = {}
            if 'slots' in response:
                for slot_name, slot_data in response['slots'].items():
                    if slot_data and 'value' in slot_data:
                        slots[slot_name] = {
                            'value': slot_data['value']['interpretedValue'],
                            'raw_value': slot_data['value']['rawValue'],
                            'confidence': slot_data.get('confidence', 1.0)
                        }
            
            # Criar resultado
            result = IntentDetectionResult(
                intent=intent_name,
                intent_id=intent_name,
                confidence=intent_confidence,
                slots=slots,
                alternatives=[]
            )
            
            logger.debug(f"Intencao detectada: {intent_name} (confianca: {intent_confidence})")
            return result
            
        except ClientError as e:
            logger.error(f"Erro ao detectar intencao com Lex: {e}")
            # Retornar intencao de fallback
            return IntentDetectionResult(
                intent=lex_config.FALLBACK_INTENT,
                intent_id=lex_config.FALLBACK_INTENT,
                confidence=0.0,
                slots={},
                alternatives=[]
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao detectar intencao: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    async def detect_intent_async(self, text: str, session_id: str,
                                bot_id: Optional[str] = None,
                                bot_alias_id: Optional[str] = None) -> IntentDetectionResult:
        """
        Detectar intencao de forma assincrona
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.detect_intent(text, session_id, bot_id, bot_alias_id)
        )
    
    @retry(max_attempts=3, delay=0.5)
    @cache(ttl=300)
    def detect_intent_with_bedrock(self, text: str, session_id: str,
                                   context: Optional[Dict[str, Any]] = None) -> IntentDetectionResult:
        """
        Detectar intencao utilizando Amazon Bedrock (LLM)
        
        Args:
            text: Texto a ser analisado
            session_id: ID da sessao
            context: Contexto adicional
            
        Returns:
            IntentDetectionResult: Resultado da deteccao
        """
        if not bedrock_config.ENABLE_BEDROCK:
            return self.detect_intent(text, session_id)
        
        self._initialize_clients()
        
        try:
            # Gerar prompt
            prompt = bedrock_config.get_prompt(
                input_text=text,
                context=str(context or {}),
                history=[]
            )
            
            # Chamar Bedrock
            response = self.bedrock_runtime_client.invoke_model(
                modelId=bedrock_config.DEFAULT_MODEL,
                body=prompt.encode('utf-8'),
                contentType='application/json',
                accept='application/json'
            )
            
            # Processar resposta
            response_body = response['body'].read().decode('utf-8')
            # Aqui seria o processamento da resposta do LLM
            # Para simplificacao, retornamos a intencao do Lex
            return self.detect_intent(text, session_id)
            
        except ClientError as e:
            logger.error(f"Erro ao detectar intencao com Bedrock: {e}")
            return self.detect_intent(text, session_id)
        except Exception as e:
            logger.error(f"Erro inesperado ao detectar intencao com Bedrock: {e}")
            return self.detect_intent(text, session_id)
    
    @retry(max_attempts=3, delay=0.5)
    def extract_slots(self, text: str, intent: str, 
                    session_id: str) -> List[SlotExtractionResult]:
        """
        Extrair slots de um texto para uma intencao especifica
        
        Args:
            text: Texto a ser analisado
            intent: Intencao associada
            session_id: ID da sessao
            
        Returns:
            List[SlotExtractionResult]: Slots extraidos
        """
        self._initialize_clients()
        
        try:
            response = self.lex_runtime_client.recognize_text(
                botId=lex_config.BOT_NAME,
                botAliasId=lex_config.BOT_ALIAS,
                localeId=lex_config.BOT_LOCALE,
                sessionId=session_id,
                text=text,
                intentId=intent
            )
            
            # Processar slots
            slots = []
            if 'slots' in response:
                for slot_name, slot_data in response['slots'].items():
                    if slot_data and 'value' in slot_data:
                        slots.append(SlotExtractionResult(
                            slot=slot_name,
                            value=slot_data['value']['interpretedValue'],
                            confidence=slot_data.get('confidence', 1.0),
                            start_index=0,
                            end_index=len(slot_data['value']['rawValue']),
                            metadata={}
                        ))
            
            return slots
            
        except ClientError as e:
            logger.error(f"Erro ao extrair slots: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao extrair slots: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def detect_entities(self, text: str, language: str = "pt") -> Dict[str, Any]:
        """
        Detectar entidades em um texto utilizando Amazon Comprehend
        
        Args:
            text: Texto a ser analisado
            language: Idioma do texto
            
        Returns:
            Dict[str, Any]: Entidades detectadas
        """
        self._initialize_clients()
        
        try:
            response = self.comprehend_client.detect_entities(
                Text=text,
                LanguageCode=language
            )
            
            # Processar entidades
            entities = {}
            for entity in response.get('Entities', []):
                entity_type = entity['Type']
                if entity_type not in entities:
                    entities[entity_type] = []
                entities[entity_type].append({
                    'text': entity['Text'],
                    'score': entity['Score'],
                    'begin_offset': entity['BeginOffset'],
                    'end_offset': entity['EndOffset']
                })
            
            return entities
            
        except ClientError as e:
            logger.error(f"Erro ao detectar entidades: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro inesperado ao detectar entidades: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def detect_sentiment(self, text: str, language: str = "pt") -> Tuple[Optional[str], Optional[float]]:
        """
        Detectar sentimento em um texto utilizando Amazon Comprehend
        
        Args:
            text: Texto a ser analisado
            language: Idioma do texto
            
        Returns:
            Tuple[Optional[str], Optional[float]]: Sentimento e score
        """
        self._initialize_clients()
        
        try:
            response = self.comprehend_client.detect_sentiment(
                Text=text,
                LanguageCode=language
            )
            
            sentiment = response.get('Sentiment')
            sentiment_score = None
            
            if sentiment in ['POSITIVE', 'NEGATIVE']:
                sentiment_score = response.get('SentimentScore', {}).get(sentiment.lower(), 0.0)
            elif sentiment == 'NEUTRAL':
                sentiment_score = 0.0
            elif sentiment == 'MIXED':
                positive = response.get('SentimentScore', {}).get('Positive', 0.0)
                negative = response.get('SentimentScore', {}).get('Negative', 0.0)
                sentiment_score = positive - negative
            
            return sentiment, sentiment_score
            
        except ClientError as e:
            logger.error(f"Erro ao detectar sentimento: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Erro inesperado ao detectar sentimento: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def detect_language(self, text: str) -> Tuple[Optional[str], Optional[float]]:
        """
        Detectar idioma de um texto utilizando Amazon Comprehend
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Tuple[Optional[str], Optional[float]]: Idioma e confianca
        """
        self._initialize_clients()
        
        try:
            response = self.comprehend_client.detect_dominant_language(
                Text=text
            )
            
            languages = response.get('Languages', [])
            if languages:
                return languages[0]['LanguageCode'], languages[0]['Score']
            return None, None
            
        except ClientError as e:
            logger.error(f"Erro ao detectar idioma: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Erro inesperado ao detectar idioma: {e}")
            raise
    
    def extract_all(self, text: str, session_id: str,
                   context: Optional[Dict[str, Any]] = None) -> NLPExtractionResult:
        """
        Extrair todas as informacoes NLP de um texto
        
        Args:
            text: Texto a ser analisado
            session_id: ID da sessao
            context: Contexto adicional
            
        Returns:
            NLPExtractionResult: Resultado completo da extracao
        """
        result = NLPExtractionResult()
        
        try:
            # Detectar intencao
            result.intent = self.detect_intent(text, session_id)
            
            # Extrair slots
            if result.intent:
                result.slots = self.extract_slots(
                    text, result.intent.intent, session_id
                )
            
            # Detectar entidades
            result.entities = self.detect_entities(text)
            
            # Detectar sentimento
            result.sentiment, result.sentiment_score = self.detect_sentiment(text)
            
            # Detectar idioma
            result.language, result.language_confidence = self.detect_language(text)
            
            # Validar
            result.is_valid = (
                result.intent is not None and 
                result.intent.confidence >= lex_config.NLP_CONFIDENCE_THRESHOLD
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao extrair informacoes NLP: {e}")
            result.is_valid = False
            result.error = str(e)
            return result


# Instancia do servico
nlp_service = NLPService()
