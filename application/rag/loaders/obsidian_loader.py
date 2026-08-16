"""
Loader: convierte notas de Obsidian (.md) en Chunks.
Estas notas son SOURCE_TYPE = "obsidian_personal", concimiento 
de las notas del cada uno como usuario
"""
import re
from pathlib import Path
from domain.entities.chunk import Chunk

SOURCE_TYPE = "obsidian_personal"


def _extract_tags(text: str) -> list[str]:
    # busca tags estilo Obsidian, ej. #tag o #tag/subtag
    return re.findall(r"#([\w/-]+)", text)


def _split_by_headings(text: str) -> list[str]:
    # corta el texto antes de cada "## " (subtitulo nivel 2), cada trozo es una seccion
    partes = re.split(r"\n(?=## )", text)
    return [p.strip() for p in partes if p.strip()]


def _split_by_length(text: str, max_length: int = 2000) -> list[str]:
    if len(text) <= max_length:
        return [text]
    partes = []
    inicio = 0
    # corta el texto en bloques de max_length caracteres, sin respetar palabras ni oraciones
    while inicio < len(text):
        fin = inicio + max_length
        partes.append(text[inicio:fin])
        inicio = fin
    return partes


def load_note_chunks(md_file: Path, vault: Path) -> list[Chunk]:
    """Convierte una nota en su lista de Chunks.
    Se separo de load_obsidian_notes para que la ingesta completa
    y la incremental compartan la misma logica de chunking, en vez
    de tenerla duplicada en dos scripts distintos."""
    text = md_file.read_text(encoding="utf-8", errors="ignore")
    # nota vacia (solo espacios en blanco), no genera chunks
    if not text.strip():
        return []

    relative_path = str(md_file.relative_to(vault))
    tags = _extract_tags(text)

    # notas cortas no vale la pena dividirlas por heading, se tratan como una sola seccion
    if len(text) < 1500:
        secciones_iniciales = [text]
    else:
        secciones_iniciales = _split_by_headings(text)

    secciones = []
    # aplica el limite de longitud tambien a cada seccion, por si un heading resulto muy largo
    for seccion in secciones_iniciales:
        secciones.extend(_split_by_length(seccion))

    chunks = []
    for i, seccion in enumerate(secciones):
        # id unico por nota + indice de seccion, permite borrar/reemplazar los chunks de una nota especifica
        chunk_id = f"obsidian::{relative_path}::{i}"
        chunks.append(
            Chunk(
                id=chunk_id,
                content=seccion,
                metadata={
                    "source_type": SOURCE_TYPE,
                    "note_path": relative_path,
                    "tags": tags,
                },
            )
        )
    return chunks


def load_obsidian_notes(notes_dir: Path) -> list[Chunk]:
    vault = Path(notes_dir)
    chunks: list[Chunk] = []
    # recorre recursivamente todo el vault buscando archivos .md
    for md_file in vault.rglob("*.md"):
        chunks.extend(load_note_chunks(md_file, vault))
    return chunks