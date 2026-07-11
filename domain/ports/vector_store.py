"""
Puerto: VectorStorePort

Define el CONTRATO para cualquier almacén de vectores, sin decir cuál.
Hoy lo implementa pgvector; mañana podría ser OpenSearch en AWS.
El resto del sistema solo conoce esta interfaz, nunca la tecnología real.
"""

from abc import ABC, abstractmethod
from domain.entities.chunk import Chunk , SearchResult

class VectorStorePort(ABC):
    @abstractmethod
    def add_chunk(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """
        Guarda chunks junto con sus vectores ya calculados.

        Recibe los embeddings ya hechos (no el texto crudo) porque
        calcular embeddings es responsabilidad de OTRO puerto
        (EmbeddingProvider). Este puerto solo sabe guardar y buscar
        vectores, no generarlos.
        """

        raise NotImplementedError

    @abstractmethod
    def search(self, query_embedding: list[float],top_k:int = 5, filters: dict | None = None) -> list[SearchResult]:
        """
        Busca los chunks más similares a un vector de consulta.

        filters: permite acotar por metadata antes de comparar
        (ej. {"platform": "Windows", "tactic": "persistence"}).
        Esto es lo que evita que el RAG sea "ciego" — filtras
        primero, buscas después.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_chunks(self, chunk_ids: list[str]) -> None:
        """Elimina chunks por id — necesario para re-ingerir fuentes actualizadas."""
        raise NotImplementedError        