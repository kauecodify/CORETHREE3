"""
CORETHREE3 - Autoatendimento Inteligente
Servico de Gerenciamento de Intencoes

Este servico implementa gerenciamento de intencoes para NLP.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from ..config import lex_config, aws_config
from ..models import Intent, IntentType, IntentDetectionResult
from ..services.nlp_service import nlp_service
from ..utils.cache import cache
from ..utils.retry import retry

logger = logging.getLogger(__name__)


@dataclass
class IntentMatchResult:
    """Resultado do casamento de intencoes"""
    intent: Intent
    score: float
    matched_samples: List[str]
    unmatched_samples: List[str]


class IntentService:
    """Servico de gerenciamento de intencoes"""
    
    def __init__(self):
        """Inicializar servico de intencoes"""
        self.lex_client = None
        self._initialized = False
        self._intents_cache = {}
        
    def _initialize_clients(self):
        """Inicializar clientes AWS"""
        if self._initialized:
            return
            
        try:
            self.lex_client = boto3.client(
                'lexv2-models',
                region_name=aws_config.REGION
            )
            self._initialized = True
            logger.info("Cliente Lex de intencoes inicializado")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Lex: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def create_intent(self, intent: Intent) -> Intent:
        """
        Criar uma nova intencao no Amazon Lex
        
        Args:
            intent: Intencao a ser criada
            
        Returns:
            Intent: Intencao criada
        """
        self._initialize_clients()
        
        try:
            # Validar intencao
            intent_dict = intent.to_lex_format()
            
            # Criar intencao no Lex
            response = self.lex_client.create_intent(
                botId=lex_config.BOT_NAME,
                botVersion='DRAFT',
                localeId=lex_config.BOT_LOCALE,
                intentName=intent.name,
                intentDefinition=intent_dict
            )
            
            # Atualizar cache
            self._intents_cache[intent.name] = intent
            
            logger.info(f"Intencao {intent.name} criada com sucesso")
            return intent
            
        except ClientError as e:
            logger.error(f"Erro ao criar intencao {intent.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar intencao: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def get_intent(self, intent_name: str, use_cache: bool = True) -> Optional[Intent]:
        """
        Obter uma intencao pelo nome
        
        Args:
            intent_name: Nome da intencao
            use_cache: Usar cache
            
        Returns:
            Intent: Intencao ou None
        """
        # Verificar cache
        if use_cache and intent_name in self._intents_cache:
            return self._intents_cache[intent_name]
        
        self._initialize_clients()
        
        try:
            response = self.lex_client.get_intent(
                botId=lex_config.BOT_NAME,
                botVersion='DRAFT',
                localeId=lex_config.BOT_LOCALE,
                intentName=intent_name
            )
            
            # Converter para modelo Intent
            intent_data = response.get('intentDefinition', {})
            intent = Intent(
                id=intent_name,
                name=intent_name,
                description=intent_data.get('description', ''),
                samples=intent_data.get('sampleUtterances', []),
                type=IntentType.CUSTOM,
                metadata={'source': 'lex'}
            )
            
            # Atualizar cache
            self._intents_cache[intent_name] = intent
            
            return intent
            
        except ClientError as e:
            logger.error(f"Erro ao obter intencao {intent_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter intencao: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def list_intents(self, bot_version: str = 'DRAFT', 
                   include_builtin: bool = False) -> List[Intent]:
        """
        Listar todas as intencoes
        
        Args:
            bot_version: Versao do bot
            include_builtin: Incluir intencoes built-in
            
        Returns:
            List[Intent]: Lista de intencoes
        """
        self._initialize_clients()
        
        try:
            response = self.lex_client.list_intents(
                botId=lex_config.BOT_NAME,
                botVersion=bot_version,
                localeId=lex_config.BOT_LOCALE,
                maxResults=100
            )
            
            intents = []
            for intent_summary in response.get('intentSummaries', []):
                intent_name = intent_summary.get('intentName')
                if not include_builtin and intent_name.startswith('AMAZON.'):
                    continue
                    
                intent = self.get_intent(intent_name, use_cache=False)
                if intent:
                    intents.append(intent)
            
            return intents
            
        except ClientError as e:
            logger.error(f"Erro ao listar intencoes: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao listar intencoes: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def update_intent(self, intent: Intent) -> Intent:
        """
        Atualizar uma intencao
        
        Args:
            intent: Intencao a ser atualizada
            
        Returns:
            Intent: Intencao atualizada
        """
        self._initialize_clients()
        
        try:
            intent_dict = intent.to_lex_format()
            
            response = self.lex_client.update_intent(
                botId=lex_config.BOT_NAME,
                botVersion='DRAFT',
                localeId=lex_config.BOT_LOCALE,
                intentName=intent.name,
                intentDefinition=intent_dict
            )
            
            # Atualizar cache
            self._intents_cache[intent.name] = intent
            
            logger.info(f"Intencao {intent.name} atualizada com sucesso")
            return intent
            
        except ClientError as e:
            logger.error(f"Erro ao atualizar intencao {intent.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar intencao: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def delete_intent(self, intent_name: str) -> bool:
        """
        Deletar uma intencao
        
        Args:
            intent_name: Nome da intencao
            
        Returns:
            bool: True se deletado com sucesso
        """
        self._initialize_clients()
        
        try:
            response = self.lex_client.delete_intent(
                botId=lex_config.BOT_NAME,
                botVersion='DRAFT',
                localeId=lex_config.BOT_LOCALE,
                intentName=intent_name
            )
            
            # Remover do cache
            if intent_name in self._intents_cache:
                del self._intents_cache[intent_name]
            
            logger.info(f"Intencao {intent_name} deletada com sucesso")
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao deletar intencao {intent_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao deletar intencao: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    def match_intent(self, text: str, session_id: str,
                   threshold: float = None) -> IntentMatchResult:
        """
        Encontrar a intencao que melhor corresponde a um texto
        
        Args:
            text: Texto a ser analisado
            session_id: ID da sessao
            threshold: Limiar de correspondencia
            
        Returns:
            IntentMatchResult: Resultado do casamento
        """
        threshold = threshold or lex_config.NLP_CONFIDENCE_THRESHOLD
        
        # Detectar intencao
        detection_result = nlp_service.detect_intent(text, session_id)
        
        if not detection_result or detection_result.confidence < threshold:
            # Tentar com fallback
            fallback_intent = self.get_intent(lex_config.FALLBACK_INTENT)
            if fallback_intent:
                return IntentMatchResult(
                    intent=fallback_intent,
                    score=detection_result.confidence if detection_result else 0.0,
                    matched_samples=[],
                    unmatched_samples=fallback_intent.samples
                )
            return None
        
        # Obter intencao
        intent = self.get_intent(detection_result.intent)
        if not intent:
            return None
        
        # Verificar amostras correspondentes
        matched_samples = []
        unmatched_samples = []
        
        for sample in intent.samples:
            sample_result = nlp_service.detect_intent(sample, session_id)
            if sample_result and sample_result.intent == intent.name:
                matched_samples.append(sample)
            else:
                unmatched_samples.append(sample)
        
        return IntentMatchResult(
            intent=intent,
            score=detection_result.confidence,
            matched_samples=matched_samples,
            unmatched_samples=unmatched_samples
        )
    
    @retry(max_attempts=3, delay=0.5)
    def get_fallback_intent(self) -> Optional[Intent]:
        """
        Obter a intencao de fallback
        
        Returns:
            Intent: Intencao de fallback ou None
        """
        return self.get_intent(lex_config.FALLBACK_INTENT)
    
    @retry(max_attempts=3, delay=0.5)
    def get_escalation_intent(self) -> Optional[Intent]:
        """
        Obter a intencao de escalonamento
        
        Returns:
            Intent: Intencao de escalonamento ou None
        """
        return self.get_intent(lex_config.ESCALATION_INTENT)
    
    @retry(max_attempts=3, delay=0.5)
    def get_default_intents(self) -> List[Intent]:
        """
        Obter as intencoes padrao
        
        Returns:
            List[Intent]: Lista de intencoes padrao
        """
        intents = []
        for intent_name in lex_config.DEFAULT_INTENTS:
            intent = self.get_intent(intent_name)
            if intent:
                intents.append(intent)
        return intents
    
    @retry(max_attempts=3, delay=0.5)
    @cache(ttl=3600)
    def get_all_intents_map(self) -> Dict[str, Intent]:
        """
        Obter mapa de todas as intencoes
        
        Returns:
            Dict[str, Intent]: Mapa de intencoes
        """
        intents = self.list_intents()
        return {intent.name: intent for intent in intents}
    
    def validate_intent_samples(self, intent: Intent, 
                               test_samples: List[str]) -> Dict[str, Any]:
        """
        Validar amostras de uma intencao
        
        Args:
            intent: Intencao a ser validada
            test_samples: Amostras de teste
            
        Returns:
            Dict[str, Any]: Resultados da validacao
        """
        results = {
            'intent_name': intent.name,
            'total_tests': len(test_samples),
            'correct': 0,
            'incorrect': 0,
            'accuracy': 0.0,
            'details': []
        }
        
        for sample in test_samples:
            detection_result = nlp_service.detect_intent(
                sample, 
                f"test-{intent.name}"
            )
            
            is_correct = detection_result.intent == intent.name
            
            results['details'].append({
                'sample': sample,
                'detected_intent': detection_result.intent,
                'confidence': detection_result.confidence,
                'is_correct': is_correct
            })
            
            if is_correct:
                results['correct'] += 1
            else:
                results['incorrect'] += 1
        
        if results['total_tests'] > 0:
            results['accuracy'] = results['correct'] / results['total_tests']
        
        return results


# Instancia do servico
intent_service = IntentService()
