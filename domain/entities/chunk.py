"""
Chunk: la unidad atómica de conocimiento que guardamos y recuperamos.

Puede ser una técnica de ATT&CK completa, una regla Sigma, o un fragmento
de una nota de Obsidian. No importa la fuente: para el dominio, todo
"conocimiento buscable" tiene esta misma forma.
"""

from dataclasses import dataclass, field 

@dataclass(frozen=True)
class Chunk:
    id:str
    content:str
    metadata:dict = field(default_factory=dict)

@dataclass(frozen=True)
class SearchResult:
    chunk:Chunk
    score:float
        