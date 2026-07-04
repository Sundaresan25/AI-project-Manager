from rag import add_to_db

with open("data/architecture_notes.txt", "r", encoding="utf-8") as f:
    content = f.read()

# split into chunks (simple version)
chunks = content.split("\n")

for i, chunk in enumerate(chunks):
    if chunk.strip():
        add_to_db(chunk, f"doc_{i}")

print("Data loaded into ChromaDB")