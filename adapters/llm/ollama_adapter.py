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
            "stream": False,  # False = espera la respuesta completa en vez de recibirla en pedazos
        }
        if system:
            # agrega el mensaje de sistema al payload si se proporcionó
            payload["system"] = system

        response = requests.post(
            f"{self._ollama_url}/api/generate",
            json=payload,
            timeout=120,
        )
        # lanza excepcion si Ollama respondio con codigo de error (4xx/5xx)
        response.raise_for_status()
        return response.json()["response"]
    