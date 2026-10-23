
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

from document_loader import load_documents
from chunk_documents import split_into_chunks


# Configuration
DB_PATH = "chroma_db"
COLLECTION_NAME = "shopsphere_documents"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def calculate_hash(text):
    """Create a fingerprint to detect document changes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_vector_store():
    print("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(path=DB_PATH)

    # Preserve the existing collection instead of deleting it.
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # Read current indexed IDs and metadata.
    existing_records = collection.get(include=["metadatas"])

    indexed_documents = {}

    for record_id, metadata in zip(
        existing_records["ids"],
        existing_records["metadatas"]
    ):
        if not metadata:
            continue

        document_id = metadata.get("document_id")

        if document_id:
            indexed_documents.setdefault(
                document_id, {"ids": [], "content_hash": None}
            )

            indexed_documents[document_id]["ids"].append(record_id)

            if metadata.get("content_hash"):
                indexed_documents[document_id]["content_hash"] = (
                    metadata["content_hash"]
                )

    print("Loading source documents...")
    documents = load_documents()

    source_document_ids = {
        document["document_id"] for document in documents
    }

    # Remove indexed documents that no longer exist in the source folder.
    deleted_documents = (
        set(indexed_documents.keys()) - source_document_ids
    )

    for document_id in deleted_documents:
        collection.delete(
            ids=indexed_documents[document_id]["ids"]
        )
        print(f"Removed deleted document: {document_id}")

    # Identify new or modified documents.
    changed_documents = []

    for document in documents:
        document_id = document["document_id"]
        content_hash = calculate_hash(document["text"])

        existing = indexed_documents.get(document_id)

        if existing and existing["content_hash"] == content_hash:
            print(f"Unchanged, skipped: {document['file_name']}")
            continue

        chunks = split_into_chunks(document["text"])

        if not chunks:
            continue

        changed_documents.append({
            "document_id": document_id,
            "file_name": document["file_name"],
            "content_hash": content_hash,
            "chunks": chunks
        })

    if not changed_documents:
        print("\nNo new or modified documents to index.")
        print(f"Documents in source folder: {len(documents)}")
        print(f"Chunks currently indexed: {collection.count()}")
        return

    # Load the embedding model only when indexing is needed.
    print("\nLoading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    texts = []
    ids = []
    metadatas = []

    for document in changed_documents:
        document_id = document["document_id"]

        # Remove old chunks for a modified document.
        if document_id in indexed_documents:
            collection.delete(
                ids=indexed_documents[document_id]["ids"]
            )
            print(f"Replacing old index: {document['file_name']}")
        else:
            print(f"Indexing new document: {document['file_name']}")

        for index, chunk in enumerate(
            document["chunks"], start=1
        ):
            ids.append(f"{document_id}::chunk_{index}")
            texts.append(chunk)

            metadatas.append({
                "document_id": document_id,
                "file_name": document["file_name"],
                "chunk_number": index,
                "content_hash": document["content_hash"]
            })

    print(f"\nGenerating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    ).tolist()

    # Insert the new chunks into the existing collection.
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("\nIncremental indexing complete!")
    print(f"Source documents found: {len(documents)}")
    print(f"Documents changed this run: {len(changed_documents)}")
    print(f"Documents removed this run: {len(deleted_documents)}")
    print(f"Total chunks currently indexed: {collection.count()}")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    build_vector_store()
