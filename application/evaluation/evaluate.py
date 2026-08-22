from application.evaluation.golden_dataset import GOLDEN_DATASET
from infrastructure.container import build_container
from application.hunting.execute_hunt import correlacionar_ioc, consultar_tecnica_attack

TOP_K = 3


def evaluar_recall(pregunta: str, expected_identifier: str, campo_metadata: str, container) -> tuple[bool, list[str]]:
    embedding = container.embedder.embed(pregunta)
    resultados = container.vector_store.search(query_embedding=embedding, top_k=TOP_K)
    encontrado = any(
        r.chunk.metadata.get(campo_metadata) == expected_identifier
        for r in resultados
    )
    return encontrado, [r.chunk.id for r in resultados]


def evaluar_ioc(pregunta: str, debe_encontrar: bool, container) -> bool:
    resultado = correlacionar_ioc(pregunta, container)
    hay_coincidencia = len(resultado["coincidencias_en_detecciones"]) > 0
    return hay_coincidencia == debe_encontrar

def evaluar_attack(pregunta: str, expected_technique_id: str, container) -> tuple[bool, list[str]]:
    resultado = consultar_tecnica_attack(pregunta, container)
    sources = resultado.get("sources", [])
    esperado = f"attack::{expected_technique_id}"
    return esperado in sources, sources

def main():
    container = build_container()

    aciertos_recall, total_recall = 0, 0
    aciertos_ioc, total_ioc = 0, 0

    print(f"Evaluando {len(GOLDEN_DATASET)} casos...\n")

    for caso in GOLDEN_DATASET:
        categoria = caso["categoria"]

        if categoria == "notas":
            ok, ids = evaluar_recall(caso["pregunta"], caso["expected_note_path"], "note_path", container)
            total_recall += 1
            aciertos_recall += int(ok)
            print(f"[{'OK' if ok else 'FALLO'}] (notas) {caso['pregunta']}")
            if not ok:
                print(f"        esperaba: {caso['expected_note_path']} | encontro: {ids}")

        elif categoria == "attack":
            ok, ids = evaluar_attack(caso["pregunta"], caso["expected_technique_id"], container)
            total_recall += 1
            aciertos_recall += int(ok)
            print(f"[{'OK' if ok else 'FALLO'}] (attack) {caso['pregunta']}")
            if not ok:
                print(f"        esperaba: {caso['expected_technique_id']} | encontro: {ids}")
                
        elif categoria == "ioc":
            ok = evaluar_ioc(caso["pregunta"], caso["debe_encontrar"], container)
            total_ioc += 1
            aciertos_ioc += int(ok)
            print(f"[{'OK' if ok else 'FALLO'}] (ioc) {caso['pregunta']}")

    print("\n=== Resumen ===")
    print(f"Recall@{TOP_K} (notas + attack): {aciertos_recall}/{total_recall} ({aciertos_recall/total_recall:.0%})")
    print(f"Correlacion de IOCs correcta:  {aciertos_ioc}/{total_ioc} ({aciertos_ioc/total_ioc:.0%})")


if __name__ == "__main__":
    main()