# LLM Zoomcamp Rubric Traceability

| Evaluation criterion | Public implementation | Verification |
|---|---|---|
| Problem description | README + Product Requirements | Manual review |
| Retrieval flow | Knowledge base + retrieval + optional live LLM + deterministic tools | `streamlit run app.py` |
| Retrieval evaluation | 24-case benchmark; 4 approaches; winner used by default | `python evaluation/run_retrieval_evaluation.py` |
| LLM evaluation | Live Direct vs RAG vs Agent+Evidence using GitHub Models/Gemini/OpenAI | `Live LLM Evaluation` Action or `python evaluation/run_live_llm_evaluation.py` |
| Interface | Streamlit multi-tab application | `streamlit run app.py` |
| Ingestion pipeline | dlt → DuckDB | `python -m src.pennantiq.ingestion` |
| Monitoring | User feedback + at least 5 dashboard views | Generate answers, open Monitoring |
| Containerization | Full application in Docker Compose; LLM SDKs included | `docker compose up --build` |
| Reproducibility | Deterministic fixture, pinned packages, benchmark and scripts | `make verify` |
| Hybrid search | Weighted keyword/vector fusion | Retrieval evaluation |
| Reranking | Explicit reranker | Retrieval evaluation |
| Query rewriting | Deterministic rewrite policy | Retrieval tests |
| Cloud bonus | GCP reference architecture only | **No deployment bonus claimed until deployed** |
| Additional work | Shadow Mode, Decision Council, Trust Ledger, Responsible AI | Project docs + scripts |

No course point should be claimed unless the corresponding command succeeds in the exact submission commit.
