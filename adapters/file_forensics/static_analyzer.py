import json
import subprocess
from datetime import datetime
from pathlib import Path
import os

from domain.entities.file_evidence import FileEvidence

IMAGEN_DOCKER = os.environ.get("FORENSICS_DOCKER_IMAGE", "file-forensics:latest")

def analyze_file(ruta: str) -> FileEvidence:
    path = Path(ruta).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No existe o no es un archivo: {ruta}")

    resultado = subprocess.run(
        [
            "docker", "run", "--rm",
            "--network", "none",
            "--read-only",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--memory", "256m", "--cpus", "0.5",
            "-v", f"{path}:/input/target:ro",
            IMAGEN_DOCKER,
            "/input/target",
        ],
        capture_output=True, text=True, timeout=30,
    )

    if resultado.returncode != 0:
        raise RuntimeError(f"Fallo el analisis en contenedor: {resultado.stderr}")

    datos = json.loads(resultado.stdout)

    return FileEvidence(
        path=str(path),
        sha256=datos["sha256"],
        md5=datos["md5"],
        sha1=datos["sha1"],
        file_type=datos["file_type"],
        mime_type=datos["mime_type"],
        size_bytes=datos["size_bytes"],
        modified_at=datetime.fromisoformat(datos["modified_at"]),
        analyzed_at=datetime.now(),
        entropy=datos["entropy"],
        strings_sample=datos["strings_sample"],
        elf_info=datos["elf_info"],
    )