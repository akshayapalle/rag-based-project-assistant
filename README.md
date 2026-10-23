# ShopSphere – Project Intelligence Dataset

## Overview

This directory contains a synthetic project dataset used by the **RAG-Based Project Assistant** to retrieve project information, answer project-related questions, and maintain structured project data.

The dataset represents a sample retail project called ShopSphere and includes meeting notes, project requirements, Excel workbooks, and team updates.

## Dataset Structure

```text
dataset/
├── meetings/
│   ├── meeting_01_2026-10-02.docx
│   └── meeting_02_2026-10-05.docx
├── project_data/
│   ├── change_requests.xlsx
│   ├── project.xlsx
│   ├── sprints.xlsx
│   ├── tasks.xlsx
│   └── team.xlsx
├── requirements/
│   ├── client_requirements.docx
│   └── project_scope.docx
└── updates/
    ├── update_01_2026-10-01.txt
    ├── update_02_2026-10-02.txt
    └── ...
```

## Data Categories

- **Meetings:** Meeting notes containing project discussions and decisions.
- **Project data:** Excel workbooks containing project details, team information, sprint information, tasks, and change requests.
- **Requirements:** Client requirements and project scope documents.
- **Updates:** Chronological text updates describing project progress, blockers, decisions, and changes.

## How the Dataset Is Used

The dataset supports two complementary information workflows.

### 1. Structured Project Data

Excel workbooks are synchronized with PostgreSQL to maintain structured information about the project, team, sprints, and tasks.

Text updates can also be parsed and stored in PostgreSQL for structured project-history tracking.

### 2. Document Retrieval and Question Answering

Meeting notes, requirements, and supported text documents are processed, split into chunks, converted into embeddings, and stored in ChromaDB.

When a user asks a question, the assistant retrieves relevant document context and combines it with structured project information from PostgreSQL before generating an answer using Azure OpenAI.

### 3. Incremental Updates

The project includes SHA-256 content hashing to identify document changes and Watchdog-based monitoring to detect changes in the dataset and trigger relevant synchronization or indexing workflows.

## Example Questions

The dataset can be used to answer questions such as:

- What are the latest project updates?
- What are the current blockers?
- Why is the authentication sprint at risk?
- What change requests did the client submit?
- What is the status of the OTP login task?
- Which team member is working on a particular task?
- Which documents contain information about a specific issue?

The quality and accuracy of answers depend on the available dataset, database contents, retrieval results, and model configuration.

## Architecture Principles

- **PostgreSQL:** Stores current structured project information and selected project-history records.
- **ChromaDB:** Stores document embeddings for semantic retrieval of historical and contextual information.
- **Azure OpenAI:** Generates answers using the retrieved context.
- **Original source files:** Remain available as source records for traceability.
- **Content hashing and file monitoring:** Help identify and respond to dataset changes.

## Dataset Scope and Limitations

This is a synthetic demonstration dataset, not a production project-management database.

The dataset supports project question answering and data synchronization experiments. It does not, by itself, guarantee that every update is automatically approved, that every source is synchronized without errors, or that all AI-generated answers are correct.

## Privacy and Usage

The dataset is intended for development, testing, and demonstration. Verify that all included files contain only synthetic or otherwise approved information before publishing the repository.

