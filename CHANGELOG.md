# Changelog

All notable public changes to PennantIQ are documented here.

## 0.1.0 — Initial public release

PennantIQ's first public release establishes an evidence-first Baseball Decision Intelligence prototype for the DataTalksClub LLM Zoomcamp and professional portfolio use.

### Included
- Streamlit decision-support interface.
- Deterministic baseball analytics and evidence policies.
- Decision Council orchestration contracts.
- Starter Pulse, Matchup Lab, Context Matrix and Shadow Mode.
- RAG knowledge base with keyword, vector, hybrid and reranked retrieval.
- Query rewriting and retrieval evaluation.
- Optional Gemini and OpenAI generation providers.
- dlt → DuckDB ingestion pipeline.
- Feedback and monitoring dashboard.
- Docker / Docker Compose packaging.
- GitHub Actions CI.
- GCP target architecture and open-core boundary.
- Responsible-use, data, model and legal documentation.

This is an independent research prototype. It is not affiliated with MLB or any club and does not guarantee sporting outcomes.

### Certificate hardening (v0.1.0)
- Added explicit problem statement, target user, success criteria and solution architecture to the README.
- Added automatic real-LLM evaluation with GitHub Models in GitHub Actions (`models: read`).
- Added GitHub Models as a third LLM provider alongside Gemini and OpenAI.
- Added an exact Zoomcamp rubric map and submission-ready guide.
- Added a provider guard test and refreshed verification evidence.


## v0.1.1-hotfix3
- Added CI-aware LLM evaluation sampling.
- Reduced GitHub Models CI cost using gpt-4o-mini.
- Improved resilience against temporary model throttling.
