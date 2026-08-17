"""
Servicio de dominio: analiza una lista de LogEvent ya parseados y
detecta patrones de fuerza bruta -- muchos intentos fallidos de la
misma IP en una ventana de tiempo corta. No toca disco ni Postgres,
solo trabaja con lo que le pasan.
"""
from collections import defaultdict, Counter
from domain.entities.log_event import LogEvent
from domain.entities.detection import Detection

UMBRAL_INTENTOS = 5
VENTANA_SEGUNDOS = 60


def contar_fallos_por_ip(eventos: list[LogEvent]) -> Counter:
    contador = Counter()
    for evento in eventos:
        if not evento.exitoso:
            #SI no ha sido exitoso, sumamos 1 al contador de la ip_origen
            contador[evento.ip_origen] += 1
    return contador


def detectar_fuerza_bruta(eventos: list[LogEvent]) -> list[Detection]:
    #defaultdict(list) es un diccionario que por defecto crea una lista vacia para cada clave nueva.
    #En este caso, la clave es la ip_origen y el valor es una lista de timestamps de fallos
    fallos_por_ip = defaultdict(list)
    for evento in eventos:
        if not evento.exitoso:
            #Si el evento no fue exitoso, agregamos el timestamp a la lista de fallos de esa ip_origen
            fallos_por_ip[evento.ip_origen].append(evento.timestamp)

    detecciones = []
    for ip, timestamps in fallos_por_ip.items():
        timestamps.sort()
        for i in range(len(timestamps)):
            fin_ventana = timestamps[i].timestamp() + VENTANA_SEGUNDOS
            #en_ventana = [t for t in timestamps[i:] if t.timestamp() <= fin_ventana]
            #es una lista de todos los timestamps que estan dentro de la ventana de tiempo de 60 segundos a partir del timestamp actual
            en_ventana = [t for t in timestamps[i:] if t.timestamp() <= fin_ventana]
            if len(en_ventana) >= UMBRAL_INTENTOS:
                detecciones.append(Detection(
                    tipo="fuerza_bruta_ssh",
                    ip_origen=ip,
                    intentos=len(en_ventana),
                    inicio=en_ventana[0],
                    fin=en_ventana[-1],
                ))
                break  # ya se alerto por esta ip, no revisar mas eventos de esa ip
    return detecciones 