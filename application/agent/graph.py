from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama

from application.agent.nodes import build_llm_node, build_tools_node
from application.hunting.execute_hunt import buscar_notas, consultar_detecciones, correlacionar_ioc
from infrastructure.container import Container
from langchain_core.tools import tool

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def _decidir_siguiente_paso(state: AgentState) -> str:
    ultimo_mensaje = state["messages"][-1]
    if ultimo_mensaje.tool_calls:
        return "tools"
    return END

def build_agent_graph(container: Container):

    @tool
    def buscar_notas_tool(pregunta: str) -> dict:
        """Busca en las notas personales del usuario sobre conceptos de ciberseguridad."""
        return buscar_notas(pregunta, container)

    @tool
    def correlacionar_ioc_tool(texto: str) -> dict:
        """Extrae IOCs (IPs, dominios, hashes) de un texto y busca coincidencias en notas y detecciones guardadas."""
        return correlacionar_ioc(texto, container)

    @tool
    def consultar_detecciones_tool(ip_origen: str | None = None) -> dict:
        """Consulta detecciones guardadas (alertas de fuerza bruta), opcionalmente filtradas por IP."""
        return consultar_detecciones(ip_origen, container)


    tools = [buscar_notas_tool, correlacionar_ioc_tool, consultar_detecciones_tool]
    tools_por_nombre = {t.name: t for t in tools}

    llm = ChatOllama(model=container.settings.llm_model, temperature=0)
    llm_con_tools = llm.bind_tools(tools)

    grafo = StateGraph(AgentState)

    grafo.add_node("llm", build_llm_node(llm_con_tools))
    grafo.add_node("tools", build_tools_node(tools_por_nombre))
    
    grafo.set_entry_point("llm")
    grafo.add_conditional_edges("llm", _decidir_siguiente_paso, {"tools": "tools", END: END})
    grafo.add_edge("tools", "llm")

    return grafo.compile()