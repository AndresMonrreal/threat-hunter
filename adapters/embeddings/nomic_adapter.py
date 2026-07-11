"""
Adaptador de EmbeddingProviderPort usando Ollama + nomic-embed-text.

Este es el UNICO archivo del proyecto que sabe que existe Ollama
o el modelo nomic-embed-text. Todo lo demas solo conoce EmbeddingProviderPort.
"""

import requests
from domain.ports.embedding_provider import EmbeddingProviderPort

class OllamaEmbeddingAdapter(EmbeddingProviderPort):
    def __init__(self, model:str, base_url:str = "http://localhost:11434"):
        self._model = model
        self._base_url = base_url

    def embed(self, text: str) -> list[float]:
        response = requests.post(
            f"{self._base_url}/api/embeddings",
            json={"model": self._model, "prompt": text},
            timeout=60,
        ) 
        response.raise_for_status()
        return response.json()["embedding"]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]