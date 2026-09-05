import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

from adapters.file_forensics.static_analyzer import analyze_file
from domain.services.file_categorizer import categorizar, es_hallazgo_notable, es_binario_empacado

directorio = Path(sys.argv[1] if len(sys.argv) > 1 else input("Ruta de la carpeta a analizar: ").strip())
archivos = [p for p in directorio.rglob("*") if p.is_file()]

print(f"Analizando {len(archivos)} archivos...\n")

registros = []
hallazgos = []
fallos = []

for i, archivo in enumerate(archivos, 1):
    relativo = str(archivo.relative_to(directorio))
    try:
        ev = analyze_file(str(archivo))
        categoria = categorizar(ev.file_type)

        razones = []
        r1 = es_hallazgo_notable(ev.file_type, relativo)
        if r1:
            razones.append(r1)
        r2 = es_binario_empacado(ev.file_type, ev.entropy)
        if r2:
            razones.append(r2)

        registros.append({
            "path": relativo,
            "file_type": ev.file_type,
            "mime_type": ev.mime_type,
            "categoria": categoria,
            "size_bytes": ev.size_bytes,
            "sha256": ev.sha256,
            "modified_at": ev.modified_at.isoformat(),
            "entropy": ev.entropy,
            "strings_sample": ev.strings_sample,
            "elf_info": ev.elf_info,
        })
        for razon in razones:
            hallazgos.append({"path": relativo, "razon": razon})

        print(f"[{i}/{len(archivos)}] {relativo}", end=" ")
        print(" HALLAZGO" if razones else "ok")
    except Exception as e:
        fallos.append({"path": relativo, "error": str(e)})
        print(f"[{i}/{len(archivos)}] {relativo} FALLO: {e}")

Path("forensic_report.json").write_text(
    json.dumps({"registros": registros, "hallazgos": hallazgos, "fallos": fallos}, indent=2)
)

conteo_categorias = Counter(r["categoria"] for r in registros)
por_categoria = defaultdict(list)
for r in registros:
    por_categoria[r["categoria"]].append(r["path"])

lineas = [f"# Reporte forense — {directorio}\n"]
lineas.append(f"Total de archivos analizados: {len(registros)} | Fallos: {len(fallos)}\n")

lineas.append("#--- Hallazgos notables\n")
if hallazgos:
    for h in hallazgos:
        lineas.append(f"- **{h['path']}** — {h['razon']}")
else:
    lineas.append("Ninguno detectado.")
lineas.append("")

lineas.append("## Resumen por categoría\n")
for categoria, cantidad in conteo_categorias.most_common():
    lineas.append(f"- **{categoria}**: {cantidad} archivos")
lineas.append("")

lineas.append(" Detalle por categoría\n")
for categoria, paths in sorted(por_categoria.items()):
    lineas.append(f"--- {categoria} ({len(paths)})")
    for p in sorted(paths)[:20]:
        lineas.append(f"- `{p}`")
    if len(paths) > 20:
        lineas.append(f"- y {len(paths) - 20} más")
    lineas.append("")

Path("forensic_report.md").write_text("\n".join(lineas))
print(f"\nHallazgos notables: {len(hallazgos)}\nReporte: forensic_report.md")