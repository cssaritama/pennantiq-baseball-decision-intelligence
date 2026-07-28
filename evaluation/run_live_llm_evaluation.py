#!/usr/bin/env python3
"""Compare three live LLM approaches on the same PennantIQ cases.

Approaches:
1. direct_llm      - model sees the question only;
2. rag_llm         - model sees retrieved knowledge-base context;
3. agent_evidence  - model sees deterministic baseball analytics + retrieved evidence.

Supported providers: GitHub Models, Gemini, OpenAI.
The same configured model is also used as an LLM-as-judge. The script writes raw
answers, summary metrics and metadata to evaluation/results/.
"""
from __future__ import annotations

from pathlib import Path
import json
import os
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.pennantiq.agent import SYSTEM, deterministic_answer
from src.pennantiq.data import load_pitches
from src.pennantiq.llm_provider import call_llm
from src.pennantiq.retrieval import Retriever


PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
if PROVIDER not in {"github", "gemini", "openai"}:
    raise SystemExit(
        "Set LLM_PROVIDER=github, gemini or openai. GitHub Actions can use provider=github with its automatic GITHUB_TOKEN."
    )


def invoke(prompt: str) -> tuple[str, str]:
    return call_llm(prompt, provider=PROVIDER)


def judge_answer(question: str, evidence: dict, answer: str) -> dict:
    rubric = {
        "groundedness": "0-5: claims are supported by the supplied evidence and do not invent baseball facts",
        "actionability": "0-5: gives a clear, useful decision-support response",
        "uncertainty_awareness": "0-5: distinguishes evidence, uncertainty and insufficient samples",
        "evidence_use": "0-5: explicitly uses or cites the supplied evidence package",
    }
    prompt = f"""You are evaluating a baseball decision-support answer, not the sporting outcome.
Return JSON only with integer scores 0-5 for each rubric key plus a short rationale.
Question: {question}
Rubric: {json.dumps(rubric)}
Evidence package: {json.dumps(evidence, default=str)}
Candidate answer: {answer}
"""
    raw, _ = invoke(prompt)
    raw = raw.strip()
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        parsed = json.loads(raw[start:end])
    except Exception:
        parsed = {key: None for key in rubric}
        parsed["rationale"] = f"Judge output could not be parsed: {raw[:240]}"
    return parsed


def build_rag_context(question: str) -> list[dict]:
    return [
        {
            "score": round(score, 4),
            "title": doc.title,
            "source": doc.source,
            "excerpt": doc.text[:500],
        }
        for score, doc in Retriever().best(question, k=4)
    ]


frame = load_pitches()
cases = [
    {"pitcher": "Demo Ace", "batter": "Demo Hitter Alpha", "balls": 0, "strikes": 2, "question": "Build a pre-game attack plan and explain the evidence and limitations."},
    {"pitcher": "Demo Ace", "batter": "Demo Hitter Beta", "balls": 1, "strikes": 1, "question": "What should we prioritize in this matchup, and how confident should we be?"},
    {"pitcher": "Demo Ace", "batter": "Demo Hitter Gamma", "balls": 3, "strikes": 0, "question": "Do we have enough evidence to recommend a plan, or should we abstain?"},
    {"pitcher": "Demo Southpaw", "batter": "Demo Hitter Alpha", "balls": 0, "strikes": 0, "question": "Give Plan A, Plan B and what to avoid before this matchup."},
    {"pitcher": "Demo Southpaw", "batter": "Demo Hitter Beta", "balls": 2, "strikes": 2, "question": "Explain the safest evidence-backed approach without overclaiming causality."},
    {"pitcher": "Demo Rookie", "batter": "Demo Hitter Gamma", "balls": 0, "strikes": 0, "question": "This pitcher has sparse history. What can we responsibly recommend?"},
]

# GitHub Actions CI runs a lightweight representative evaluation to avoid
# unnecessary model throttling. Full evaluation remains available locally.
if os.getenv("CI", "false").lower() == "true":
    cases = cases[:3]

rows = []
model_name = None
for case_id, case in enumerate(cases, start=1):
    evidence_agent = deterministic_answer(
        frame,
        case["pitcher"],
        case["batter"],
        case["balls"],
        case["strikes"],
        case["question"],
    )
    rag_context = build_rag_context(case["question"])
    evidence_for_judge = {
        "brief": evidence_agent["brief"],
        "retrieved_sources": evidence_agent["sources"],
    }

    prompts = {
        "direct_llm": f"""{SYSTEM}\nQuestion: {case['question']}\nPitcher: {case['pitcher']}\nBatter: {case['batter']}\nCount: {case['balls']}-{case['strikes']}\nDo not pretend you have statistics that were not supplied.""",
        "rag_llm": f"""{SYSTEM}\nQuestion: {case['question']}\nKnowledge context: {json.dumps(rag_context, default=str)}\nUse the knowledge context, but do not invent matchup statistics.""",
        "agent_evidence": f"""{SYSTEM}\nQuestion: {case['question']}\nEvidence package: {json.dumps(evidence_for_judge, default=str)}\nUse the supplied deterministic analytics. Separate observed evidence from hypotheses.""",
    }

    for approach, prompt in prompts.items():
        started = time.perf_counter()
        answer, model_name = invoke(prompt)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        judgment = judge_answer(case["question"], evidence_for_judge, answer)
        rows.append(
            {
                "case_id": case_id,
                **case,
                "provider": PROVIDER,
                "model": model_name,
                "approach": approach,
                "latency_ms": latency_ms,
                "answer": answer,
                "groundedness": judgment.get("groundedness"),
                "actionability": judgment.get("actionability"),
                "uncertainty_awareness": judgment.get("uncertainty_awareness"),
                "evidence_use": judgment.get("evidence_use"),
                "judge_rationale": judgment.get("rationale"),
            }
        )

result = pd.DataFrame(rows)
score_cols = ["groundedness", "actionability", "uncertainty_awareness", "evidence_use"]
for col in score_cols:
    result[col] = pd.to_numeric(result[col], errors="coerce")
result["mean_quality_score"] = result[score_cols].mean(axis=1)
summary = (
    result.groupby("approach")
    .agg(
        mean_quality_score=("mean_quality_score", "mean"),
        groundedness=("groundedness", "mean"),
        actionability=("actionability", "mean"),
        uncertainty_awareness=("uncertainty_awareness", "mean"),
        evidence_use=("evidence_use", "mean"),
        avg_latency_ms=("latency_ms", "mean"),
    )
    .sort_values("mean_quality_score", ascending=False)
)

output = Path("evaluation/results")
output.mkdir(parents=True, exist_ok=True)
result.to_csv(output / f"live_llm_{PROVIDER}_results.csv", index=False)
summary.to_csv(output / f"live_llm_{PROVIDER}_summary.csv")
metadata = {
    "provider": PROVIDER,
    "model": model_name,
    "cases": len(cases),
    "judge": "same configured live provider; rubric-based LLM-as-judge",
    "selected_approach": summary.index[0] if not summary.empty else None,
    "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
}
(output / f"live_llm_{PROVIDER}_metadata.json").write_text(
    json.dumps(metadata, indent=2), encoding="utf-8"
)
print(summary.to_string())
