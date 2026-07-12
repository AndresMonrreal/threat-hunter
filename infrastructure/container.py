"""
Tablero electrico: decide que adaptador conectar a cada puerto,
segun la configuracion (.env). Este es el UNICO lugar del proyecto
que conoce TODAS las implementaciones concretas a la vez.

Cualquier script o futuro caso de uso pide sus dependencias aqui,
en vez de construir adaptadores por su cuenta.
"""

from adapters.embeddings.nomic_adapter import OllamaEmbeddingAdapter
from adapters.llm.ollama_adapter import OllamaAdapter
from adapters.vector_store.pgvector_adapter import PgVectorAdapter
from domain.ports.embedding_provider import EmbeddingProviderPort
from domain.ports.llm_provider import LLMProviderPort
from domain.ports.vector_store import VectorStorePort
from infrastructure.config import Settings, load_settings


class Container:
    """
    Agrupa las tres dependencias principales, ya construidas segun
    la configuracion actual (local con Ollama, o en el futuro AWS).
    """
    def __init__(self,settings:Settings):
        self.settings = settings
        self.embedder = EmbeddingProviderPort = self._build_embedder()
        self.llm: LLMProviderPort = self._build_llm()
        self.vector_store: VectorStorePort = self._build_vector_store()
        
    def _build_embedder(self) -> EmbeddingProviderPort:
        if self.settings.llm_provider == "ollama":
            return OllamaEmbeddingAdapter(model=self.settings.embedding_model)
        raise ValueError(f"Unknown LLM provider: {self.settings.llm_provider}")
    
    def _build_llm(self) -> LLMProviderPort:
        if self.settings.llm_provider == "ollama":
            return OllamaAdapter(model_name=self.settings.llm_model)
        raise ValueError(f"Unknown LLM provider: {self.settings.llm_provider}")
    
    def _build_vector_store(self) -> VectorStorePort:
        return PgVectorAdapter(self.settings.postgres_conninfo)
    
def build_container() -> Container:
    """
    Punto de entrada: arma el container leyendo el .env
    """
    settings = load_settings()
    return Container(settings) 