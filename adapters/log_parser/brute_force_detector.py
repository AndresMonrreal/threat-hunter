import re
from datetime import datetime
from collections import defaultdict
#EL re.compile() compila la expresion regular para que sea mas eficiente al usarla varias veces
PATRON_FALLO_SSH = re.compile(
    #El regex para detectar intentos fallidos de SSH y capturar la IP del atacante
    r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2}).*"
    #Esta de aqui es la parte que matchea el timestamp del log, que tiene el formato "Mes Dia Hora:Minuto:Segundo"
    r"Failed password for (?:invalid user )?\S+ from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port"
)

UMBRAL_INTENTOS = 5
VENTANA_SEGUNDOS = 60

def parsear_timestamp(texto_fecha: str) -> datetime:
    # auth.log no trae el año en el timestamp, se asume el año actual
    year_actual = datetime.now().year
    texto_completo = f"{year_actual} {texto_fecha}"
    return datetime.strptime(texto_completo, "%Y %b %d %H:%M:%S")

#Regresa una lista de tuplas (timestamp, ip) de todos los intentos fallidos de SSH encontrados en el log
def extraer_eventos(ruta_log: str) -> list[tuple[datetime,str]]:
    eventos = []
#El with open(ruta_log,"r", encoding="utf-8", errors="ignore") as f: abre el archivo de log en modo lectura, con codificación UTF-8 y omitiendo errores de codificación.
#Esto permite leer el archivo línea por línea sin que se interrumpa por caracteres no válidos.
    with open(ruta_log,"r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = PATRON_FALLO_SSH.search(line)
            if match:
                # group(1) es el timestamp del log, group(2) es la ip del intento fallido
                timestamp = parsear_timestamp(match.group(1))
                ip = match.group(2)
                eventos.append((timestamp, ip))
    return eventos


def detectar_fuerza_bruta(eventos: list[tuple[datetime, str]]) -> list[dict]:
    # agrupa los timestamps de fallo por ip, para analizar cada ip por separado
    #El defaultdict(list) crea un diccionario donde cada clave es una IP y el valor es una lista de timestamps de intentos fallidos asociados a esa IP.
    eventos_por_ip = defaultdict(list)
    for timestamp, ip in eventos:
        eventos_por_ip[ip].append(timestamp)

    alertas = []
    #El items() devuelve una vista de los pares clave-valor del diccionario, permitiendo iterar sobre cada IP y su lista de timestamps.
    for ip, timestamps in eventos_por_ip.items():
        timestamps.sort()

        # ventana deslizante: por cada evento, cuenta cuantos eventos de esa ip
        # caen dentro de los siguientes VENTANA_SEGUNDOS
        for i in range(len(timestamps)):
            inicio_ventana = timestamps[i]
            fin_ventana = inicio_ventana.timestamp() + VENTANA_SEGUNDOS
            #Eventos en la ventana: filtra los timestamps de la lista que caen dentro del rango de tiempo definido por inicio_ventana y fin_ventana.
            #El t for t in timestamps[i:] itera sobre los timestamps desde el índice i hasta el final de la lista, y la condición 
            #if t.timestamp() <= fin_ventana asegura que solo se incluyan aquellos que están dentro de la ventana de tiempo.
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
                break # ya se alerto por esta ip, no revisar mas eventos de esa ip
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