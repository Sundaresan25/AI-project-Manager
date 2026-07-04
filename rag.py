from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_DIR = BASE_DIR / "db" / "chroma_db"
FALLBACK_DB_DIR = BASE_DIR / ".chroma" / "project_manager"
DB_DIR = Path(os.getenv("CHROMA_DB_PATH", str(DEFAULT_DB_DIR)))
COLLECTION_NAME = "project_manager_knowledge"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

_embedding_model: SentenceTransformer | None = None
_collection: Collection | None = None


def _get_embedding_model() -> SentenceTransformer:
    """Load the embedding model lazily so imports stay fast."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def _get_collection() -> Collection:
    """Return the persistent ChromaDB collection used by the RAG pipeline."""
    global _collection
    if _collection is None:
        try:
            _collection = _create_collection(DB_DIR)
        except Exception as exc:
            if DB_DIR == FALLBACK_DB_DIR:
                raise
            LOGGER.warning(
                "Unable to initialize ChromaDB at %s. Falling back to %s. Error: %s",
                DB_DIR,
                FALLBACK_DB_DIR,
                exc,
            )
            _collection = _create_collection(FALLBACK_DB_DIR)
    return _collection


def _create_collection(path: Path) -> Collection:
    path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(path),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _embed(text: str) -> list[float]:
    return _get_embedding_model().encode(text).tolist()


def _stable_document_id(text: str, source: str | None = None) -> str:
    identity = f"{source or 'manual'}::{text}".encode("utf-8")
    return hashlib.sha256(identity).hexdigest()


def add_to_db(
    text: str,
    document_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Embed a text chunk and upsert it into ChromaDB."""
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Cannot add empty text to the vector database.")

    source = metadata.get("source") if metadata else None
    doc_id = document_id or _stable_document_id(clean_text, str(source) if source else None)

    try:
        _get_collection().upsert(
            ids=[doc_id],
            embeddings=[_embed(clean_text)],
            documents=[clean_text],
            metadatas=[metadata or {}],
        )
    except Exception as exc:  # Chroma and model errors vary by environment.
        LOGGER.exception("Failed to add document %s to ChromaDB.", doc_id)
        raise RuntimeError(f"Failed to add document to ChromaDB: {exc}") from exc

    return doc_id


def search(query: str, n_results: int = 4) -> list[str]:
    """Search ChromaDB for text chunks related to the query."""
    clean_query = query.strip()
    if not clean_query:
        return []

    try:
        results = _get_collection().query(
            query_embeddings=[_embed(clean_query)],
            n_results=max(1, n_results),
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        LOGGER.exception("RAG search failed for query: %s", clean_query)
        return [f"RAG search failed: {exc}"]

    documents = results.get("documents") or [[]]
    return [doc for doc in documents[0] if doc]


def get_relevant_context(query: str, n_results: int = 4) -> str:
    """Return a readable context block for an agent."""
    matches = search(query=query, n_results=n_results)
    if not matches:
        return "No relevant context found in the local knowledge base."

    return "\n\n---\n\n".join(matches)
