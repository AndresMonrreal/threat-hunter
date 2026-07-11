"""
Prueba de humo del RAG COMPLETO: pregunta -> busqueda semantica ->
respuesta generada citando fuentes.
"""

from adapters.embeddings.nomic_adapter import OllamaEmbeddingAdapter
from adapters.llm.ollama_adapter import OllamaAdapter
from adapters.vector_store.pgvector_adapter import PgVectorAdapter
from application.rag.answer_question import answer_question
from domain.entities.chunk import Chunk
from infrastructure.config import load_settings


settings = load_settings()
store = PgVectorAdapter(settings.postgres_conninfo)
embedder = OllamaEmbeddingAdapter(model=settings.embedding_model)
llm = OllamaAdapter(model_name=settings.llm_model) 

textos = [
    ("t1059-001", "PowerShell permite a un atacante ejecutar comandos y scripts maliciosos en Windows.", {"tactic": "execution"}),
    ("t1055", "Process Injection consiste en insertar codigo malicioso dentro de un proceso legitimo para evadir defensas.", {"tactic": "defense-evasion"}),
    ("t1071-001", "Los atacantes usan protocolos web comunes como HTTP para camuflar su comunicacion de comando y control.", {"tactic": "command-and-control"}),
]

print("1) Ingiriendo conocimiento de prueba...")
chunks = [Chunk(id=cid, content=content, metadata=meta) for cid, content, meta in textos]
embeddings = [embedder.embed(content) for _, content, _ in textos]
store.add_chunk(chunks, embeddings)
print("   OK")

pregunta = "¿que tecnica usa un atacante para esconder codigo dentro de otro proceso?"
print(f"\n2) Preguntando: '{pregunta}'")
resultado = answer_question(
    question=pregunta,
    embedder=embedder,
    vector_store=store,
    llm=llm,
)

print(f"\n3) Respuesta del sistema:\n{resultado['answer']}")
print(f"\n4) Fuentes usadas: {resultado['sources']}")

print("\n5) Limpiando...")
store.delete_chunks([c.id for c in chunks])
print("   OK")

print("\nRAG completo funcionando: retrieval + generacion con citas.")
