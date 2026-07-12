"""
Ingiere la base oficial de MITRE ATT&CK al RAG.
"""


from application.rag.loaders.attack_loader import load_attack_techniques
from infrastructure.container import build_container

JSON_PATH = "data/knowledge/attack/enterprise-attack.json"

container = build_container()

print(f"1) Leyendo tecnicas desde: {JSON_PATH}")
chunks = load_attack_techniques(JSON_PATH)
print(f"   {len(chunks)} tecnicas validas encontradas.")

print("\n2) Generando embeddings e insertando en pgvector...")
for i,chunk in enumerate(chunks):
    embedding = container.embedder.embed(chunk.content)
    container.vector_store.add_chunk([chunk], [embedding])
    if i % 25 == 0 or i == len(chunks):
        print(f"   [{i}/{len(chunks)}] {chunk.metadata['technique_id']} - {chunk.metadata['name']}")
print("\nIngesta de ATT&CK completa.")

