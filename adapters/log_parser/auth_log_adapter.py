import re
from datetime import datetime
from domain.entities.log_event import LogEvent

# matchea lineas de auth.log tipo:
# "Failed password for invalid user admin from 185.220.101.45 port 51320 ssh2"
# "Accepted password for andres from 200.30.15.9 port 40500 ssh2"
PATRON_EVENTO_SSH = re.compile(
    r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2}).*"
    r"(Accepted|Failed) password for (?:invalid user )?(\S+) from "
    r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port"
)


def _parsear_timestamp(texto_fecha: str) -> datetime:
    # el log no trae el anio, se le pega el anio actual para
    # construir un datetime completo
    year_actual = datetime.now().year
    return datetime.strptime(f"{year_actual} {texto_fecha}", "%Y %b %d %H:%M:%S")


def parse_auth_log(ruta_log: str) -> list[LogEvent]:
    eventos = []
    with open(ruta_log, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = PATRON_EVENTO_SSH.search(line)
            if not match:
                continue
            eventos.append(LogEvent(
                timestamp=_parsear_timestamp(match.group(1)),
                exitoso=match.group(2) == "Accepted",
                usuario=match.group(3),
                ip_origen=match.group(4),
            ))
    return eventos