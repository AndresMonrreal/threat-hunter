from infrastructure.container import build_container
from application.agent.graph import build_agent_graph

container = build_container()
agente = build_agent_graph(container)

pregunta = "¿Has visto algo relacionado con la IP 185.220.101.45 antes? ¿Que sabes de eso?"
print(f"Pregunta: {pregunta}\n")

resultado = agente.invoke({"messages": [("human", pregunta)]})

print("=== Trace completo ===")
for m in resultado["messages"]:
    print(f"[{m.type}] {m.content[:200] if m.content else '(tool call)'}")

print(f"\n=== Respuesta final ===\n{resultado['messages'][-1].content}")