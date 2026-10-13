"""
CORETHREE3 - Autoatendimento Inteligente
Modelo de Base de Conhecimento (Knowledge)
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class KnowledgeCategory(str, Enum):
    """Categorias de conhecimento"""
    FAQ = "faq"
    PRODUCT = "product"
    SERVICE = "service"
    POLICY = "policy"
    PROCEDURE = "procedure"
    TROUBLESHOOTING = "troubleshooting"
    GENERAL = "general"


class KnowledgeItemStatus(str, Enum):
    """Status do item de conhecimento"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class KnowledgeItem(BaseModel):
    """Modelo de item de conhecimento"""
    
    # Identificacao
    id: str = Field(..., description="ID unico do item")
    
    # Titulo
    title: str = Field(..., description="Titulo do item")
    
    # Conteudo
    content: str = Field(..., description="Conteudo do item")
    
    # Categoria
    category: KnowledgeCategory = Field(KnowledgeCategory.GENERAL, description="Categoria do item")
    
    # Palavras-chave
    keywords: List[str] = Field(default_factory=list, description="Palavras-chave")
    
    # Sinonimos
    synonyms: List[str] = Field(default_factory=list, description="Sinonimos")
    
    # Status
    status: KnowledgeItemStatus = Field(KnowledgeItemStatus.DRAFT, description="Status do item")
    
    # Prioridade
    priority: int = Field(0, description="Prioridade (0-10)")
    
    # Autor
    author_id: Optional[str] = Field(None, description="ID do autor")
    author_name: Optional[str] = Field(None, description="Nome do autor")
    
    # Revisor
    reviewer_id: Optional[str] = Field(None, description="ID do revisor")
    reviewer_name: Optional[str] = Field(None, description="Nome do revisor")
    
    # Versao
    version: int = Field(1, description="Versao do item")
    
    # Relacionamentos
    related_items: List[str] = Field(default_factory=list, description="Itens relacionados")
    
    # Tags
    tags: List[str] = Field(default_factory=list, description="Tags")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Controle
    is_active: bool = Field(True, description="Item ativo")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualizacao")
    published_at: Optional[datetime] = Field(None, description="Data de publicacao")
    archived_at: Optional[datetime] = Field(None, description="Data de arquivamento")
    
    # Estaticas
    view_count: int = Field(0, description="Numero de visualizacoes")
    use_count: int = Field(0, description="Numero de usos")
    helpful_count: int = Field(0, description="Numero de avaliacoes uteis")
    not_helpful_count: int = Field(0, description="Numero de avaliacoes nao uteis")
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validar prioridade"""
        if not 0 <= v <= 10:
            raise ValueError("Prioridade deve estar entre 0 e 10")
        return v
    
    @validator('view_count', 'use_count', 'helpful_count', 'not_helpful_count')
    def validate_counts(cls, v):
        """Validar contadores"""
        if v < 0:
            raise ValueError("Contador nao pode ser negativo")
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "knowledge-1",
                    "title": "Como consultar o status de um pedido?",
                    "content": "Para consultar o status de um pedido, basta informar o numero do pedido. O sistema ira verificar automaticamente e retornar o status atual.",
                    "category": "faq",
                    "keywords": ["status", "pedido", "consultar", "onde esta"],
                    "synonyms": ["rastrear", "acompanhar", "situacao"],
                    "status": "approved",
                    "priority": 10,
                    "author_id": "user-1",
                    "tags": ["pedidos", "status", "cliente"]
                }
            ]
        }
    
    def increment_view_count(self) -> None:
        """Incrementar contador de visualizacoes"""
        self.view_count += 1
        self.updated_at = datetime.utcnow()
    
    def increment_use_count(self) -> None:
        """Incrementar contador de usos"""
        self.use_count += 1
        self.updated_at = datetime.utcnow()
    
    def increment_helpful_count(self) -> None:
        """Incrementar contador de avaliacoes uteis"""
        self.helpful_count += 1
        self.updated_at = datetime.utcnow()
    
    def increment_not_helpful_count(self) -> None:
        """Incrementar contador de avaliacoes nao uteis"""
        self.not_helpful_count += 1
        self.updated_at = datetime.utcnow()
    
    def get_helpfulness_score(self) -> float:
        """Calcular score de utilidade"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return self.helpful_count / total


class KnowledgeSearchResult(BaseModel):
    """Resultado de busca na base de conhecimento"""
    
    # Itens encontrados
    items: List[KnowledgeItem] = Field(default_factory=list, description="Itens encontrados")
    
    # Total de itens
    total: int = Field(0, description="Total de itens encontrados")
    
    # Paginacao
    page: int = Field(1, description="Pagina atual")
    page_size: int = Field(20, description="Tamanho da pagina")
    total_pages: int = Field(0, description="Total de paginas")
    
    # Metricas de busca
    search_time: Optional[float] = Field(None, description="Tempo de busca (ms)")
    
    # Sugestoes
    suggestions: List[str] = Field(default_factory=list, description="Sugestoes de busca")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")


class KnowledgeEmbedding(BaseModel):
    """Embedding de item de conhecimento"""
    
    # ID do item
    item_id: str = Field(..., description="ID do item de conhecimento")
    
    # Embedding
    embedding: List[float] = Field(..., description="Vetor de embedding")
    
    # Dimensao
    dimension: int = Field(..., description="Dimensao do embedding")
    
    # Modelo
    model_id: str = Field(..., description="ID do modelo de embedding")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Controle
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criacao")
    
    @validator('embedding')
    def validate_embedding(cls, v, values):
        """Validar embedding"""
        if len(v) != values.get('dimension', 0):
            raise ValueError(f"Embedding deve ter {values.get('dimension')} dimensoes")
        return v


class KnowledgeSearchConfig(BaseModel):
    """Configuracoes de busca na base de conhecimento"""
    
    # Filtros
    category: Optional[KnowledgeCategory] = Field(None, description="Filtro por categoria")
    tags: List[str] = Field(default_factory=list, description="Filtro por tags")
    keywords: List[str] = Field(default_factory=list, description="Filtro por palavras-chave")
    
    # Ordenacao
    sort_by: str = Field("priority", description="Campo para ordenacao")
    sort_order: str = Field("desc", description="Ordem de ordenacao (asc, desc)")
    
    # Paginacao
    page: int = Field(1, description="Pagina")
    page_size: int = Field(20, description="Tamanho da pagina")
    
    # Busca semantica
    semantic_search: bool = Field(True, description="Busca semantica")
    similarity_threshold: float = Field(0.7, description="Limiar de similaridade")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    @validator('page', 'page_size')
    def validate_pagination(cls, v):
        """Validar paginacao"""
        if v < 1:
            raise ValueError("Pagina e tamanho da pagina devem ser maiores que 0")
        return v
    
    @validator('similarity_threshold')
    def validate_threshold(cls, v):
        """Validar limiar de similaridade"""
        if not 0 <= v <= 1:
            raise ValueError("Limiar de similaridade deve estar entre 0 e 1")
        return v
