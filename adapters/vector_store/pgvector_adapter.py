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

        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor() as cur:
                for chunk , embeddings in zip(chunks, embeddings):
                    cur.execute(
                        """
                        INSERT INTO chunks (id, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                        """,
                        (chunk.id,chunk.content,json.dumps(chunk.metadata),embeddings)
                    )        
                    conn.commit()

    def search(self, query_embedding: list[float], top_k: int = 5, filters: dict | None = None) -> list[SearchResult]:
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
        params = [query_embedding] + ([json.dumps(filters)] if filters else []) + [query_embedding, top_k]

        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()  
                    
        results = []
        for row in rows:
            chunk_id, content, metadata, score = row
            chunk = Chunk(id=chunk_id, content=content, metadata=metadata)
            results.append(SearchResult(chunk=chunk, score=score))        
        return results

    def delete_chunks(self, chunk_ids: list[str]) -> None:
        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM chunks WHERE id = ANY(%s)",
                    (chunk_ids,)
                )
                conn.commit()