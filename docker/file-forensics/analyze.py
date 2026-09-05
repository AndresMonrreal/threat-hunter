import sys
import json 
import hashlib
import subprocess
import math
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

def calcular_hashes(path: Path) -> dict[str, str]:
    md5, sha1, sha256 = hashlib.md5(), hashlib.sha1(), hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            md5.update(bloque)
            sha1.update(bloque)
            sha256.update(bloque)
    return {
        "md5": md5.hexdigest(),
        "sha1": sha1.hexdigest(),
        "sha256": sha256.hexdigest(),
    }

def obtener_tipo(path: Path) -> str:
    resultado = subprocess.run(
        ["file", "--brief", str(path)],
        capture_output=True, text=True, timeout=10,
    )
    return resultado.stdout.strip()

def obtener_mime(path: Path) -> str:
    r = subprocess.run(["file", "--mime-type", "--brief", str(path)], capture_output=True, text=True, timeout=10)
    return r.stdout.strip()

def calcular_entropia(path: Path, muestra: int = 1_000_000) -> float:
    with open(path, "rb") as f:
        data = f.read(muestra)

    if not data:
        return 0.0
    contador = Counter(data)
    total = len(data)
    entropia = 0.0

    for cuenta in contador.values():
        p = cuenta / total
        entropia -= p * math.log2(p)
    return round(entropia, 3)

def extraer_strings(path: Path, min_length: int = 9, max_length: int = 60) -> list[str]:
    try:
        r = subprocess.run(
            [
                "strings", "-n", str(min_length),str(path)
            ],
            capture_output=True, text=True, timeout=15,
        )
        lineas = [l for l in r.stdout.splitlines() if l.strip()]
        return lineas[:max_length]
    except Exception :
        return []

def obtener_info_elf(path: Path) -> dict | None:
    try:
        r = subprocess.run(
            ["readelf", "-h", str(path)], capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0:
            return None
        info = {}
        for linea in r.stdout.splitlines():
            if ":" in linea:
                clave, _, valor = linea.partition(":")
                info[clave.strip()] = valor.strip()
        return info
    except Exception:
        return None

def main():
    path = Path(sys.argv[1])
    stat = path.stat()

    resultado = {
        "file_type": obtener_tipo(path),
        "mime_type": obtener_mime(path),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "entropy": calcular_entropia(path),
        "strings_sample": extraer_strings(path),
        "elf_info": obtener_info_elf(path),
        **calcular_hashes(path),
    }
    print(json.dumps(resultado))


if __name__ == "__main__":
    main()