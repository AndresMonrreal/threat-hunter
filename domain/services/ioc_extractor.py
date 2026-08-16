import re
PATRON_IP = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")  # forma de IPv4, no valida rango (eso lo hace _octetos_validos)

# TLDs comunes, para reducir falsos positivos con nombres de archivo
# (ej. "informe.txt" no debe contar como dominio, aunque tenga la forma).
TLDS_VALIDOS = {
    "com", "net", "org", "io", "gov", "edu", "mil", "info", "biz",
    "co", "us", "ru", "cn", "de", "uk", "mx", "xyz", "top", "onion",
}

PATRON_DOMINIO = re.compile(
    # regex para detectar dominios, sin validar TLDs
    r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b"
)
# largo del hash determina el tipo: 32 hex = md5, 40 = sha1, 64 = sha256
PATRON_MD5 = re.compile(r"\b[a-fA-F0-9]{32}\b")
PATRON_SHA1 = re.compile(r"\b[a-fA-F0-9]{40}\b")
PATRON_SHA256 = re.compile(r"\b[a-fA-F0-9]{64}\b")

def _octetos_validos(ip:str) -> bool:
    octetos = ip.split(".")
    # cada octeto debe estar entre 0 y 255 para ser una IP valida (el regex solo valida la forma)
    return all(0 <= int(octeto) <= 255 for octeto in octetos)

def extraer_ips(texto: str) -> list[str]:
    candidatos = PATRON_IP.findall(texto)
    # descarta matches con forma de IP pero octetos fuera de rango (ej. "999.999.999.999")
    return [ip for ip in candidatos if _octetos_validos(ip)]

def extraer_dominios(texto: str) -> list[str]:
    candidatos = PATRON_DOMINIO.findall(texto)
    validos = []
    for dominio in candidatos:
        tld = dominio.rsplit(".", 1)[-1].lower()  # ultimo segmento tras el punto, en minusculas
        # descarta matches que no tengan un TLD valido (ej. "informe.txt" no es un dominio)
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
    # inserta corchetes/letras x para que el IOC no sea clicable ni resoluble al copiarlo
    resultado = indicador.replace(".","[.]")
    resultado = resultado.replace("http://","hxxp://")
    resultado = resultado.replace("https://","hxxps://")
    return resultado