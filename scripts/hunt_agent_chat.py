from infrastructure.container import build_container
from application.agent.graph import build_agent_graph

print("Cargando agente (puede tardar por el modelo en CPU)...")
container = build_container()
agente = build_agent_graph(container)

historial = []

print("\nListo. Escribe tu pregunta (o 'salir' para terminar).\n")

while True:
    pregunta = input("Tu: ").strip()

    if pregunta.lower() in  ("salir", "exit", "quit"):
        break
    if not pregunta:
        continue

    len_antes = len(historial)
    historial.append(("human", pregunta))
    resultado = agente.invoke({"messages": historial})
    historial = resultado["messages"]

    # muestra que herramienta(s) uso el agente en este turno, antes de la respuesta final
    for m in historial[len_antes + 1:-1]:
        if getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                print(f"  [tool] {tc['name']}({tc['args']})")

    respuesta = historial[-1]
    print(f"\nAgente: {respuesta.content}\n")

    