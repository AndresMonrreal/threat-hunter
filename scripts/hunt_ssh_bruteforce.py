#El sys nos permite acceder a los argumentos de la linea de comandos. En este caso, el primer argumento es la ruta del log a analizar.
#Si no se pasa ningun argumento, se usa un log de prueba por defecto
import sys
from adapters.log_parser.auth_log_adapter import parse_auth_log
from domain.services.brute_force_detector import detectar_fuerza_bruta
from infrastructure.container import build_container

#por defecto usa el fixture de prueba; se puede pasar otra ruta como argumento
#En esta ruta sys.argv[1] es el primer argumento de la linea de comandos, que es la ruta del log a analizar.
#Si no se pasa ningun argumento, se usa un log de prueba por defecto
#El > 1 else "tests/fixtures/muestra_auth.log" significa que si no se pasa ningun argumento, se usa el log de prueba por defecto
ruta_log = sys.argv[1] if len(sys.argv) > 1 else "tests/fixtures/muestra_auth.log"

container = build_container()

print(f"1) Parseando: {ruta_log}")
eventos = parse_auth_log(ruta_log)
print(f"   {len(eventos)} eventos encontrados")

print("\n2) Buscando patrones de fuerza bruta...")
detecciones = detectar_fuerza_bruta(eventos)
print(f"   {len(detecciones)} deteccion(es) encontrada(s)")
for d in detecciones:
    print(f"   ALERTA: {d.ip_origen} - {d.intentos} intentos entre {d.inicio} y {d.fin}")

if detecciones:
    print("\n3) Guardando en Postgres...")
    container.log_engine.save_detections(detecciones)
    print("   OK")
else:
    print("\n3) Nada que guardar.") 