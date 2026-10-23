# RAG-Based Project Assistant

An AI-powered project assistant that combines Retrieval-Augmented Generation (RAG), PostgreSQL, ChromaDB, and Azure OpenAI to answer questions about project documents, status, blockers, deadlines, and change requests.

## Overview

Managing project information across meeting notes, Excel workbooks, requirements documents, and team updates can make it difficult to find the latest information.

The RAG-Based Project Assistant brings these sources together to help users retrieve relevant project information and generate context-aware answers. It combines structured project data stored in PostgreSQL with semantic document retrieval through ChromaDB and answer generation using Azure OpenAI.

## Key Features

- **Retrieval-Augmented Generation (RAG):** Retrieves relevant context before generating answers.
- **Semantic Search:** Uses ChromaDB and Sentence Transformers to find relevant document content.
- **Structured Data Integration:** Uses PostgreSQL to store and retrieve project information, including tasks, sprints, team details, and project history.
- **Excel Data Synchronization:** Synchronizes project data from Excel workbooks into PostgreSQL.
- **Document Ingestion:** Processes TXT and DOCX files for retrieval.
- **Incremental Indexing:** Uses SHA-256 content hashing to identify document changes and avoid unnecessary re-indexing.
- **Automated Dataset Monitoring:** Uses Watchdog to detect file changes and trigger the relevant synchronization or indexing workflow.
- **Source-Aware Answers:** Provides relevant source filenames to help users trace retrieved information.
- **Project Query Support:** Answers questions about project updates, blockers, deadlines, and client change requests.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| LLM | Azure OpenAI (GPT-4o-mini deployment) |
| RAG | Retrieval-Augmented Generation |
| Vector database | ChromaDB |
| Embeddings | Sentence Transformers — `all-MiniLM-L6-v2` |
| Structured database | PostgreSQL |
| Document formats | TXT, DOCX, XLSX |
| Excel processing | openpyxl |
| File monitoring | Watchdog |
| Environment configuration | python-dotenv |

## Architecture

```text
Project Documents and Excel Workbooks
                 |
                 v
          Dataset Directory
                 |
        +--------+---------+
        |                  |
        v                  v
  TXT / DOCX Files     Excel Workbooks
        |                  |
        v                  v
 Document Processing   PostgreSQL Sync
        |                  |
        v                  v
 Embeddings + ChromaDB  Structured Project Data
        |                  |
        +--------+---------+
                 |
                 v
          User Question
                 |
                 v
       Context Retrieval
       from ChromaDB and
          PostgreSQL
                 |
                 v
          Azure OpenAI
                 |
                 v
       Context-Aware Answer
       with Source Filenames
```

## Project Structure

```text
rag-based-project-assistant/
├── dataset/
│   ├── meetings/
│   ├── project_data/
│   ├── requirements/
│   └── updates/
├── .env.example
├── .gitignore
├── ai_analysis.py
├── build_vector_store.py
├── chunk_documents.py
├── create_tables.py
├── document_loader.py
├── evaluate_copilot.py
├── evaluate_retrieval.py
├── ingest_updates.py
├── load_project_events.py
├── project_history.py
├── project_intelligence.py
├── rag_chat.py
├── rerank_experiment.py
├── retrieval_metrics.py
├── search_documents.py
├── seed_data.py
├── sync_excel_to_postgres.py
├── test_db.py
├── watch_dataset.py
└── requirements.txt
```



## Setup and Configuration

### Prerequisites

- Python 3.12
- PostgreSQL
- Azure OpenAI access and a configured model deployment
- Required Python packages from `requirements.txt`

### 1. Clone the repository

```bash
git clone https://github.com/akshayapalle/rag-based-project-assistant.git
cd rag-based-project-assistant
```


### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a template.

Configure the following values:

```dotenv
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=postgres
DB_PASSWORD=your_database_password

# Azure OpenAI
AOAI_CHAT_ENDPOINT=your_azure_openai_endpoint
AOAI_CHAT_KEY=your_azure_openai_key
AOAI_CHAT_DEPLOYMENT=your_deployment_name
AOAI_API_VERSION_GPT=your_api_version
```


### 5. Prepare the database and dataset

- Create the PostgreSQL database and required tables.
- Place the approved project documents and Excel workbooks in the appropriate `dataset/` subdirectories.
- Configure the dataset paths if your local directory structure differs.

Use the relevant database setup, data synchronization, ingestion, and indexing scripts according to their dependencies.

### 6. Build the retrieval index

Run the document-processing and vector-store scripts to load supported documents, generate embeddings, and populate ChromaDB.

For example:

```bash
python build_vector_store.py
```

### 7. Run the assistant

Start the question-answering workflow:

```bash
python rag_chat.py
```

Run commands from the project root. Refer to the individual scripts for any additional setup or execution requirements.

## Example Questions

The assistant is designed to answer questions such as:

- What is the current OTP login blocker?
- What changes did the client request?
- What is the status of the authentication sprint?
- Which tasks are blocked?
- What is the deadline for the current sprint?
- What are the latest project updates?
- Which documents contain information about a particular issue?

Answers depend on the information available in the dataset and the configured databases and retrieval index.

## Evaluation

The project includes retrieval evaluation and experimentation scripts to assess search performance, including metrics such as Hit Rate and Mean Reciprocal Rank (MRR).

Additional testing can cover answer grounding, source accuracy, incremental indexing, file-monitoring behavior, and consistency between structured data and documents.

## Security Considerations

- Keep credentials in a local `.env` file.
- Exclude `.env`, virtual environments, generated vector databases, and caches from Git.
- Use only datasets approved for sharing.
- Do not publish confidential client documents, internal meeting notes, or personal information.
- Configure database access and Azure credentials securely.

## Future Improvements

- Add a web-based user interface.
- Improve source citations and answer-grounding validation.
- Expand automated evaluation for retrieval and answer quality.
- Add support for additional document formats and data sources.
- Improve monitoring, logging, and error handling.


