"""
Prueba de humo para PgVectorAdapter.
Usa vectores FALSOS (aleatorios) a proposito: aqui solo verificamos
que el adaptador habla bien con Postgres, no la calidad semantica
(eso vendra cuando conectemos embeddings reales de Ollama).
"""

import random 
from adapters.vector_store.pgvector_adapter import PgVectorAdapter
from domain.entities.vector.chunk import Chunk
from infrastructure.config import load_config

settings = load_config()
CONNINFO = settings.postgres_conninfo

def fake_vector(seed: int) -> list[float]:
    random.seed(seed)
    return [random.random() for _ in range(768)]

store = PgVectorAdapter(CONNINFO)

chunks = [
    Chunk(
        id="test-1",
        content="T1059.001 - PowerShell es una tecnica de ejecucion",
        metadata={"tactic": "execution", "platform": "Windows"},
    ),
    Chunk(
        id="test-2",
        content="T1055 - Process Injection es una tecnica de evasion",
        metadata={"tactic": "defense-evasion", "platform": "Windows"},
    ),
]

embeddings = [fake_vector(1) , fake_vector(2)]

print("Insertando chunks de prueba en PgVectorAdapter...")
store.add_chunk(chunks, embeddings)
print("Chunks insertados correctamente.")

print("\n2) Buscando sin filtro...")
results = store.search(query_embedding=fake_vector(1), top_k=5)
for r in results:
    print(f"   id={r.chunk.id}  score={r.score:.4f}  content={r.chunk.content[:40]}")
assert len(results) == 2, "Deberian aparecer los 2 chunks insertados"

print("\n3) Buscando CON filtro (tactic=defense-evasion)...")
results = store.search(query_embedding=fake_vector(1), top_k=5, filters={"tactic": "defense-evasion"})
for r in results:
     print(f"   id={r.chunk.id}  score={r.score:.4f}")
assert len(results) == 1 and results[0].chunk.id == "test-2", "El filtro deberia dejar solo test-2"

print("\n4) Borrando chunks de prueba...")
store.delete_chunks(["test-1", "test-2"])
print("   OK")

print("\n5) Confirmando que ya no existen...")
results = store.search(query_embedding=fake_vector(1), top_k=5)
assert len(results) == 0, "No deberia quedar nada tras borrar"
print("   OK, 0 resultados")

print("\n TODO PASO. El adaptador funciona correctamente.")
