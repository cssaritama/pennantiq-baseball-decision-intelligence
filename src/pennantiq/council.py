from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import pandas as pd

from .analytics import adaptation_signals, build_brief
from .context import context_split_table
from .starter_readiness import starter_assessment


@dataclass(frozen=True)
class SpecialistReport:
    specialist: str
    role: str
    finding: str
    evidence: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _top_context(df: pd.DataFrame, pitcher: str, dimension: str) -> dict[str, Any]:
    table, warnings = context_split_table(df, pitcher, dimension)
    if table.empty:
        return {"dimension": dimension, "top": None, "warnings": warnings}
    row = table.iloc[0].to_dict()
    return {"dimension": dimension, "top": row, "warnings": warnings}


def run_decision_council(
    df: pd.DataFrame,
    pitcher: str,
    batter: str,
    balls: int = 0,
    strikes: int = 0,
    organization: dict | None = None,
) -> dict[str, Any]:
    """Run a small, auditable specialist council.

    The public implementation is deliberately a deterministic agentic workflow:
    specialist components call statistical tools, then a chief-strategy layer
    synthesizes their evidence. A production Team edition can replace individual
    specialists with Vertex AI ADK agents without changing the evidence contract.
    """
    organization = organization or {"display_name": "Demo Professional Club", "objective": "decision quality"}
    brief = build_brief(df, pitcher, batter, balls, strikes)
    starter, _ = starter_assessment(df, pitcher)
    adaptation = adaptation_signals(df, batter)
    adaptation_rows = adaptation.dropna(subset=["value_shift"]).sort_values("value_shift", ascending=False)
    context = [_top_context(df, pitcher, d) for d in ["home_away", "stand", "day_of_week", "days_rest"]]

    reports: list[SpecialistReport] = []
    plan = brief.get("plan_a")
    reports.append(
        SpecialistReport(
            "Pitching Strategy Agent",
            "matchup plan",
            (
                f"Primary supported scenario: {plan['pitch_family']} / {plan['zone_group']}"
                if plan else "No player-specific plan clears the evidence gate."
            ),
            (plan or {}).get("confidence", "insufficient"),
            {"brief": brief},
        )
    )
    reports.append(
        SpecialistReport(
            "Starter Pulse Agent",
            "recent form and sparse-history control",
            starter.summary,
            starter.evidence,
            starter.to_dict(),
        )
    )
    context_supported = [c for c in context if c.get("top")]
    reports.append(
        SpecialistReport(
            "Context Intelligence Agent",
            "time × space context",
            f"Evaluated {len(context_supported)} contextual dimensions with shrinkage and confounding warnings.",
            "moderate" if context_supported else "insufficient",
            {"dimensions": context},
        )
    )
    if adaptation_rows.empty:
        adaptation_finding = "No stable recent adaptation signal is available in the active data."
        adaptation_evidence = "insufficient"
        adaptation_payload: dict[str, Any] = {"signals": []}
    else:
        row = adaptation_rows.iloc[0]
        adaptation_finding = (
            f"Largest observed recent shift is versus {row['pitch_family']} "
            f"(value shift {row['value_shift']:+.3f}); treat as associative."
        )
        n = int(row.get("early_n", 0)) + int(row.get("recent_n", 0))
        adaptation_evidence = "moderate" if n >= 35 else "weak"
        adaptation_payload = {"signals": adaptation_rows.head(5).to_dict("records")}
    reports.append(
        SpecialistReport(
            "Opponent Adaptation Agent",
            "behavioral change detection",
            adaptation_finding,
            adaptation_evidence,
            adaptation_payload,
        )
    )

    evidence_order = {"strong": 3, "moderate": 2, "weak": 1, "insufficient": 0}
    scores = [evidence_order.get(r.evidence, 0) for r in reports]
    council_score = sum(scores) / max(1, len(scores))
    council_evidence = "strong" if council_score >= 2.5 else "moderate" if council_score >= 1.7 else "weak" if council_score >= 0.8 else "insufficient"
    veto = brief.get("abstain", False) or council_evidence == "insufficient"

    return {
        "organization": organization,
        "query_context": {"pitcher": pitcher, "batter": batter, "count": f"{balls}-{strikes}"},
        "specialists": [r.to_dict() for r in reports],
        "chief_strategy": {
            "objective": organization.get("objective"),
            "evidence": council_evidence,
            "decision_status": "human_review_required" if veto else "decision_brief_ready",
            "recommendation": brief,
            "principle": "Specialists advise; evidence can veto; the human owns the decision.",
        },
        "architecture_status": "deterministic public workflow; Vertex AI ADK multi-agent orchestration is the Team roadmap",
    }
