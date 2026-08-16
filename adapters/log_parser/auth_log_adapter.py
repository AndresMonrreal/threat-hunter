import re
from collections import Counter

# matchea lineas de auth.log tipo:
# "Failed password for invalid user admin from 185.220.101.45 port 51320 ssh2"
#el re.compile() compila la expresion regular para que sea mas eficiente al usarla varias veces
PATRON_FALLO_SSH = re.compile(
    # regex para detectar intentos fallidos de SSH y capturar la IP del atacante
    r"Failed password for (?:invalid user )?\S+ from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port"
)

#Porque counter es util para contar ocurrencias de elementos en una lista o iterable.
#En este caso, se usa para contar cuántos intentos fallidos de SSH provienen de cada dirección IP.
def contar_fallos_por_ip(ruta_log: str) -> Counter:
    contador = Counter()
#El with open(ruta_log,"r", encoding="utf-8", errors="ignore") as f: abre el archivo de log en modo lectura, con codificación UTF-8 y omitiendo errores de codificación.
#Esto permite leer el archivo línea por línea sin que se interrumpa por caracteres no válidos.
    with open(ruta_log,"r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = PATRON_FALLO_SSH.search(line)
            if match:
                ip = match.group(1)
                contador[ip] += 1

    return contador


def main():
    ruta = "muestra_auth.log"
    resultados = contar_fallos_por_ip(ruta)
    print(f"IPs con intentos fallidos de SSH ({len(resultados)}) distintos :\n")
    # most_common() ya regresa ordenado de mayor a menor cantidad, sin necesidad de sorted()
    for ip, cantidad in resultados.most_common():
        print(f" {ip:20} {cantidad} intentos fallidos ")

if __name__ == "__main__":
    main()