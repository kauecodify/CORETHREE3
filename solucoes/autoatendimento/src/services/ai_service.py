"""
CORETHREE3 - Autoatendimento Inteligente
Servico de IA para Autoatendimento

Este servico integra NLP, Bedrock e Lex para fornecer
uma solucao de IA completa para autoatendimento.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from ..config import settings, lex_config, bedrock_config
from ..models import (
    IntentDetectionResult, 
    SlotExtractionResult, 
    Conversation,
    Message,
    Response
)
from ..services.nlp_service import nlp_service, NLPExtractionResult
from ..services.bedrock_service import bedrock_service, BedrockResponse
from ..services.intent_service import intent_service
from ..services.slot_service import slot_service
from ..services.knowledge_service import knowledge_service
from ..utils.cache import cache
from ..utils.retry import retry

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Resposta completa da IA"""
    response: Response
    intent: Optional[IntentDetectionResult]
    slots: List[SlotExtractionResult]
    entities: Dict[str, Any]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    knowledge_used: Optional[Any]
    actions: List[Dict[str, Any]]
    confidence: float
    is_fallback: bool
    should_escalate: bool


class AIService:
    """Servico de IA para autoatendimento"""
    
    def __init__(self):
        """Inicializar servico de IA"""
        self._initialized = False
        
    def _initialize(self):
        """Inicializar servicos"""
        if self._initialized:
            return
        
        # Todos os servicos ja sao inicializados separadamente
        self._initialized = True
        logger.info("Servico de IA inicializado")
    
    @retry(max_attempts=3, delay=0.5)
    def process_message(self, message: Message, 
                       conversation: Optional[Conversation] = None) -> AIResponse:
        """
        Processar uma mensagem e gerar resposta
        
        Args:
            message: Mensagem a ser processada
            conversation: Conversa associada (opcional)
            
        Returns:
            AIResponse: Resposta completa da IA
        """
        self._initialize()
        
        try:
            # Extrair texto da mensagem
            text = self._extract_text_from_message(message)
            if not text:
                return self._create_fallback_response(message, "Mensagem vazia")
            
            # Extrair informacoes NLP
            nlp_result = nlp_service.extract_all(
                text=text,
                session_id=message.session_id,
                context=self._get_context(conversation)
            )
            
            # Verificar se e valido
            if not nlp_result.is_valid:
                logger.warning(f"NLP invalido: {nlp_result.error}")
                return self._create_fallback_response(message, nlp_result.error)
            
            # Obter intencao
            intent = nlp_result.intent
            
            # Verificar se precisa de escalonamento
            should_escalate = self._should_escalate(intent, conversation)
            
            # Buscar na base de conhecimento
            knowledge_result = None
            if intent and intent.intent != lex_config.FALLBACK_INTENT:
                knowledge_result = knowledge_service.search(
                    query=text,
                    intent=intent.intent,
                    slots=nlp_result.slots
                )
            
            # Gerar resposta
            response = self._generate_response(
                message=message,
                intent=intent,
                slots=nlp_result.slots,
                entities=nlp_result.entities,
                sentiment=nlp_result.sentiment,
                sentiment_score=nlp_result.sentiment_score,
                knowledge_result=knowledge_result,
                conversation=conversation
            )
            
            # Determinar acoes
            actions = self._determine_actions(
                intent=intent,
                slots=nlp_result.slots,
                conversation=conversation
            )
            
            # Criar resposta completa
            ai_response = AIResponse(
                response=response,
                intent=intent,
                slots=nlp_result.slots or [],
                entities=nlp_result.entities or {},
                sentiment=nlp_result.sentiment,
                sentiment_score=nlp_result.sentiment_score,
                knowledge_used=knowledge_result,
                actions=actions,
                confidence=intent.confidence if intent else 0.0,
                is_fallback=intent.intent == lex_config.FALLBACK_INTENT if intent else True,
                should_escalate=should_escalate
            )
            
            logger.debug(f"Mensagem processada: intent={intent.intent if intent else 'None'}, confidence={ai_response.confidence}")
            return ai_response
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return self._create_fallback_response(message, str(e))
    
    async def process_message_async(self, message: Message,
                                    conversation: Optional[Conversation] = None) -> AIResponse:
        """Processar mensagem de forma assincrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.process_message(message, conversation)
        )
    
    def _extract_text_from_message(self, message: Message) -> str:
        """Extrair texto de uma mensagem"""
        if message.type.value == "text":
            if isinstance(message.content, str):
                return message.content
            elif isinstance(message.content, dict):
                return message.content.get('text', '')
        return ''
    
    def _get_context(self, conversation: Optional[Conversation]) -> Dict[str, Any]:
        """Obter contexto da conversa"""
        context = {}
        
        if conversation:
            context['conversation_id'] = conversation.id
            context['current_intent'] = conversation.current_intent
            context['filled_slots'] = conversation.filled_slots
            context['status'] = conversation.status.value
            context['message_count'] = conversation.message_count
        
        return context
    
    def _should_escalate(self, intent: Optional[IntentDetectionResult],
                       conversation: Optional[Conversation]) -> bool:
        """Determinar se deve escalar para humano"""
        # Verificar se e intencao de escalonamento
        if intent and intent.intent == lex_config.ESCALATION_INTENT:
            return True
        
        # Verificar se e fallback
        if intent and intent.intent == lex_config.FALLBACK_INTENT:
            # Verificar numero de tentativas de fallback
            if conversation:
                fallback_count = sum(
                    1 for msg in conversation.messages 
                    if msg.metadata.intent == lex_config.FALLBACK_INTENT
                )
                return fallback_count >= lex_config.FALLBACK_MAX_ATTEMPTS
            return True
        
        # Verificar confianca baixa
        if intent and intent.confidence < lex_config.NLP_CONFIDENCE_THRESHOLD:
            return True
        
        return False
    
    def _generate_response(self, message: Message, intent: Optional[IntentDetectionResult],
                           slots: List[SlotExtractionResult], entities: Dict[str, Any],
                           sentiment: Optional[str], sentiment_score: Optional[float],
                           knowledge_result: Optional[Any],
                           conversation: Optional[Conversation]) -> Response:
        """Gerar resposta"""
        
        # Tentar usar base de conhecimento
        if knowledge_result and knowledge_result.items:
            # Usar a melhor resposta da base de conhecimento
            best_item = knowledge_result.items[0]
            return Response(
                id=f"response-{message.id}",
                request_id=message.id,
                conversation_id=message.conversation_id,
                message_id=message.id,
                type="text",
                content=best_item.content,
                intent=intent.intent if intent else None,
                slots={s.slot: s.value for s in slots} if slots else {},
                status="completed",
                confidence=knowledge_result.items[0].metadata.get('confidence', 1.0),
                metadata={
                    'source': 'knowledge_base',
                    'knowledge_item_id': best_item.id
                }
            )
        
        # Tentar usar Bedrock para gerar resposta
        if bedrock_config.ENABLE_BEDROCK and intent:
            try:
                # Gerar resposta com Bedrock
                bedrock_response = bedrock_service.generate_response(
                    prompt=self._format_prompt(message, intent, slots, conversation),
                    session_id=message.session_id,
                    context=self._get_context(conversation),
                    history=self._get_history(conversation)
                )
                
                return Response(
                    id=f"response-{message.id}",
                    request_id=message.id,
                    conversation_id=message.conversation_id,
                    message_id=message.id,
                    type="text",
                    content=bedrock_response.text,
                    intent=intent.intent if intent else None,
                    slots={s.slot: s.value for s in slots} if slots else {},
                    status="completed",
                    confidence=bedrock_response.metadata.get('confidence', 0.9),
                    generation_time=bedrock_response.latency,
                    metadata={
                        'source': 'bedrock',
                        'model_id': bedrock_response.model_id,
                        'input_tokens': bedrock_response.input_tokens,
                        'output_tokens': bedrock_response.output_tokens
                    }
                )
            except Exception as e:
                logger.warning(f"Falha ao gerar resposta com Bedrock: {e}")
        
        # Usar resposta padrao da intencao
        if intent:
            intent_obj = intent_service.get_intent(intent.intent)
            if intent_obj and intent_obj.responses:
                return Response(
                    id=f"response-{message.id}",
                    request_id=message.id,
                    conversation_id=message.conversation_id,
                    message_id=message.id,
                    type="text",
                    content=intent_obj.responses[0],
                    intent=intent.intent,
                    slots={s.slot: s.value for s in slots} if slots else {},
                    status="completed",
                    confidence=intent.confidence,
                    metadata={
                        'source': 'intent_response',
                        'intent_name': intent.intent
                    }
                )
        
        # Resposta de fallback
        return Response(
            id=f"response-{message.id}",
            request_id=message.id,
            conversation_id=message.conversation_id,
            message_id=message.id,
            type="text",
            content=lex_config.FALLBACK_RESPONSE,
            intent=lex_config.FALLBACK_INTENT,
            slots={},
            status="completed",
            confidence=0.0,
            metadata={
                'source': 'fallback'
            }
        )
    
    def _format_prompt(self, message: Message, intent: IntentDetectionResult,
                      slots: List[SlotExtractionResult],
                      conversation: Optional[Conversation]) -> str:
        """Formatar prompt para Bedrock"""
        
        # Contexto da conversa
        context_parts = []
        
        if conversation:
            context_parts.append(f"Conversa ID: {conversation.id}")
            context_parts.append(f"Status: {conversation.status.value}")
            if conversation.current_intent:
                context_parts.append(f"Intencao atual: {conversation.current_intent}")
        
        # Slots preenchidos
        if slots:
            slot_text = ", ".join([f"{s.slot}={s.value}" for s in slots])
            context_parts.append(f"Slots preenchidos: {slot_text}")
        
        # Historico
        history_text = ""
        if conversation and conversation.messages:
            last_messages = conversation.messages[-3:]  # Ultimas 3 mensagens
            for msg in last_messages:
                if msg.direction.value == "incoming":
                    history_text += f"Usuario: {msg.content}\n"
                else:
                    history_text += f"Assistente: {msg.content}\n"
        
        # Prompt final
        prompt = f"""
        Voce e um assistente de autoatendimento do CORETHREE3.
        
        Contexto:
        {chr(10).join(context_parts)}
        
        Historico:
        {history_text}
        
        Usuario: {message.content}
        
        Intencao detectada: {intent.intent if intent else 'Desconhecida'}
        
        Responda de forma clara, objetiva e em portugues do Brasil.
        Se nao souber a resposta, diga que nao sabe.
        """
        
        return prompt
    
    def _get_history(self, conversation: Optional[Conversation]) -> List[Dict[str, str]]:
        """Obter historico da conversa"""
        if not conversation or not conversation.messages:
            return []
        
        history = []
        for msg in conversation.messages[-bedrock_config.CONTEXT_WINDOW:]:
            if msg.direction.value == "incoming":
                history.append({"role": "user", "content": str(msg.content)})
            else:
                history.append({"role": "assistant", "content": str(msg.content)})
        
        return history
    
    def _determine_actions(self, intent: Optional[IntentDetectionResult],
                          slots: List[SlotExtractionResult],
                          conversation: Optional[Conversation]) -> List[Dict[str, Any]]:
        """Determinar acoes a serem executadas"""
        actions = []
        
        if not intent:
            return actions
        
        # Verificar se precisa de fulfillment
        intent_obj = intent_service.get_intent(intent.intent)
        if intent_obj and intent_obj.fulfillment:
            actions.append({
                'type': 'fulfillment',
                'intent': intent.intent,
                'function': intent_obj.fulfillment,
                'slots': {s.slot: s.value for s in slots} if slots else {}
            })
        
        # Verificar se precisa salvar informacoes
        if intent.intent in ['AgendarServico', 'CancelarPedido']:
            actions.append({
                'type': 'save_to_database',
                'intent': intent.intent,
                'data': {s.slot: s.value for s in slots} if slots else {}
            })
        
        # Verificar se precisa notificar
        if intent.intent == 'FalarComHumano':
            actions.append({
                'type': 'notify_human',
                'intent': intent.intent,
                'message': 'Cliente solicitou falar com um humano'
            })
        
        return actions
    
    def _create_fallback_response(self, message: Message, error: str) -> AIResponse:
        """Criar resposta de fallback"""
        return AIResponse(
            response=Response(
                id=f"response-{message.id}",
                request_id=message.id,
                conversation_id=message.conversation_id,
                message_id=message.id,
                type="text",
                content=lex_config.FALLBACK_RESPONSE or f"Desculpe, ocorreu um erro: {error}",
                intent=lex_config.FALLBACK_INTENT,
                slots={},
                status="completed",
                confidence=0.0,
                metadata={
                    'source': 'fallback',
                    'error': error
                }
            ),
            intent=IntentDetectionResult(
                intent=lex_config.FALLBACK_INTENT,
                intent_id=lex_config.FALLBACK_INTENT,
                confidence=0.0,
                slots={},
                alternatives=[]
            ),
            slots=[],
            entities={},
            sentiment=None,
            sentiment_score=None,
            knowledge_used=None,
            actions=[],
            confidence=0.0,
            is_fallback=True,
            should_escalate=True
        )
    
    @retry(max_attempts=3, delay=0.5)
    def generate_quick_replies(self, intent: str, 
                             conversation: Optional[Conversation] = None) -> List[Dict[str, Any]]:
        """
        Gerar opcoes de resposta rapida
        
        Args:
            intent: Intencao atual
            conversation: Conversa associada
            
        Returns:
            List[Dict[str, Any]]: Lista de opcoes
        """
        # Opcoes padrao
        default_options = [
            {"text": "Status de Pedido", "value": "StatusPedido"},
            {"text": "Agendar Servico", "value": "AgendarServico"},
            {"text": "Cancelar Pedido", "value": "CancelarPedido"},
            {"text": "Falar com Humano", "value": "FalarComHumano"}
        ]
        
        # Opcoes baseadas na intencao
        intent_options = {
            "StatusPedido": [
                {"text": "Sim, quero verificar", "value": "StatusPedido_confirm"},
                {"text": "Nao, outra coisa", "value": "Ajuda"}
            ],
            "AgendarServico": [
                {"text": "Manutencao", "value": "manutencao"},
                {"text": "Suporte", "value": "suporte"},
                {"text": "Consulta", "value": "consulta"}
            ]
        }
        
        return intent_options.get(intent, default_options)
    
    @retry(max_attempts=3, delay=0.5)
    def suggest_follow_up(self, conversation: Conversation) -> Optional[str]:
        """
        Sugerir follow-up para a conversa
        
        Args:
            conversation: Conversa
            
        Returns:
            Optional[str]: Sugestao de follow-up
        """
        # Verificar intencao atual
        if not conversation.current_intent:
            return None
        
        # Sugestoes baseadas na intencao
        follow_ups = {
            "StatusPedido": "Voce gostaria de agendar uma manutencao preventiva?",
            "AgendarServico": "Voce gostaria de confirmar o agendamento?",
            "PesquisaSatisfacao": "Obrigado pelo feedback! Posso te ajudar com mais alguma coisa?"
        }
        
        return follow_ups.get(conversation.current_intent)
    
    @retry(max_attempts=3, delay=0.5)
    def analyze_conversation(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analisar conversa completa
        
        Args:
            conversation: Conversa a ser analisada
            
        Returns:
            Dict[str, Any]: Analise da conversa
        """
        analysis = {
            'conversation_id': conversation.id,
            'message_count': conversation.message_count,
            'intent_distribution': {},
            'slot_distribution': {},
            'sentiment_trend': [],
            'average_response_time': 0.0,
            'resolution_time': conversation.resolution_time,
            'satisfaction_score': conversation.satisfaction_score
        }
        
        # Analisar distribuicao de intencoes
        for msg in conversation.messages:
            if msg.metadata.intent:
                intent = msg.metadata.intent
                analysis['intent_distribution'][intent] = analysis['intent_distribution'].get(intent, 0) + 1
            
            # Analisar slots
            for slot_name in msg.metadata.response_slots:
                analysis['slot_distribution'][slot_name] = analysis['slot_distribution'].get(slot_name, 0) + 1
            
            # Analisar sentimento
            if msg.metadata.sentiment:
                analysis['sentiment_trend'].append({
                    'message_id': msg.id,
                    'sentiment': msg.metadata.sentiment,
                    'score': msg.metadata.sentiment_score
                })
        
        # Calcular tempo medio de resposta
        if conversation.messages:
            total_time = 0
            response_count = 0
            for i in range(1, len(conversation.messages)):
                prev_msg = conversation.messages[i-1]
                curr_msg = conversation.messages[i]
                if prev_msg.direction.value == "incoming" and curr_msg.direction.value == "outgoing":
                    if prev_msg.sent_at and curr_msg.sent_at:
                        time_diff = (curr_msg.sent_at - prev_msg.sent_at).total_seconds()
                        total_time += time_diff
                        response_count += 1
            
            if response_count > 0:
                analysis['average_response_time'] = total_time / response_count
        
        return analysis


# Instancia do servico
ai_service = AIService()
