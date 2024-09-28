# Coffee RAG

This is a simple RAG (Retrieval-Augmented Generation) demo using Chainlit.

## Setup

```bash
poetry shell
poetry install
```


## Run PostgreSQL

```bash
docker compose build postgresql
docker compose up -d postgresql
```

## Run

```bash
chainlit run coffee/main.py
```

