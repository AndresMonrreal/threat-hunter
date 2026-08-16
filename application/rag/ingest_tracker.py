import psycopg

def get_hash_registrado(conninfo: str, note_path: str) -> tuple[str, int] | None:
    """Regresa (hash, chunk_count) si la nota ya fue ingerida antes, o None si es que todavia no"""
    # With psycopg.connect(conninfo) as conn sirve para abrir una conexion a la base de datos y cerrarla automaticamente al final del bloque
    with psycopg.connect(conninfo) as conn:
        # with conn.cursor() as cur sirve para abrir un cursor para ejecutar consultas SQL y cerrarlo automaticamente al final del bloque
        with conn.cursor() as cur:
            # Ejecuta una consulta SQL para obtener el hash y el numero de chunks de la nota especificada
            cur.execute(
                "SELECT content_hash, chunk_count FROM ingested_notes WHERE note_path = %s",
                (note_path,)
            )
            # fila = cur.fetchone() obtiene la primera fila del resultado de la consulta, o None si no hay resultados
            fila = cur.fetchone()
            # retorna una tupla con el hash y el numero de chunks si la nota fue encontrada, o None si no fue encontrada
            return tuple(fila) if fila else None

def registrar_nota(conninfo: str, note_path: str, content_hash: str, chunk_count: int) -> None:
    """Inserta el registro de una nota nueva, o actualiza hash/chunk_count si ya existia (upsert)"""
    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            # ON CONFLICT hace el upsert: inserta si note_path es nuevo, actualiza si ya estaba registrado
            cur.execute(
                """INSERT INTO ingested_notes (note_path, content_hash, chunk_count, updated_at)
                VALUES (%s, %s, %s, now())
                ON CONFLICT (note_path) DO UPDATE SET
                    content_hash = EXCLUDED.content_hash,
                    chunk_count = EXCLUDED.chunk_count,
                    updated_at = now()
                """,
                (note_path, content_hash, chunk_count),
            )
            # conn.commit() guarda los cambios; sin esto el insert/update no persiste
            conn.commit()

def eliminar_registro(conninfo: str, note_path: str) -> None:
    """Borra el registro de una nota (se usa cuando la nota ya no existe en el vault)"""
    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM Ingested_notes WHERE note_path = %s", (note_path,)
            )
            conn.commit()

def listar_notas_registradas(connninfo: str) -> list[str]:
    """Regresa la lista de note_path de todas las notas ya ingeridas"""
    with psycopg.connect(connninfo) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT note_path FROM ingested_notes")
            # cada fila es una tupla de un solo campo (note_path,), fila[0] saca el string
            return [fila[0] for fila in cur.fetchall()]