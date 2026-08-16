"""
Adaptador de VectorStorePort usando pgvector sobre PostgreSQL.

Este archivo es el UNICO lugar del proyecto que sabe que existe
Postgres, psycopg, o pgvector. Todo lo demas solo conoce VectorStorePort.
"""

import json
import psycopg
from domain.entities.chunk import Chunk, SearchResult
from domain.ports.vector_store import VectorStorePort
class PgVectorAdapter(VectorStorePort):
    def __init__(self, conninfo:str):
        """
        conninfo: cadena de conexion a Postgres, ej.
        "host=localhost port=5432 dbname=threathunter user=thm password=..."
        Se recibe ya armada desde infrastructure/config.py — este
        archivo no sabe leer variables de entorno, solo recibe la conexion.
        """
        self._conninfo = conninfo

    def add_chunk(self,chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("La cantidad de chunks y embeddings debe coincidir.")
#El with psycopg.connect(self._conninfo) as conn: abre una conexion a la base de datos Postgres usando la cadena de conexion proporcionada.
        with psycopg.connect(self._conninfo) as conn:
    #El with conn.cursor() as cur: abre un cursor para ejecutar comandos SQL en la conexion. El cursor se cierra automaticamente al salir del bloque with.
            with conn.cursor() as cur:
                #EL zip(chunks, embeddings) combina las dos listas en pares (chunk, embedding) para iterar sobre ellas simultaneamente.
                for chunk , embeddings in zip(chunks, embeddings):
                    # ON CONFLICT hace upsert: si el chunk ya existe (mismo id) lo actualiza en vez de duplicarlo
                    cur.execute(
                        """
                        INSERT INTO chunks (id, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                        """,
                #Aqui se pasan los valores de cada chunk y su embedding como parametros de la query, evitando inyeccion SQL
                #el json.dumps(chunk.metadata) convierte el diccionario de metadata a una cadena JSON para almacenarlo en la base de datos
                        (chunk.id,chunk.content,json.dumps(chunk.metadata),embeddings)
                    )
                    # commit por cada chunk, no al final del loop
                    conn.commit()

    def search(self, query_embedding: list[float], top_k: int = 5, filters: dict | None = None) -> list[SearchResult]:
        # metadata @> %s filtra por chunks cuya metadata contenga el filtro dado (ej. {"platform": "Windows"})
        where_clause = ""
        params = [query_embedding]

        if filters:
            where_clause = "WHERE metadata @> %s"
            params.append(json.dumps(filters))
        params.append(top_k)
        query = f"""
                SELECT id, content, metadata, 1 - (embedding <=> %s::vector) AS score
                FROM chunks
                {where_clause}
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
        # <=> es la distancia coseno de pgvector; se usa dos veces en la query (score y order by),
        # por eso query_embedding se repite en la lista de params
        params = [query_embedding] + ([json.dumps(filters)] if filters else []) + [query_embedding, top_k]

        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()  
                    
        results = []
        # reconstruye cada fila cruda de postgres como Chunk + SearchResult del dominio
        for row in rows:
            chunk_id, content, metadata, score = row
            chunk = Chunk(id=chunk_id, content=content, metadata=metadata)
            results.append(SearchResult(chunk=chunk, score=score))
        return results

    def delete_chunks(self, chunk_ids: list[str]) -> None:
        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor() as cur:
                # ANY(%s) permite pasar la lista completa de ids en un solo DELETE
                cur.execute(
                    "DELETE FROM chunks WHERE id = ANY(%s)",
                    (chunk_ids,)
                )
                conn.commit()