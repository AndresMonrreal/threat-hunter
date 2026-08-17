from adapters.embeddings.nomic_adapter import OllamaEmbeddingAdapter
from adapters.llm.ollama_adapter import OllamaAdapter
from adapters.vector_store.pgvector_adapter import PgVectorAdapter
from adapters.log_engine.postgres_adapter import PostgresLogEngineAdapter
from domain.ports.embedding_provider import EmbeddingProviderPort
from domain.ports.llm_provider import LLMProviderPort
from domain.ports.vector_store import VectorStorePort
from domain.ports.log_query_engine import LogQueryEnginePort
from infrastructure.config import Settings, load_settings


class Container:
    """
    Agrupa las dependencias principales, ya construidas segun
    la configuracion actual (local con Ollama, o en el futuro AWS).
    """
    #En el __init__ recibimos un objeto Settings que contiene la configuracion de la aplicacion.
    #Este objeto se crea leyendo el .env y se pasa al container para que pueda construir los adaptadores correctos segun la configuracion
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embedder: EmbeddingProviderPort = self._build_embedder()
        self.llm: LLMProviderPort = self._build_llm()
        self.vector_store: VectorStorePort = self._build_vector_store()
        self.log_engine: LogQueryEnginePort = self._build_log_engine()

    def _build_embedder(self) -> EmbeddingProviderPort:
        #hoy solo hay adaptador de Ollama; otros providers lanzan error hasta que se implementen
        if self.settings.llm_provider == "ollama":
            return OllamaEmbeddingAdapter(model=self.settings.embedding_model)
        raise ValueError(f"Unknown LLM provider: {self.settings.llm_provider}")

    def _build_llm(self) -> LLMProviderPort:
        if self.settings.llm_provider == "ollama":
            return OllamaAdapter(model_name=self.settings.llm_model)
        raise ValueError(f"Unknown LLM provider: {self.settings.llm_provider}")

    def _build_vector_store(self) -> VectorStorePort:
        return PgVectorAdapter(self.settings.postgres_conninfo)

    def _build_log_engine(self) -> LogQueryEnginePort:
        return PostgresLogEngineAdapter(self.settings.postgres_conninfo)


def build_container() -> Container:
    """
    Punto de entrada: arma el container leyendo el .env
    """
    settings = load_settings()
    return Container(settings)