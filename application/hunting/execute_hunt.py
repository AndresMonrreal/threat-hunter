from domain.services.ioc_extractor import extraer_ips, extraer_dominios, extraer_hashes
from application.rag.answer_question import answer_question
from infrastructure.container import Container

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
    
    resultado = {
        "iocs_encontrados": {"ips": ips, "dominios": dominios, "hashes": hashes},
        "coincidencias_en_notas": [],
        "coincidencias_en_detecciones": [],
    }

    for ip in ips:
        hits = container.vector_store.search(
            query_embedding=container.embedder.embed(ip), top_k=2
        )

        for h in hits:
            if ip in h.chunk.content:
                resultado["coincidencias_en_notas"].append(
                    {"ip": ip, "nota": h.chunk.metadata.get("note_path"), "chunk_id": h.chunk.id}
                )

        detecciones = container.log_engine.query_detections(ip_origen=ip)
        for d in detecciones:
            resultado["coincidencias_en_detecciones"].append(
                {"ip": ip, "tipo": d.tipo, "intentos": d.intentos, "inicio": str(d.inicio)}
            )

    return resultado


def consultar_detecciones(ip_origen: str | None, container: Container) -> dict:
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
            for d in detecciones
        ]
    }


