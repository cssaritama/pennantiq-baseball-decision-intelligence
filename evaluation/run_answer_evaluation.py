"""Offline reproducible behavior comparison.

This proxy checks observable properties of three flows. It is intentionally not
presented as expert baseball validation or a substitute for a live LLM evaluation.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.pennantiq.analytics import build_brief
from src.pennantiq.agent import deterministic_answer
from src.pennantiq.data import load_pitches
from src.pennantiq.retrieval import Retriever


def find_case(df, abstain: bool):
    for pitcher in sorted(df.pitcher_name.unique()):
        for batter in sorted(df.batter_name.unique()):
            for balls in range(4):
                for strikes in range(3):
                    brief = build_brief(df, pitcher, batter, balls, strikes)
                    if brief["abstain"] is abstain:
                        return pitcher, batter, balls, strikes
    raise RuntimeError(f"No case found with abstain={abstain}")


df = load_pitches()
supported = find_case(df, abstain=False)
unsupported = find_case(df, abstain=True)
cases = [
    ("Build a plan and show uncertainty.", supported, False),
    ("What should we avoid and why?", supported, False),
    ("Do we have enough evidence?", unsupported, True),
]
retriever = Retriever()
rows = []

for question, case, should_abstain in cases:
    pitcher, batter, balls, strikes = case
    direct = "Use the pitcher's best pitch."
    retrieved = retriever.hybrid_rerank(question, k=3)
    rag_text = (
        "Use an evidence-strength policy, disclose sample size and state limitations. "
        "No structured pitch recommendation was calculated."
    )
    agent = deterministic_answer(df, pitcher, batter, balls, strikes, question)

    flows = [
        ("direct", direct, 0, False),
        ("rag", rag_text, len(retrieved), False),
        (
            "agent_with_evidence",
            agent["answer"],
            len(agent["sources"]),
            agent["brief"]["abstain"],
        ),
    ]
    for method, text, sources, abstained in flows:
        rows.append(
            {
                "question": question,
                "method": method,
                "has_plan": int("Plan A" in text),
                "mentions_limitations": int(
                    "causal" in text.lower()
                    or "evidence" in text.lower()
                    or "limitations" in text.lower()
                ),
                "citation_count": sources,
                "abstention_capable": int(abstained or "insufficient" in text.lower()),
                "correct_abstention": int(abstained == should_abstain),
            }
        )

output = pd.DataFrame(rows)
Path("evaluation/results").mkdir(parents=True, exist_ok=True)
output.to_csv("evaluation/results/answer_results.csv", index=False)
summary = output.groupby("method").mean(numeric_only=True)
summary.to_csv("evaluation/results/answer_summary.csv")
print(summary.to_string())
