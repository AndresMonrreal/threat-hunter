import json 
import subprocess
from datetime import datetime
from pathlib import Path

from domain.entities.file_evidence import FileEvidence

IMAGEN_DOCKER = "file-forensics:latest"

def analyze_file(ruta: str) -> FileEvidence:
    path = Path(ruta)
    if not path.is_file():
        raise FileNotFoundError(f"No existe o no es un archivo: {ruta}")

    resultado = subprocess.run([
            "docker", "run", "--rm",
            "--network", "none",                    # sin salida a internet desde el contenedor
            "--read-only",                            # filesystem del contenedor inmutable
            "--cap-drop", "ALL",                       # sin permisos extra de Linux
            "--security-opt", "no-new-privileges",
            "--memory", "256m", "--cpus", "0.5",       # limite de recursos, por si es una zip bomb
            "-v", f"{path}:/input/target:ro",          # la MUESTRA, solo lectura
            IMAGEN_DOCKER,
            "/input/target",
        ]
    , capture_output=True, text=True, timeout=30
    )

    if resultado.returncode != 0:
        raise RuntimeError(f"Error al analizar el archivo: {resultado.stderr.strip()}")

    datos = json.loads(resultado.stdout)

    return FileEvidence(
        path=str(path),
        sha256=datos["sha256"],
        md5=datos["md5"],
        sha1=datos["sha1"],
        file_type=datos["file_type"],
        size_bytes=datos["size_bytes"],
        modified_at=datetime.fromisoformat(datos["modified_at"]),
        analyzed_at=datetime.now(),
    )