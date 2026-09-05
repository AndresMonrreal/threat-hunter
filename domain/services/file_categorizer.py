import re 

CATEGORIAS = {
    "binario_elf": re.compile(r"ELF \d+-bit", re.IGNORECASE),
    "codigo_python": re.compile(r"Python script", re.IGNORECASE),
    "codigo_java_fuente": re.compile(r"Java source", re.IGNORECASE),
    "codigo_java_compilado": re.compile(r"compiled Java class", re.IGNORECASE),
    "codigo_php": re.compile(r"PHP script", re.IGNORECASE),
    "script_shell": re.compile(r"shell script", re.IGNORECASE),
    "ibm_i_programa": re.compile(r"\.(clle|cl|cbl|cblle)$", re.IGNORECASE),
    "ibm_i_savefile": re.compile(r"IBM OS/400 save file", re.IGNORECASE),
    "archivo_comprimido": re.compile(r"(Zip archive|JAR|compress|tar archive)", re.IGNORECASE),
    "certificado_o_llave": re.compile(r"(PEM certificate|PRIVATE KEY|PKCS)", re.IGNORECASE),
    "texto_plano": re.compile(r"(ASCII text|Unicode text|ISO-8859|EBCDIC)", re.IGNORECASE),
    "vacio": re.compile(r"^empty$", re.IGNORECASE),
}

def categorizar(file_type: str) -> str:
    for categoria, patron in CATEGORIAS.items():
        if patron.search(file_type):
            return categoria
    return "desconocido"

def es_hallazgo_notable(file_type: str, nombre_realtivo: str) -> str | None:
    """Regresa la razon si el archivo merece atencion especial o no"""

    if re.search(r"PRIVATE KEY", file_type, re.IGNORECASE):
        return "Llave privada en texto plano -- riesgo critico de exposicion de credenciales"

    if re.search(f"ELF", file_type, re.IGNORECASE):
        base = nombre_realtivo.rsplit("/", 1)[-1]
        if base.startswith(".") and re.match(r"^\.[a-zA-Z0-9]{1,3}$", base):
            return "Binario ELF con nombre oculto --patron de backdoor o malware"

    return None

ENTROPIA_ALTA = 7.5

def es_binario_empacado(file_type:str, entropy: float) -> str | None:
    if "ELF" in file_type and entropy >= ENTROPIA_ALTA:
        return f"Entropia muy alta ({entropy:.2f}) -- posible binario empacado o cifrado"
    return None
    