
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

DB_PATH = "chroma_db"
COLLECTION_NAME = "shopsphere_documents"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

RETRIEVE_K = 10
TOP_K = 3

TEST_CASES = [
    {
        "question": "What is blocking OTP testing?",
        "expected_source": "update_09_2026-10-07.txt",
    },
    {
        "question": "Why is Sprint 1 at risk?",
        "expected_source": "update_06_2026-10-06.txt",
    },
    {
        "question": "What did the client request about authentication?",
        "expected_source": "update_02_2026-10-02.txt",
    },
    {
        "question": "What is the latest status of the Product Catalog UI?",
        "expected_source": "update_07_2026-10-06.txt",
    },
]


def main():
    print("Loading embedding model...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    print("Loading cross-encoder reranking model...")
    reranker = CrossEncoder(RERANK_MODEL)

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    baseline_hits = 0
    reranked_hits = 0
    baseline_rr = 0.0
    reranked_rr = 0.0

    for case in TEST_CASES:
        question = case["question"]
        expected = case["expected_source"]

        query_embedding = embedding_model.encode(
            question,
            normalize_embeddings=True
        ).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(RETRIEVE_K, collection.count())
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        candidates = [
            {
                "text": text,
                "file_name": metadata["file_name"],
                "document_id": metadata["document_id"],
            }
            for text, metadata in zip(documents, metadatas)
        ]

        # Original semantic-search order, evaluated at top 3.
        baseline_sources = [
            item["file_name"] for item in candidates[:TOP_K]
        ]

        # Score each question-document pair, then rank highest first.
        pairs = [
            [question, item["text"]]
            for item in candidates
        ]
        scores = reranker.predict(pairs)

        reranked_candidates = [
            item for _, item in sorted(
                zip(scores, candidates),
                key=lambda pair: float(pair[0]),
                reverse=True
            )
        ]

        reranked_sources = [
            item["file_name"]
            for item in reranked_candidates[:TOP_K]
        ]

        print("\n" + "=" * 70)
        print(f"Question: {question}")
        print(f"Expected: {expected}")

        print("\nOriginal top 3:")
        for rank, source in enumerate(baseline_sources, start=1):
            print(f"  {rank}. {source}")

        print("\nReranked top 3:")
        for rank, source in enumerate(reranked_sources, start=1):
            print(f"  {rank}. {source}")

        if expected in baseline_sources:
            rank = baseline_sources.index(expected) + 1
            baseline_hits += 1
            baseline_rr += 1 / rank

        if expected in reranked_sources:
            rank = reranked_sources.index(expected) + 1
            reranked_hits += 1
            reranked_rr += 1 / rank

    total = len(TEST_CASES)

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print(f"Original Hit Rate@3: {baseline_hits / total:.2%}")
    print(f"Reranked Hit Rate@3: {reranked_hits / total:.2%}")
    print(f"Original MRR: {baseline_rr / total:.3f}")
    print(f"Reranked MRR: {reranked_rr / total:.3f}")


if __name__ == "__main__":
    main()
