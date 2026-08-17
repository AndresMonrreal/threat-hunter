"""
Adaptador de LogQueryEnginePort usando PostgreSQL. Guarda y consulta
Detection en la tabla detections -- dato relacional, no vectorial.
"""
#Psycopg es para conectarse a Postgres y ejecutar queries SQL. No es un ORM, es
import psycopg
from datetime import datetime
from domain.entities.detection import Detection
from domain.ports.log_query_engine import LogQueryEnginePort


class PostgresLogEngineAdapter(LogQueryEnginePort):
    def __init__(self, conninfo: str):
        self._conninfo = conninfo

    def save_detections(self, detections: list[Detection]) -> None:
        if not detections:
            return
        #with psycopg.connect(self._conninfo) as conn: es un context manager que abre la conexion y la cierra automaticamente
        with psycopg.connect(self._conninfo) as conn:
            #EL with conn.cursor() as cur: sirve para crear un cursor que nos permite ejecutar queries SQL. El cursor se cierra automaticamente al salir del bloque with
            with conn.cursor() as cur:
                for d in detections:
                    cur.execute(
                        """
                        INSERT INTO detections (tipo, ip_origen, intentos, inicio, fin)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (ip_origen, inicio, fin) DO NOTHING
                        """,
                        (d.tipo, d.ip_origen, d.intentos, d.inicio, d.fin),
                    )
                conn.commit()

    def query_detections(
        self, ip_origen: str | None = None, desde: datetime | None = None
    ) -> list[Detection]:
        condiciones = []
        params = []
        if ip_origen:
            #Guardamos la ip = %s lo que significa que vamos a filtrar por la columna ip_origen en la tabla detections. El %s es un placeholder para el valor que vamos a pasar en params
            condiciones.append("ip_origen = %s")
            params.append(ip_origen)
        if desde:
            condiciones.append("inicio >= %s")
            params.append(desde)
        #Este where = f"WHERE {' AND '.join(condiciones)}" if condiciones else "" genera la clausula WHERE de la query SQL. Si hay condiciones, las unimos con AND, si no hay condiciones, el where queda vacio
        where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

        query = f"""
            SELECT tipo, ip_origen, intentos, inicio, fin
            FROM detections
            {where}
            ORDER BY inicio DESC
        """
        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                #El rows = cur.fetchall() obtiene todas las filas resultantes de la query ejecutada.
                #Cada fila es una tupla con los valores de las columnas seleccionadas en el SELECT
                rows = cur.fetchall()

        return [
            Detection(tipo=r[0], ip_origen=r[1], intentos=r[2], inicio=r[3], fin=r[4])
            for r in rows
        ]