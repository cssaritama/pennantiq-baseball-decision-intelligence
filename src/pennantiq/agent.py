from __future__ import annotations

import json
import os

from .analytics import build_brief
from .retrieval import Retriever
from .llm_provider import call_llm

SYSTEM = """You are PennantIQ, an evidence-first pre-game baseball strategy assistant.
Never guarantee outcomes. Separate observed data, estimates and hypotheses. Abstain when evidence is insufficient.
Return a concise decision brief with Plan A, Plan B, Avoid, Evidence Strength and Limitations."""


def deterministic_answer(df, pitcher, batter, balls=0, strikes=0, query=""):
    brief = build_brief(df, pitcher, batter, balls, strikes)
    retrieval = Retriever().best(
        query or f"pitching matchup evidence confidence {pitcher} {batter}", k=3
    )
    sources = [
        {
            "score": round(score, 4),
            "title": document.title,
            "source": document.source,
            "excerpt": document.text[:240],
        }
        for score, document in retrieval
    ]

    if brief["abstain"]:
        answer = (
            "Insufficient evidence for a reliable recommendation. "
            "Expand the history window or use licensed/team-owned data."
        )
    else:
        plan_a = brief["plan_a"]
        plan_b = brief["plan_b"]
        avoid = brief["avoid"]
        answer = (
            f"Plan A: {plan_a['pitch_family']} in the {plan_a['zone_group']} region "
            f"(n={plan_a['n']}, {plan_a['confidence']} evidence). "
            f"Plan B: {plan_b['pitch_family']} in the {plan_b['zone_group']} region. "
            f"Avoid: {avoid['pitch_family']} in the {avoid['zone_group']} region. "
            "Treat this as descriptive scenario support, not a causal guarantee."
        )

    return {
        "answer": answer,
        "brief": brief,
        "sources": sources,
        "provider": "deterministic",
    }


def generate_answer(df, pitcher, batter, balls=0, strikes=0, query=""):
    base = deterministic_answer(df, pitcher, batter, balls, strikes, query)
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "mock":
        return base

    context = json.dumps(
        {"brief": base["brief"], "sources": base["sources"]}, default=str
    )
    prompt = f"{SYSTEM}\nUser question: {query}\nEvidence package: {context}"

    try:
        text, model = call_llm(prompt, provider=provider)
        base["answer"] = text
        base["provider"] = provider
        base["model"] = model
    except Exception as exc:  # deterministic answer remains available
        base["provider_error"] = str(exc)

    return base
