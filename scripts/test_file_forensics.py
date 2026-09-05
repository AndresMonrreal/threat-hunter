from adapters.file_forensics.static_analyzer import analyze_file

ruta = input("Ruta del archivo a analizar: ").strip()
evidencia = analyze_file(ruta)

print(f"\nRuta:        {evidencia.path}")
print(f"Tipo:        {evidencia.file_type}")
print(f"MIME:        {evidencia.mime_type}")
print(f"Tamaño:      {evidencia.size_bytes} bytes")
print(f"Modificado:  {evidencia.modified_at}")
print(f"Entropía:    {evidencia.entropy}")
print(f"SHA256:      {evidencia.sha256}")
print(f"MD5:         {evidencia.md5}")

print(f"\n--- ELF info ---")
if evidencia.elf_info:
    for clave, valor in evidencia.elf_info.items():
        print(f"  {clave}: {valor}")
else:
    print("  (no aplica, no es ELF)")

print(f"\n--- Strings (primeras 15) ---")
for s in evidencia.strings_sample[:15]:
    print(f"  {s}")
print(f"   total capturados: {len(evidencia.strings_sample)}")