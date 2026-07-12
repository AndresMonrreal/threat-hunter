"""
Loader: convierte tecnicas de MITRE ATT&CK (formato STIX) en Chunks.

Estas tecnicas son SOURCE_TYPE = "attack_official" -- fuente de
verdad oficial, distinta de las notas personales del usuario.
"""

import json
from domain.entities.chunk import Chunk

SOURCE_TYPE = "attack_official"

def _get_technique_id(obj:dict) -> str | None:
    for ref in obj.get("external_references",[]):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None

def _get_tactics(obj:dict) -> list[str]:
    return [phase["phase_name"] for phase in obj.get("kill_chain_phases", [])]


def load_attack_techniques(json_path: str) -> list[Chunk]:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
        
    chunks: list[Chunk] = []
    
    for obj in data["objects"]:
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue
        
        technique_id = _get_technique_id(obj)
        if not technique_id:
            continue
        
        name = obj.get("name","")
        description = obj.get("description","")
        tactics = _get_tactics(obj)
        platform = obj.get("x_mitre_platforms",[])
        
        content = f"{technique_id} - {name}\n\n{description}"
        
        chunks.append(
            Chunk(
                id = f"attack::{technique_id}",
                content = content,
                metadata = {
                    "source_type": SOURCE_TYPE,
                    "technique_id": technique_id,
                    "name": name,
                    "tactics": tactics,
                    "platform": platform
                },
            )
        )
    return chunks