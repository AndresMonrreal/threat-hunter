import re
from datetime import datetime
from collections import defaultdict

PATRON_FALLO_SSH = re.compile(
    r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2}).*"
    r"Failed password for (?:invalid user )?\S+ from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port"
)

UMBRAL_INTENTOS = 5
VENTANA_SEGUNDOS = 60

def parsear_timestamp(texto_fecha: str) -> datetime:
    year_actual = datetime.now().year
    texto_completo = f"{year_actual} {texto_fecha}"
    #EL strptime() convierte una cadena de texto en un objeto datetime según el formato especificado.
    return datetime.strptime(texto_completo, "%Y %b %d %H:%M:%S")

#El list[tuple[datetime, str]] indica que la función devuelve una lista de tuplas, donde cada tupla contiene un objeto datetime y una cadena de texto (str).
#  Esto es útil para representar eventos con su marca de tiempo y la dirección IP asociada.
def extraer_eventos(ruta_log: str) -> list[tuple[datetime,str]]:
    eventos = []

    with open(ruta_log,"r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = PATRON_FALLO_SSH.search(line)
            if match:
                #EL parsear_timestamp() convierte la cadena de texto que representa la fecha y hora en un objeto datetime
                #EL match.group(1) obtiene la primera coincidencia del patrón regex, que corresponde a la marca de tiempo del evento
                timestamp = parsear_timestamp(match.group(1))
                #Marcamos la ip con el match.group(2) que obtiene la segunda coincidencia del patrón regex, que corresponde a la dirección IP desde la cual se intentó el acceso fallido
                ip = match.group(2)
                eventos.append((timestamp, ip))
    return eventos


def detectar_fuerza_bruta(eventos: list[tuple[datetime, str]]) -> list[dict]:
    #El defaultdict(list) crea un diccionario donde cada clave es una dirección IP y su valor asociado es una lista de marcas de tiempo (timestamps)
    # de los eventos de fallo de autenticación para esa IP.
    eventos_por_ip = defaultdict(list)
    for timestamp, ip in eventos:
    #El eventos_por_ip[ip].append(timestamp) agrega la marca de tiempo del evento a la lista correspondiente a la dirección IP en el diccionario eventos_por_ip.
        eventos_por_ip[ip].append(timestamp)

    alertas = []
    #El items() devuelve una vista de los pares clave-valor del diccionario eventos_por_ip,
    # lo que permite iterar sobre cada dirección IP y su lista de marcas de tiempo asociadas.
    for ip, timestamps in eventos_por_ip.items():
        timestamps.sort()

        for i in range(len(timestamps)):
            inicio_ventana = timestamps[i]
            #EL inicio_ventana.timestamp() obtiene el timestamp del evento
            fin_ventana = inicio_ventana.timestamp() + VENTANA_SEGUNDOS
            #EL t for t in timestamps[i:] itera sobre las marcas de tiempo desde la posición i hasta el final de la lista.
            #Y en eventos_en_ventana se almacenan solo aquellos eventos cuya marca de tiempo es menor o igual a fin_ventana, es decir,
            # los eventos que ocurren dentro de la ventana de tiempo especificada.
            eventos_en_ventana = [
                t for t in timestamps [i:] 
                if t.timestamp() <= fin_ventana
            ]

            if len(eventos_en_ventana) >= UMBRAL_INTENTOS:
                alertas.append({
                    "ip": ip,
                    "intentos": len(eventos_en_ventana),
                    "inicio": eventos_en_ventana[0],
                    "fin": eventos_en_ventana[-1]
                })
                break #Ya se alerto por ip no revisar mas eventos de esa ip
    return alertas

def main():
    ruta = "muestra_auth.log"
    eventos = extraer_eventos(ruta)
    alertas = detectar_fuerza_bruta(eventos)

    print(f"Total de eventos de fallo prarseados: {len(eventos)}")

    if not alertas:
        print("No se detectaron ataques de fuerza bruta")
        return

    print(f"ALERTAS: {len(alertas)} ataques de fuerza bruta detectados:\n")
    for alerta in alertas:
        print(f"    IP: {alerta['ip']}")
        print(f"    Intentos: {alerta['intentos']} en {VENTANA_SEGUNDOS} ")
        print(f"    Ventana: {alerta['inicio']} -> {alerta['fin']}")
        print()

if __name__ == "__main__":
    main()      