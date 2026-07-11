"""
Caso de uso: responder una pregunta usando RAG.

Coordina los TRES puertos (embeddings, vector store, LLM) sin saber
nada de Ollama, pgvector, ni ninguna tecnologia concreta. Solo conoce
los contratos.
"""

from domain.ports.embedding_provider import EmbeddingProviderPort
from domain.ports.llm_provider import LLMProviderPort
from domain.ports.vector_store import VectorStorePort

SYSTEM_PROMPT = (
    "Eres un asistente de threat hunting. Responde SOLO con base en el "
    "contexto proporcionado. Si el contexto no tiene la respuesta, dilo "
    "claramente en vez de inventar. SIEMPRE cita el id del chunk del que "
    "sacaste cada afirmacion, usando el formato [id]."
)

def answer_question(
    question: str,
    embedder: EmbeddingProviderPort,
    vector_store: VectorStorePort,
    llm: LLMProviderPort,
    top_k: int = 3,
) -> dict:
    query_vector = embedder.embed(question)
    results = vector_store.search(query_embedding=query_vector, top_k=top_k)
    
    context = "\n".join(
        f"[{r.chunk.id}] {r.chunk.content}" for r in results
    )
    
    prompt = (
        f"Contexto:\n{context}\n\n"
        f"Pregunta: {question}\n\n"
        f"Respuesta (cita los ids entre corchetes):"
    )
    
    answer_text = llm.generate_text(prompt=prompt, system=SYSTEM_PROMPT)
    
    return {
        "question": question,
            "answer": answer_text,
        "sources": [r.chunk.id for r in results],
    }

