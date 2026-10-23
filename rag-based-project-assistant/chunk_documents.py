
from document_loader import load_documents

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping character-based chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Prefer ending at a word boundary
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def chunk_documents():
    documents = load_documents()
    all_chunks = []

    for document in documents:
        chunks = split_into_chunks(document["text"])

        for index, chunk in enumerate(chunks, start=1):
            all_chunks.append({
                "document_id": document["document_id"],
                "file_name": document["file_name"],
                "chunk_id": f"{document['document_id']}::chunk_{index}",
                "chunk_number": index,
                "text": chunk
            })

    return all_chunks


if __name__ == "__main__":
    chunks = chunk_documents()

    print(f"\nDocuments processed: {len(set(c['document_id'] for c in chunks))}")
    print(f"Total chunks created: {len(chunks)}")

    for chunk in chunks[:5]:
        print(f"\n--- {chunk['chunk_id']} ---")
        print(chunk["text"])
