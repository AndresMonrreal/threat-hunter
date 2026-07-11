"""
Puerto: EmbeddingProviderPort

Define el CONTRATO para convertir texto en vectores, sin decir con que
modelo. Hoy lo implementa nomic-embed-text via Ollama; manana podria
ser Titan de AWS Bedrock.
"""

from abc import ABC, abstractmethod

class EmbeddingProviderPort(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Convierte UN texto en su vector."""
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Convierte VARIOS textos de una vez.

        No es solo comodidad: muchos proveedores (Ollama incluido)
        procesan lotes mas eficientemente que uno por uno. Al ingerir
        cientos de chunks de ATT&CK, la diferencia de velocidad es real.
        """
        raise NotImplementedError
            
