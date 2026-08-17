from domain.entities.log_event import LogEvent
from domain.services.brute_force_detector import detectar_fuerza_bruta
from datetime import datetime


def test_detecta_fuerza_bruta_con_5_intentos_en_ventana():
    base = datetime(2026, 7, 20, 3, 14, 20)
    eventos = [
        LogEvent(timestamp=base, ip_origen="185.220.101.45", usuario="admin", exitoso=False),
        LogEvent(timestamp=base.replace(second=22), ip_origen="185.220.101.45", usuario="test", exitoso=False),
        LogEvent(timestamp=base.replace(second=24), ip_origen="185.220.101.45", usuario="root", exitoso=False),
        LogEvent(timestamp=base.replace(second=26), ip_origen="185.220.101.45", usuario="oracle", exitoso=False),
        LogEvent(timestamp=base.replace(second=28), ip_origen="185.220.101.45", usuario="root", exitoso=False),
    ]

    detecciones = detectar_fuerza_bruta(eventos)

    assert len(detecciones) == 1
    assert detecciones[0].ip_origen == "185.220.101.45"
    assert detecciones[0].intentos == 5


def test_no_detecta_con_menos_de_5_intentos():
    base = datetime(2026, 7, 20, 3, 14, 20)
    eventos = [
        LogEvent(timestamp=base, ip_origen="1.2.3.4", usuario="root", exitoso=False),
        LogEvent(timestamp=base.replace(second=25), ip_origen="1.2.3.4", usuario="root", exitoso=False),
    ]

    detecciones = detectar_fuerza_bruta(eventos)

    assert len(detecciones) == 0


def test_login_exitoso_no_cuenta_como_fallo():
    eventos = [
        LogEvent(timestamp=datetime(2026, 7, 20, 9, 0, 0), ip_origen="200.30.15.9", usuario="andres", exitoso=True),
    ]

    detecciones = detectar_fuerza_bruta(eventos)

    assert len(detecciones) == 0