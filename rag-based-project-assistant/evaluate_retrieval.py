from search_documents import search_documents

test_questions = [
    "What is blocking OTP testing?",
    "Why is Sprint 1 at risk?",
    "What did the client request about authentication?",
    "What is the latest status of the Product Catalog UI?",
]

if __name__ == "__main__":
    for question in test_questions:
        print("\n" + "=" * 70)
        print(f"QUESTION: {question}")
        print("=" * 70)
        search_documents(question, top_k=3)