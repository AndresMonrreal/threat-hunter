from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from infrastructure.container import build_container
from application.hunting.execute_hunt import correlacionar_ioc as _correlacionar_ioc

container = build_container()

@tool
def correlacionar_ioc(texto: str) -> dict:
    """Extrae IOCs (IPs, dominios, hashes) de un texto y busca coincidencias en notas y detecciones guardadas."""
    return _correlacionar_ioc(texto, container)

llm = ChatOllama(model="qwen3:8b", temperature=0)

print("    Prueba 1: sin tools, pregunta simple   ")
r1 = llm.invoke("Di solo la palabra: listo")
print(f"content: {r1.content!r}")

print("\n Prueba 2: con tools + system prompt explicito ")
llm_con_tools = llm.bind_tools([correlacionar_ioc])
mensajes = [
    ("system", "Tienes acceso a la herramienta correlacionar_ioc. Usala SIEMPRE que el usuario mencione una IP, dominio o hash, para verificar si ya se ha visto antes."),
    ("human", "¿Has visto algo relacionado con la IP 185.220.101.45 antes?"),
]
r2 = llm_con_tools.invoke(mensajes)
print(f"tool_calls: {r2.tool_calls}")
print(f"content: {r2.content!r}")
print(f"additional_kwargs: {r2.additional_kwargs}")
