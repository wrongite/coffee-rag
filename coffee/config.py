from os import getenv

DATASET_PATH = getenv("DATASET_PATH", "datasets/catalog.csv")
EMBEDDING_MODEL_NAME = getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-small")
EMBEDDING_QUERY_INSTRUCTION = getenv("EMBEDDING_QUERY_INSTRUCTION", "query: ")
EMBEDDING_TEXT_INSTRUCTION = getenv("EMBEDDING_TEXT_INSTRUCTION", "passage: ")


POSTGRES_USER = getenv("POSTGRES_USER", "coffee")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "coffee")
POSTGRES_DB = getenv("POSTGRES_DB", "coffee")
