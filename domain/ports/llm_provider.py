"""
Puerto: LLMProviderPort

Define el CONTRATO para generar texto a partir de un prompt, sin decir
que modelo lo hace. Hoy lo implementa Qwen3 via Ollama; manana podria
ser Bedrock en AWS.
"""

from abc import ABC, abstractmethod

class LLMProviderPort(ABC):
    
    @abstractmethod
    def generate_text(self, prompt: str, system: str | None = None) -> str:
        """
        Genera texto a partir de un prompt.

        system: instrucciones de comportamiento separadas del prompt
        del usuario (ej. "responde solo citando las fuentes dadas").
        Se separan porque conceptualmente son cosas distintas: una es
        el ROL del modelo, la otra es la PREGUNTA concreta.
        """
        raise NotImplementedError
