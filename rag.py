import chromadb
from sentence_transformers import SentenceTransformer
from crewai.tools import tool   # 🔥 IMPORTANT FIX

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="db/chroma_db")
collection = client.get_or_create_collection("architecture_docs")


def search(query):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )

    if results and results.get("documents"):
        return results["documents"][0]

    return "No relevant context found"


# 🔥 CREWAI TOOL WRAPPER (FIX)
@tool("Architecture Knowledge Search")
def rag_tool(query: str) -> str:
    """Search system design, API, DB, architecture knowledge"""
    return search(query)