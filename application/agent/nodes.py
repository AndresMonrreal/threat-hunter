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

def build_llm_node(llm_con_tools):
    def llamar_llm(state: dict) -> dict:
        #State es un diccionario con la clave "messages" que contiene una lista de mensajes
        mensajes = state["messages"]
        #Si no hay mensajes o el primer mensaje no es de tipo "system", agregamos un mensaje de sistema con el prompt del asistente
        if not mensajes or mensajes[0].type != "system":
            mensajes = [("system", SYSTEM_PROMPT)] + mensajes
        respuesta = llm_con_tools.invoke(mensajes)
        return {"messages": [respuesta]}
    return llamar_llm


def build_tools_node(tools_por_nombre: dict):
    def ejecutar_tools(state: dict) -> dict:
        #El último mensaje de la lista de state["messages"][-1] es un mensaje de tipo "tool" que contiene una lista de llamadas a herramientas en la clave "tool_calls"
        ultimo_mensaje = state["messages"][-1]
        resultados = []
        #Si el último mensaje es de tipo "tool", ejecutamos las llamadas a las herramientas
        for tool_call in ultimo_mensaje.tool_calls:
            #tool_call es un diccionario con las claves "name" y "args", donde "name" es el nombre de la herramienta a invocar y "args" son los argumentos a pasarle
            tool_fn = tools_por_nombre[tool_call["name"]]
            resultado = tool_fn.invoke(tool_call["args"])
            #Agregamos el resultado de la llamada a la herramienta a la lista de resultados, como un mensaje de tipo "tool" con el contenido del resultado y el id de la llamada a la herramienta
            resultados.append(
                ToolMessage(content=str(resultado), tool_call_id=tool_call["id"])
            )
        return {"messages": resultados}
    return ejecutar_tools