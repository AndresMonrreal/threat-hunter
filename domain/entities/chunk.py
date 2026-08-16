"""
Chunk: la unidad atómica de conocimiento que guardamos y recuperamos.

Puede ser una técnica de ATT&CK completa, una regla Sigma, o un fragmento
de una nota de Obsidian. No importa la fuente: para el dominio, todo
"conocimiento buscable" tiene esta misma forma.
"""

from dataclasses import dataclass, field

@dataclass(frozen=True)  # frozen=True hace la instancia inmutable, no se puede modificar despues de creada
class Chunk:
    id:str
    content:str
    metadata:dict = field(default_factory=dict)  # default_factory evita que todas las instancias compartan el mismo dict

@dataclass(frozen=True)
class SearchResult:
    chunk:Chunk
    score:float  # que tan similar es este chunk a la consulta (mientras mas alto, mas relevante)
        