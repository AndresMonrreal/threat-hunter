"""
Punto UNICO donde se lee el .env y se arma la configuracion.
Nada mas en el proyecto deberia leer variables de entorno directamente:
todo pasa por aqui.
"""

import os 
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: str
    postgres_host: str
    llm_model: str
    llm_provider: str
    embedding_model: str

    @property
    def postgres_conninfo(self) -> str:
        return (
            f"host={self.postgres_host} "
            f"port={self.postgres_port} "
            f"dbname={self.postgres_db} "
            f"user={self.postgres_user} "
            f"password={self.postgres_password}"
        )

def load_settings() -> Settings:
    return Settings(
        postgres_user=os.environ["POSTGRES_USER"],
        postgres_password=os.environ["POSTGRES_PASSWORD"],
        postgres_db=os.environ["POSTGRES_DB"],
        postgres_host=os.environ.get("POSTGRES_HOST", "localhost"),
        postgres_port=os.environ.get("POSTGRES_PORT", "5432"),
        llm_provider=os.environ.get("LLM_PROVIDER", "ollama"),
        llm_model=os.environ.get("LLM_MODEL", "qwen3:8b"),
        embedding_model=os.environ.get("EMBEDDING_MODEL", "nomic-embed-text"),
    )