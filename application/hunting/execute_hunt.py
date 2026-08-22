from domain.services.ioc_extractor import extraer_ips, extraer_dominios, extraer_hashes
from application.rag.answer_question import answer_question
from infrastructure.container import Container

import re   

PATRON_TECHNIQUE_ID = re.compile(r"\bT\d{4}(?:\.\d{3})?\b", re.IGNORECASE)

def buscar_notas(pregunta: str, container: Container):
    return answer_question(
        question=pregunta,
        embedder=container.embedder,
        vector_store=container.vector_store,
        llm=container.llm,
    )

def correlacionar_ioc(texto: str, container: Container):
    ips = extraer_ips(texto)
    dominios = extraer_dominios(texto)
    hashes = extraer_hashes(texto)

    #El resultado es un diccionario que contiene los IOCs encontrados y las coincidencias en notas y detecciones
    resultado = {
        #En {"ips": ips, "dominios": dominios, "hashes": hashes} se guardan los IOCs encontrados en el texto
        "iocs_encontrados": {"ips": ips, "dominios": dominios, "hashes": hashes},
        "coincidencias_en_notas": [],
        "coincidencias_en_detecciones": [],
    }

    for ip in ips:
        #En hits el container.vector_store.search busca en la base de datos de vectores las notas que contienen el IOC (en este caso, la IP) y devuelve los resultados más relevantes
        hits = container.vector_store.search(
            #El query_embedding=container.embedder.embed(ip) convierte la IP en un vector para poder buscarla en la base de datos de vectores
            query_embedding=container.embedder.embed(ip), top_k=2
        )

        for h in hits:
            if ip in h.chunk.content:
                #Aqui se guardan las coincidencias encontradas en las notas, incluyendo la IP, la ruta de la nota y el ID del chunk donde se encontró la coincidencia
                resultado["coincidencias_en_notas"].append(
                    {"ip": ip, "nota": h.chunk.metadata.get("note_path"), "chunk_id": h.chunk.id}
                )

        #En detecciones se guardan las detecciones que contienen la IP
        detecciones = container.log_engine.query_detections(ip_origen=ip)
        for d in detecciones:
            resultado["coincidencias_en_detecciones"].append(
                {"ip": ip, "tipo": d.tipo, "intentos": d.intentos, "inicio": str(d.inicio)}
            )

    return resultado


def consultar_detecciones(ip_origen: str | None, container: Container) -> dict:
    #Aqui en detecciones se guardan las detecciones que contienen la IP de origen
    #container.log_engine.query_detections busca en la base de datos de detecciones las que coinciden con la IP de origen
    detecciones = container.log_engine.query_detections(ip_origen=ip_origen)
    return {
        "detecciones": [
            {
                "ip": d.ip_origen,
                "tipo": d.tipo,
                "intentos": d.intentos,
                "inicio": str(d.inicio),
                "fin": str(d.fin),
            }
            #Retornamos una lista de diccionarios con la información de cada detección encontrada
            #Y el for d in detecciones al final de la lista de diccionarios indica que se va a iterar sobre cada detección encontrada y se va a crear un diccionario con la información de cada una
            for d in detecciones
        ]
    }

def consultar_tecnica_attack(consulta: str, container: Container) -> dict:
    """
    Busca tecnicas de MITRE ATT&CK. Si la consulta contiene un ID
    reconocible (ej. T1055, T1055.001), busca EXACTO por metadata en
    vez de semantico -- un ID corto como "T1055" no tiene suficiente
    contenido para que la busqueda por embeddings lo encuentre bien.
    """
    match = PATRON_TECHNIQUE_ID.search(consulta)
    if match:
        #El match.group(0) devuelve el primer grupo de la expresión regular que coincide con la consulta, que en este caso es el ID de la técnica (ej. T1055)
        technique_id = match.group(0).upper()
        chunk_id = f"attack::{technique_id}"
        # top_k alto + filtro por id exacto simula un "WHERE id = X"
        # sobre el vector store, sin necesitar un metodo get_by_id nuevo
        #El container.vector_store.search busca en la base de datos de vectores las notas que contienen el ID de la técnica y devuelve los resultados más relevantes
        resultados = container.vector_store.search(
            query_embedding=container.embedder.embed(consulta),
            top_k=1,
            filters={"technique_id": technique_id},
        )
        if resultados:
            r = resultados[0]
            return {
                "question": consulta,
                "answer": r.chunk.content,
                "sources": [r.chunk.id],
            }
        return {
            "question": consulta,
            "answer": f"No se encontro la tecnica {technique_id} en la base de ATT&CK ingerida.",
            "sources": [],
        }

    # sin ID reconocible -- pregunta conceptual, aqui si sirve semantico
    #Este es el caso en el que la consulta no contiene un ID de técnica reconocible, por lo que se realiza una búsqueda semántica en la base de datos
    #de vectores para encontrar la información más relevante sobre la técnica de MITRE ATT&CK relacionada con la consulta.
    return answer_question(
        question=consulta,
        embedder=container.embedder,
        vector_store=container.vector_store,
        llm=container.llm,
    )