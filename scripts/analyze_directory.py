import sys
from pathlib import Path
from adapters.file_forensics.static_analyzer import analyze_file

directorio = Path(sys.argv[1] if len(sys.argv) > 1 else input("Ruta de la carpeta a analizar: ").strip())

if not directorio.is_dir():
    print(f"No es una carpeta valida: {directorio}")
    sys.exit(1)

archivos = [p for p in directorio.rglob("*") if p.is_file()]
print(f"Encontrados {len(archivos)} archivos en {directorio}\n")

resultados = []
fallos = []

for i, archivo in enumerate(archivos, 1):
    print(f"[{i}/{len(archivos)}] {archivo.relative_to(directorio)}", end=" ... ")
    try:
        evidencia = analyze_file(str(archivo))
        resultados.append(evidencia)
        print(f"OK ({evidencia.file_type[:50]})")
    except Exception as e:
        fallos.append((archivo, str(e)))
        print(f"FALLO: {e}")

print(f"\n=== Resumen ===")
print(f"Analizados con exito: {len(resultados)}")
print(f"Fallos:                {len(fallos)}")

if fallos:
    print("\nArchivos que fallaron:")
    for archivo, error in fallos:
        print(f"  {archivo.relative_to(directorio)}: {error}")