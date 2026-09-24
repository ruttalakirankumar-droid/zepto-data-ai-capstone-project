from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"


# -----------------------------
# Load embedding model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# Connect to ChromaDB
# -----------------------------
client = chromadb.PersistentClient(
    path=str(DB_DIR)
)

collection = client.get_collection(
    name="support_docs"
)


# -----------------------------
# Retrieve relevant documents
# -----------------------------
def retrieve_documents(query, top_k=3):

    query_embedding = model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        retrieved.append({
            "document": document,
            "document_id": metadata["document_id"],
            "chunk_id": metadata["chunk_id"],
            "distance": distance
        })

    return retrieved


# -----------------------------
# Test retrieval
# -----------------------------
if __name__ == "__main__":

    question = "How much is the delivery fee for orders below INR 149?"

    results = retrieve_documents(question)

    print("\nRetrieved documents:\n")

    for result in results:

        print("Document ID:", result["document_id"])
        print("Chunk ID:", result["chunk_id"])
        print("Distance:", result["distance"])
        print("Content:", result["document"])
        print("-" * 60)