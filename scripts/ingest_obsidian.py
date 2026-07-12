"""
Ingiere toda tu boveda de Obsidian (clonada como repo Git) al RAG.
"""

from application.rag.loaders.obsidian_loader import load_obsidian_notes
from infrastructure.container import build_container

VAULT_PATH = "/home/andres/obsidian-notes"

container = build_container()

print(f"1) Leyendo notas desde: {VAULT_PATH}")
chunks = load_obsidian_notes(VAULT_PATH)
print(f"   {len(chunks)} chunks generados de tus notas.")

print("\n2) Generando embeddings e insertando en pgvector...")
for i,chunk in enumerate(chunks,1):
    embedding = container.embedder.embed(chunk.content)
    container.vector_store.add_chunk([chunk],[embedding])
    print(f"   [{i}/{len(chunks)}] {chunk.metadata['note_path']}")
    
print("\nIngesta de Obsidian completa")

