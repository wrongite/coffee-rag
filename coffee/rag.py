import csv
import logging

import asyncpg
import numpy as np
from sentence_transformers import SentenceTransformer

from config import (DATASET_PATH, EMBEDDING_MODEL_NAME,
                     EMBEDDING_QUERY_INSTRUCTION, EMBEDDING_TEXT_INSTRUCTION)


logger = logging.getLogger(__name__)
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
embedding_dimension = embedding_model.get_sentence_embedding_dimension()


def embed_text(text: str) -> np.ndarray:
    input_text = f"{EMBEDDING_TEXT_INSTRUCTION}{text}"
    return embedding_model.encode(input_text, normalize_embeddings=True)

def embed_query(query: str) -> np.ndarray:
    input_text = f"{EMBEDDING_QUERY_INSTRUCTION}{query}"
    return embedding_model.encode(input_text, normalize_embeddings=True)


async def reindex(conn: asyncpg.Connection, documents: list[dict]):
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    await conn.execute("DROP TABLE IF EXISTS documents")
    await conn.execute(
        f"CREATE TABLE documents (id bigserial PRIMARY KEY, content text, embedding vector({embedding_dimension}))" 
    )

    async with conn.transaction():
        for document in documents:
            content = document["content"]
            embedding = embed_text(content)
            await conn.execute(
                f"INSERT INTO documents (content, embedding) VALUES ($1, $2)",
                content,
                embedding,
            )
            logger.info(f"Inserted document: {content}")

async def reindex_dataset(conn: asyncpg.Connection):
    documents = []
    with open(DATASET_PATH, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            documents.append({"content": row["description"]})
    await reindex(conn, documents)


async def search(conn: asyncpg.Connection, query: str, limit: int = 5) -> list[dict]:
    embedding = embed_query(query)
    results = await conn.fetch(
        """
        SELECT id, content, 1 - (embedding <=> $1) as match_score
        FROM documents
        ORDER BY match_score DESC
        LIMIT $2
        """,
        embedding,
        limit,
    )
    return results
