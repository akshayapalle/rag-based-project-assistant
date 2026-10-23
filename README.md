# ShopSphere – AI Project Intelligence Dataset

This is a synthetic project dataset for building an AI-powered Project Intelligence / Project Copilot system.

## Goal

The system should reduce manual project-management work by:
1. Understanding team/client updates.
2. Extracting structured project changes.
3. Maintaining current project state.
4. Keeping historical project knowledge searchable with RAG.
5. Allowing PM approval before important changes are committed.
6. Answering questions such as:
   - What changed this week?
   - What are the current blockers?
   - Why is Sprint 1 at risk?
   - What did the client request?
   - What changed in authentication?
   - Who is working on which task?

## Suggested first experiment

Do NOT start with agents.

First build:
Documents -> RAG -> Question Answering

Then:
Text update -> LLM structured extraction -> proposed database update

Then add:
PM approval -> database update

Then:
Voice -> speech-to-text -> same update pipeline

Finally evaluate whether AutoGen / Semantic Kernel is useful for orchestration.

## Important architecture principle

- SQL/database = current structured project state.
- Vector DB/RAG = unstructured historical/contextual knowledge.
- Original updates should be preserved for audit/history.
- AI should propose critical changes before committing them.
