
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "chroma_db"
COLLECTION_NAME = "shopsphere_documents"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
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
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    hits = 0
    reciprocal_rank_total = 0.0

    print("\n=== RETRIEVAL EVALUATION ===")

    for case in TEST_CASES:
        question = case["question"]
        expected = case["expected_source"]

        embedding = model.encode(
            question,
            normalize_embeddings=True
        ).tolist()

        results = collection.query(
            query_embeddings=[embedding],
            n_results=min(TOP_K, collection.count())
        )

        sources = [
            metadata["file_name"]
            for metadata in results["metadatas"][0]
        ]

        print(f"\nQuestion: {question}")
        print(f"Expected source: {expected}")
        print("Retrieved sources:")
        for rank, source in enumerate(sources, start=1):
            print(f"  {rank}. {source}")

        if expected in sources:
            rank = sources.index(expected) + 1
            hits += 1
            reciprocal_rank_total += 1 / rank
            print(f"Result: PASS (rank {rank})")
        else:
            print("Result: FAIL (expected source not in top 3)")

    total = len(TEST_CASES)
    hit_rate = hits / total
    mrr = reciprocal_rank_total / total

    print("\n=== SUMMARY ===")
    print(f"Questions evaluated: {total}")
    print(f"Hits in top {TOP_K}: {hits}/{total}")
    print(f"Hit rate: {hit_rate:.2%}")
    print(f"Mean Reciprocal Rank (MRR): {mrr:.3f}")


if __name__ == "__main__":
    main()
