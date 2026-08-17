from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Detection:
    tipo: str          # ej. "fuerza_bruta_ssh"
    ip_origen: str
    intentos: int
    inicio: datetime
    fin: datetime