
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "chroma_db"
COLLECTION_NAME = "shopsphere_documents"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def search_documents(question, top_k=3):
    # Load the same embedding model used during indexing
    model = SentenceTransformer(MODEL_NAME)

    # Connect to the saved vector database
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    # Convert the question into an embedding
    question_embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    # Retrieve the most relevant document chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count())
    )

    for i, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        print(f"\n--- Result {i + 1} ---")
        print(f"Source: {metadata['file_name']}")
        print(f"Chunk: {metadata['chunk_number']}")
        print(f"Cosine distance: {distance:.4f}")
        print(document)


if __name__ == "__main__":
    question = input("Ask a question about ShopSphere: ")
    search_documents(question)
