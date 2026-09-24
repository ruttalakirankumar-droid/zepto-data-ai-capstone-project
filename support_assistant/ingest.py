from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer


# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DB_DIR = BASE_DIR / "chroma_db"


# -----------------------------
# Load embedding model
# -----------------------------
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# Create ChromaDB
# -----------------------------
client = chromadb.PersistentClient(path=str(DB_DIR))

collection = client.get_or_create_collection(
    name="support_docs"
)


# -----------------------------
# Chunking function
# -----------------------------
def create_chunks(text, chunk_size=500, overlap=50):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# -----------------------------
# Read documents
# -----------------------------
documents = []
metadatas = []
ids = []

for file_path in sorted(DOCS_DIR.glob("*.txt")):

    text = file_path.read_text(encoding="utf-8")

    chunks = create_chunks(text)

    for index, chunk in enumerate(chunks):

        documents.append(chunk)

        metadatas.append({
            "document_id": file_path.stem,
            "chunk_id": f"{file_path.stem}_chunk_{index}"
        })

        ids.append(
            f"{file_path.stem}_chunk_{index}"
        )


# -----------------------------
# Generate embeddings
# -----------------------------
print(f"Creating embeddings for {len(documents)} chunks...")

embeddings = model.encode(
    documents,
    show_progress_bar=True
).tolist()


# -----------------------------
# Store in ChromaDB
# -----------------------------
collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings
)


# -----------------------------
# Verification
# -----------------------------
print("\nIngestion completed successfully!")
print(f"Documents/chunks stored: {collection.count()}")
print(f"ChromaDB location: {DB_DIR}")
print(f"Collection: {collection.name}")    