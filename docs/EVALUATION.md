# Evaluation

PennantIQ evaluates three different layers separately: retrieval, answer-policy behavior and chronological decision support. A live-provider LLM comparison is included for the final certificate run.

## 1. Retrieval evaluation

```bash
python evaluation/run_retrieval_evaluation.py
```

The bundled benchmark contains **24 questions** across confidence, Shadow Mode, scenario methodology, Trust Ledger, Statcast fields, adaptation signals, product scope and responsible use.

Compared methods:

- keyword;
- TF-IDF vector;
- hybrid;
- hybrid + overlap reranking.

Current bundled results:

| Method | Hit@1 | Hit@3 | Hit@5 | MRR@5 |
|---|---:|---:|---:|---:|
| keyword | 0.833 | 0.917 | 1.000 | 0.885 |
| **vector** | **0.917** | **1.000** | **1.000** | **0.951** |
| hybrid | 0.875 | 0.958 | 1.000 | 0.925 |
| hybrid + rerank | 0.917 | 0.958 | 1.000 | 0.946 |

The application reads `evaluation/results/best_retrieval_method.json`, so the evaluated winner is used by default. `RETRIEVAL_METHOD` can override it for experiments.

These results apply only to the bundled project benchmark; they are not claims about arbitrary baseball questions.

## 2. Offline answer-policy evaluation

```bash
python evaluation/run_answer_evaluation.py
```

This executable offline comparison tests direct, retrieval-grounded and evidence-aware behaviors without pretending that a deterministic baseline is a live LLM. It verifies evidence use, limitations and correct abstention mechanics.

## 3. Live LLM evaluation

The repository supports three real providers: GitHub Models, Gemini and OpenAI. For the public certificate path, GitHub Models is the default CI evaluator because GitHub Actions can authenticate with the repository's automatic `GITHUB_TOKEN` and `models: read` permission; this removes the need to publish or configure an external API secret.

Automatic CI path:

```text
.github/workflows/live-llm-evaluation.yml
```

Local Gemini example:

```bash
pip install -r requirements-llm.txt
export LLM_PROVIDER=gemini
export GEMINI_API_KEY="..."
python evaluation/run_live_llm_evaluation.py
```

Local GitHub Models example:

```bash
export LLM_PROVIDER=github
export GITHUB_MODELS_TOKEN="..."
python evaluation/run_live_llm_evaluation.py
```

The live script compares the same cases using:

1. `direct_llm` — model receives the question only;
2. `rag_llm` — model receives retrieved knowledge context;
3. `agent_evidence` — model receives deterministic baseball analytics plus retrieved evidence.

A rubric-based live LLM judge scores groundedness, actionability, uncertainty awareness and evidence use. The script writes raw answers, summary metrics and the selected approach under `evaluation/results/`.

**For the final submission, verify that the Live LLM Evaluation workflow is green and that the generated result files are committed or available as its workflow artifact.**

## 4. Shadow Mode

```bash
python scripts/run_shadow_mode.py
```

Shadow Mode cuts data chronologically. Recommendations use only prior records. Historical action comparisons remain associative rather than causal.

Current deterministic fixture results:

- evaluated rows: **14,252**;
- moderate/strong recommendation coverage: **4.67%**;
- observed pitch-family match rate: **12.90%**;
- observed defensive value when matched: **0.0036**;
- observed defensive value when not matched: **-0.0924**.

These values validate software mechanics on the synthetic fixture; they are **not MLB performance evidence**.

## Interpretation rules

- synthetic-data metrics validate software mechanics, not MLB performance;
- no handwritten result may be presented as generated evidence;
- model comparisons use the same evaluation set;
- insufficient evidence is a valid output;
- causal language is prohibited for descriptive historical comparisons;
- future production evaluation should include domain-expert usefulness and prospective timestamped plans.
