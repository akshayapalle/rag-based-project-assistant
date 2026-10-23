
import os

import chromadb
from dotenv import load_dotenv
from openai import AzureOpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

DB_PATH = "chroma_db"
COLLECTION_NAME = "shopsphere_documents"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load the local embedding model
print("Loading embedding model...")
embedding_model = SentenceTransformer(MODEL_NAME)

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_collection(COLLECTION_NAME)

# Connect to Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=os.getenv("AOAI_CHAT_ENDPOINT"),
    api_key=os.getenv("AOAI_CHAT_KEY"),
    api_version=os.getenv("AOAI_API_VERSION_GPT")
)

deployment = os.getenv("AOAI_CHAT_DEPLOYMENT")


def retrieve_documents(question, top_k=3):
    question_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count())
    )

    sources = []

    for i, text in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]

        sources.append({
            "text": text,
            "file_name": metadata["file_name"],
            "document_id": metadata["document_id"],
            "distance": results["distances"][0][i]
        })

    return sources


def answer_question(question):
    sources = retrieve_documents(question)

    if not sources:
        print("No relevant documents were retrieved.")
        return

    evidence = "\n\n".join(
        f"Source: {source['file_name']}\n{source['text']}"
        for source in sources
    )

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ShopSphere Project Copilot. "
                    "Answer using only the supplied project evidence. "
                    "Do not invent facts. If the evidence is insufficient, "
                    "say so. Distinguish historical updates from current "
                    "status when the evidence permits. Mention relevant "
                    "dates and source filenames in your answer."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Retrieved project evidence:\n{evidence}"
                )
            }
        ],
        temperature=0.2
    )

    print("\nCopilot:")
    print(response.choices[0].message.content)

    print("\nSources retrieved:")
    for source in sources:
        print(
            f"- {source['file_name']} "
            f"(distance: {source['distance']:.4f})"
        )


if __name__ == "__main__":
    print("\n=== SHOPSPHERE RAG COPILOT ===")
    print("Type 'exit' to stop.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            print("Copilot stopped.")
            break

        if question:
            try:
                answer_question(question)
            except Exception as error:
                print(f"Error: {error}")
