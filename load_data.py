from __future__ import annotations

import logging
from pathlib import Path

from rag import add_to_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks for retrieval."""
    clean = " ".join(text.split())
    if not clean:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(0, end - overlap)
    return chunks


def load_text_files(data_dir: Path = DATA_DIR) -> int:
    """Load every .txt file in data/ into the persistent ChromaDB collection."""
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    total = 0
    for text_file in sorted(data_dir.glob("*.txt")):
        content = text_file.read_text(encoding="utf-8")
        chunks = chunk_text(content)
        for index, chunk in enumerate(chunks):
            add_to_db(
                text=chunk,
                document_id=f"{text_file.stem}-{index}",
                metadata={"source": text_file.name, "chunk": index},
            )
            total += 1
        LOGGER.info("Loaded %s chunks from %s", len(chunks), text_file.name)

    return total


def main() -> None:
    try:
        total = load_text_files()
    except Exception as exc:
        raise SystemExit(f"Failed to load RAG data: {exc}") from exc
    print(f"Loaded {total} chunks into ChromaDB.")


if __name__ == "__main__":
    main()
