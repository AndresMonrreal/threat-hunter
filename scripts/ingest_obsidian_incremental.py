import hashlib
from pathlib import Path

from application.rag.loaders.obsidian_loader import load_note_chunks
from application.rag.ingest_tracker import (
    get_hash_registrado,
    registrar_nota,
    eliminar_registro,
    listar_notas_registradas,
)

from infrastructure.container import build_container
from infrastructure.config import load_settings

settings = load_settings()
container = build_container()
VAULT = Path(settings.obsidian_vault_path)

print(f"1- Recorriendo vault: {VAULT}")

notas_encontradas = set()
nuevas, actualizadas, sin_cambios = 0, 0, 0

for md_file in VAULT.rglob("*.md"):
    text = md_file.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        continue

    note_path = str(md_file.relative_to(VAULT))
    notas_encontradas.add(note_path)
    # hash del contenido actual, para comparar contra lo ya registrado y detectar cambios
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    registro = get_hash_registrado(settings.postgres_conninfo, note_path)
    # Si el registro no es None, significa que la nota ya fue ingerida antes
    if registro is not None:
        hash_viejo , chunk_count_viejo = registro
        # mismo hash = el contenido no cambio, no hay nada que reingerir
        if hash_viejo == content_hash:
            sin_cambios += 1
            continue

        # borra los chunks viejos antes de reinsertar; si cambio el numero de secciones
        # los ids nuevos no coincidirian 1:1 con los viejos y quedarian chunks huerfanos
        ids_viejos = [f"obsidian::{note_path}::{i}" for i in range(chunk_count_viejo)]
        container.vector_store.delete_chunks(ids_viejos)
        actualizadas += 1
    else:
        nuevas += 1

    chunks = load_note_chunks(md_file, VAULT)
    for chunk in chunks:
        embedding = container.embedder.embed(chunk.content)
        container.vector_store.add_chunk([chunk], [embedding])
    registrar_nota(settings.postgres_conninfo, note_path, content_hash, len(chunks))
    print(f"   procesada: {note_path} ({len(chunks)} chunks)")

print(f"\n2- Nuevas: {nuevas} | Actualizadas: {actualizadas} | Sin cambios: {sin_cambios}")
registradas = set(listar_notas_registradas(settings.postgres_conninfo))
# notas que estan registradas en la DB pero ya no se encontraron en el vault: fueron borradas
borradas = registradas - notas_encontradas

for note_path in borradas:
    # recupera cuantos chunks tenia la nota para poder reconstruir sus ids y borrarlos
    _, chunk_count = get_hash_registrado(settings.postgres_conninfo, note_path)
    ids = [f"obsidian::{note_path}::{i}" for i in range(chunk_count)]
    container.vector_store.delete_chunks(ids)
    eliminar_registro(settings.postgres_conninfo, note_path)
    print(f"   eliminada: {note_path}")

print(f"\nIngesta incremental completa. {len(borradas)} notas eliminadas.")