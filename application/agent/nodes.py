from langchain_core.messages import ToolMessage

SYSTEM_PROMPT = (
    "Eres un asistente de threat hunting. Tienes acceso a herramientas "
    "para buscar en las notas del usuario, correlacionar indicadores de "
    "compromiso (IPs, dominios, hashes), y consultar detecciones "
    "guardadas (ej. alertas de fuerza bruta). "
    "SIEMPRE que el usuario mencione una IP, dominio o hash, usa "
    "correlacionar_ioc para verificar si ya se ha visto antes, en vez "
    "de responder de memoria. Usa buscar_notas para preguntas "
    "conceptuales. Usa consultar_detecciones para pedir alertas "
    "guardadas directamente."
)

def build_llm_model(llm_con_tools):
    def llamar_llm(state: dict) -> dict:
        mensajes = state["message"]
        if not mensajes or mensajes[0].type != "system":
            mensajes = [("system", SYSTEM_PROMPT)] + mensajes
        respuesta = llm_con_tools.invoke(mensajes)
        return {"messages": [respuesta]}
    return llamar_llm


def build_tools_node(tools_por_nombre: dict):
    def ejecutar_tools(state: dict) -> dict:
        ultimo_mensaje = state["messages"][-1]
        resultados = []
        for tool_call in ultimo_mensaje.tool_calls:
            tool_fn = tools_por_nombre[tool_call["name"]]
            resultado = tool_fn.invoke(tool_call["args"])
            resultados.append(
                ToolMessage(content=str(resultado), tool_call_id=tool_call["id"])
            )
            return {"messages": resultados}
        return ejecutar_tools