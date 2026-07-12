"""
Loader: convierte notas de Obsidian (.md) en Chunks.

Estas notas son SOURCE_TYPE = "obsidian_personal" -- conocimiento
propio del usuario, distinto de fuentes oficiales como ATT&CK.
El sistema debe tratarlas con esa distincion.
"""

import re
from pathlib import Path
from domain.entities.chunk import Chunk

SOURCE_TYPE = "obsidian_personal"

def _extract_tags(text:str) -> list[str]:
    return re.findall(r"#([\w/-]+)", text)

def _split_by_headings(text:str) -> list[str]:
    partes = re.split(r"\n(?=## )",text)
    return [p.strip() for p in partes if p.strip()]

def _split_by_length(text:str, max_length:int=2000) -> list[str]:
    if len(text) <= max_length:
        return [text]
    partes = []
    inicio = 0
    while inicio < len(text):
        fin = inicio + max_length
        partes.append(text[inicio:fin])
        inicio = fin
    return partes

def load_obsidian_notes(notes_dir:Path) -> list[Chunk]:
    valut = Path(notes_dir)
    chunks: list[Chunk] = []
    
    
    for md_file in valut.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        if not text.strip():
            continue
        
        relative_path = str(md_file.relative_to(valut))
        tags = _extract_tags(text)
        
        if len(text) < 1500:
            secciones_iniciales = [text]
        else:
            secciones_iniciales = _split_by_headings(text)
        
        secciones = []
        for seccion in secciones_iniciales:
            secciones.extend(_split_by_length(seccion))
            
        for i, seccion in enumerate(secciones):
            chunk_id = f"obsidian::{relative_path}::{i}"
            chunks.append(
                Chunk(
                    id=chunk_id,
                    content=seccion,
                    metadata={
                        "source_type": SOURCE_TYPE,
                        "note_path": relative_path,
                        "tags": tags
                    },
                )
            )
    return chunks