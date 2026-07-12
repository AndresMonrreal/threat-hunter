"""
Prueba de humo del RAG COMPLETO, usando el Container en vez de
construir adaptadores a mano.
"""


from application.rag.answer_question import answer_question
from infrastructure.container import build_container
from domain.entities.chunk import Chunk

container = build_container()

textos = [
    ("t1059-001", "PowerShell permite a un atacante ejecutar comandos y scripts maliciosos en Windows.", {"tactic": "execution"}),
    ("t1055", "Process Injection consiste en insertar codigo malicioso dentro de un proceso legitimo para evadir defensas.", {"tactic": "defense-evasion"}),
    ("t1071-001", "Los atacantes usan protocolos web comunes como HTTP para camuflar su comunicacion de comando y control.", {"tactic": "command-and-control"}),
]

print("1) Ingiriendo conocimiento de prueba...")
chunks = [Chunk(id=cid,content=content,metadata=meta) for cid,content,meta in textos]
embeddings = [container.embedder.embed(content) for _,content,_ in textos]
container.vector_store.add_chunk(chunks, embeddings)
print("   OK")

pregunta = "¿que tecnica usa un atacante para esconder codigo dentro de otro proceso?"
print(f"\n2) Preguntando: '{pregunta}'")
resultado = answer_question(question=pregunta,embedder=container.embedder,vector_store=container.vector_store,
                            llm=container.llm,)

print(f"\n3) Respuesta del sistema:\n{resultado['answer']}")
print(f"\n4) Fuentes usadas: {resultado['sources']}")

print("\n5) Limpiando...")
container.vector_store.delete_chunks([c.id for c in chunks])
print("   OK")

print("\n  RAG semantico funcionando de punta a punta, usando el Container.")
