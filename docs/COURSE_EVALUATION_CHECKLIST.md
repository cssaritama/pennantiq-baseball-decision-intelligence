# DataTalksClub LLM Zoomcamp — Evaluation Checklist

Source: official `project.md` rubric in the DataTalksClub `llm-zoomcamp` repository.

## Core criteria — 18 points maximum

### 1. Problem description — 0 / 1 / 2
- 0: problem not described.
- 1: brief or unclear.
- 2: well-described and the solved problem is clear.

**PennantIQ evidence:** `README.md` → Problem statement, Solution, target user and success criteria.

### 2. Retrieval flow — 0 / 1 / 2
- 0: no knowledge base or LLM.
- 1: LLM queried directly, no knowledge base.
- 2: knowledge base and LLM are both used.

**Evidence:** `knowledge_base/`, `src/pennantiq/retrieval.py`, `src/pennantiq/agent.py`, `src/pennantiq/llm_provider.py`.

### 3. Retrieval evaluation — 0 / 1 / 2
- 0: none.
- 1: one retrieval approach.
- 2: multiple approaches evaluated and the best is used.

**Evidence:** 24 cases; keyword, TF-IDF vector, hybrid, hybrid + rerank; generated winner used by `Retriever.best()`.

### 4. LLM evaluation — 0 / 1 / 2
- 0: no final LLM output evaluation.
- 1: one approach evaluated.
- 2: multiple approaches evaluated and the best is used.

**Evidence path:** Live LLM Evaluation Action compares Direct LLM, RAG LLM and Agent + Evidence. Final submission should preserve its generated result files or artifact.

### 5. Interface — 0 / 1 / 2
- 0: none.
- 1: CLI/script/notebook.
- 2: UI, web app or API.

**Evidence:** multi-workspace Streamlit application.

### 6. Ingestion pipeline — 0 / 1 / 2
- 0: none.
- 1: semi-automated script/notebook.
- 2: automated ingestion with a specialized tool.

**Evidence:** `dlt` pipeline to DuckDB in `src/pennantiq/ingestion.py`; CI executes it.

### 7. Monitoring — 0 / 1 / 2
- 0: none.
- 1: feedback OR dashboard.
- 2: feedback AND dashboard with at least five charts.

**Evidence:** feedback persistence plus Trust & Monitoring workspace with multiple dashboard views.

### 8. Containerization — 0 / 1 / 2
- 0: none.
- 1: Dockerfile for app OR Compose only for dependencies.
- 2: everything in Docker Compose.

**Evidence:** Dockerfile + `docker-compose.yml`; CI builds, starts and health-checks the Streamlit container.

### 9. Reproducibility — 0 / 1 / 2
- 0: unclear instructions/missing data.
- 1: incomplete instructions or missing dataset.
- 2: clear instructions, accessible dataset, easy run path and pinned versions.

**Evidence:** bundled deterministic fixture, source registry, pinned requirements, `make verify`, Docker path and setup docs.

## Best-practice points — 3 maximum

- Hybrid search — 1.
- Document reranking — 1.
- User query rewriting — 1.

PennantIQ implements and tests all three.

## Bonus

- Cloud deployment — 2 points when a real deployment is verified. The current repo documents GCP target architecture but intentionally does not claim this bonus yet.
- Up to 3 discretionary extra bonus points for additional work. PennantIQ provides Shadow Mode, Decision Council, decision memory, evidence gating, Responsible AI and extensive evaluation/documentation as possible reviewer-visible extras.

## Peer review obligation

The official project instructions require the student to evaluate three peer projects; the course states that each review provides extra points.

## Submission evidence

Reviewers receive:

1. public GitHub repository URL;
2. exact commit hash.

The final hash must refer to the exact project state being graded.
