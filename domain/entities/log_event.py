from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LogEvent:
    timestamp: datetime
    ip_origen: str
    usuario: str
    exitoso: bool
