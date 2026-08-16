import re
PATRON_IP = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

# TLDs comunes, para reducir falsos positivos con nombres de archivo
# (ej. "informe.txt" no debe contar como dominio, aunque tenga la forma).
TLDS_VALIDOS = {
    "com", "net", "org", "io", "gov", "edu", "mil", "info", "biz",
    "co", "us", "ru", "cn", "de", "uk", "mx", "xyz", "top", "onion",
}

PATRON_DOMINIO = re.compile(
    r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b"
)

PATRON_MD5 = re.compile(r"\b[a-fA-F0-9]{32}\b")
PATRON_SHA1 = re.compile(r"\b[a-fA-F0-9]{40}\b")
PATRON_SHA256 = re.compile(r"\b[a-fA-F0-9]{64}\b")

def _octetos_validos(ip:str) -> bool:
    octetos = ip.split(".")
    #El all() devuelve True si todos los elementos del iterable son verdaderos, y False si al menos uno es falso.
    #El return all(0 <= int(octeto) <= 255 for octeto in octetos) verifica que cada octeto de la dirección IP esté en el rango válido de 0 a 255.
    return all(0 <= int(octeto) <= 255 for octeto in octetos)

def extraer_ips(texto: str) -> list[str]:
    candidatos = PATRON_IP.findall(texto)
    return [ip for ip in candidatos if _octetos_validos(ip)]

def extraer_dominios(texto: str) -> list[str]:
    candidatos = PATRON_DOMINIO.findall(texto)
    validos = []
    for dominio in candidatos:
        tld = dominio.rsplit(".", 1)[-1].lower()
        if tld in TLDS_VALIDOS:
            validos.append(dominio)
    return validos

def extraer_hashes(texto: str) -> dict[str, list[str]]:
    return {
        "md5": PATRON_MD5.findall(texto),
        "sha1": PATRON_SHA1.findall(texto),
        "sha256": PATRON_SHA256.findall(texto),
    }

def defanguear(indicador: str) -> str:
    #El replace() reemplaza todas las ocurrencias de un substring por otro en la cadena de texto.
    resultado = indicador.replace(".","[.]")
    #El http:// y https:// se reemplazan por hxxp:// y hxxps:// respectivamente, para evitar que los enlaces sean clicables o ejecutables.
    resultado = resultado.replace("http://","hxxp://")
    resultado = resultado.replace("https://","hxxps://")
    return resultado