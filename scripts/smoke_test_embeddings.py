"""
Prueba de humo END-TO-END: texto real -> embedding real -> pgvector -> busqueda semantica real.

Aqui es donde por fin ves el RAG funcionando de verdad: insertamos
texto sobre tecnicas de ATT&CK y buscamos por SIGNIFICADO, no por
coincidencia de palabras exactas.
"""

from adapters.embeddings.nomic_adapter import OllamaEmbeddingAdapter
from adapters.vector_store.pgvector_adapter import PgVectorAdapter
from domain.entities.chunk import Chunk
from infrastructure.config import load_settings

settings = load_settings()
store = PgVectorAdapter(settings.postgres_conninfo)
embedder = OllamaEmbeddingAdapter(model=settings.embedding_model)

textos = [
    ("t1059-001", "PowerShell permite a un atacante ejecutar comandos y scripts maliciosos en Windows.", {"tactic": "execution"}),
    ("t1055", "Process Injection consiste en insertar codigo malicioso dentro de un proceso legitimo para evadir defensas.", {"tactic": "defense-evasion"}),
    ("t1071-001", "Los atacantes usan protocolos web comunes como HTTP para camuflar su comunicacion de comando y control.", {"tactic": "command-and-control"}),
]

print("1) Generando embeddings reales con nomic-embed-text...")
chunks = []
embeddings = []

for chunk_id, content, meta in textos:
    chunks.append(Chunk(id=chunk_id,content=content,metadata=meta))
    embeddings.append(embedder.embed(content))
print(f"   OK, {len(embeddings)} vectores generados, dimension={len(embeddings[0])}")

print("\n2) Guardando en pgvector...")
store.add_chunk(chunks, embeddings)
print("   OK")


pregunta = "¿como se puede correr codigo malicioso escondido dentro de otro proceso?"
print(f"\n3) Buscando por SIGNIFICADO: '{pregunta}'")
query_vector = embedder.embed(pregunta)
results = store.search(query_embedding=query_vector,top_k=3)

for r in results:
    print(f"   score={r.score:.4f}  id={r.chunk.id}  -> {r.chunk.content[:60]}...")
    mejor = results[0]
    
print(f"\n4) Verificando que el MEJOR resultado sea el correcto (t1055, Process Injection)...")
assert mejor.chunk.id == "t1055", f"Se esperaba t1055, salio {mejor.chunk.id}"
print("   CORRECTO: encontro el chunk correcto por significado, no por palabras exactas.")


print("\n5) Limpiando...")
store.delete_chunks([c.id for c in chunks])
print("   OK")

print("\n  RAG semantico funcionando de punta a punta.")
