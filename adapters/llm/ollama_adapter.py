"""
Adaptador de LLMProviderPort usando Ollama.

Este es el UNICO archivo del proyecto que sabe que existe Ollama
o el modelo Qwen3. Todo lo demas solo conoce LLMProviderPort.
"""

import requests
from domain.ports.llm_provider import LLMProviderPort

class OllamaAdapter(LLMProviderPort):
    def __init__(self, model_name: str, ollama_url: str = "http://localhost:11434"):
        self._model=model_name
        self._ollama_url=ollama_url
        
    def generate_text(self, prompt: str, system: str | None = None) -> str:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
            
        response = requests.post(
            f"{self._ollama_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"]
    