import re #Modulo de expresiones regulares de python el cual sabe buscar patrones de texto
from collections import Counter #Clase para poder contar cosas 
#Convierte el texto del patrón en un objeto regex reutilizable (re.compile)
#Permite aplicar el mismo patrón de búsqueda a múltiples cadenas de texto sin necesidad de reescribir o recompilar la expresión cada vez
PATRON_FALLO_SSH = re.compile(
    r"Failed password for (?:invalid user )?\S+ from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port"
)
#Example Failed password for invalid user admin from 185.220.101.45 port 51320 ssh2

def contar_fallos_por_ip(ruta_log: str) -> Counter:
    contador = Counter()

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
    #{ip:20} dentro del f-string es formato de columna: reserva 20 caracteres de ancho para la IP
    #El .most_common() nos ahorra el hecho de usar el sorted() para que nos muestre del mayor al menor
    for ip, cantidad in resultados.most_common():
        print(f" {ip:20} {cantidad} intentos fallidos ")

if __name__ == "__main__":
    main()