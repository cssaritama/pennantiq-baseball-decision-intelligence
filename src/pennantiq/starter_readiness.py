from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from .analytics import evidence_label
from .context import enrich_context


@dataclass(frozen=True)
class StarterAssessment:
    pitcher: str
    mode: str
    appearances: int
    pitches: int
    evidence: str
    form_index: float | None
    velocity_delta: float | None
    whiff_delta: float | None
    hard_contact_delta: float | None
    days_rest: float | None
    summary: str
    limitations: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def game_level_starts(df: pd.DataFrame, pitcher_name: str) -> pd.DataFrame:
    x = enrich_context(df)
    x = x[x["pitcher_name"] == pitcher_name].copy()
    if x.empty:
        return pd.DataFrame()

    mix = (
        x.groupby(["game_date", "pitch_family"]).size().rename("family_n").reset_index()
    )
    mix["family_share"] = mix["family_n"] / mix.groupby("game_date")["family_n"].transform("sum")
    entropy = (
        mix.assign(term=lambda d: -d["family_share"] * np.log2(d["family_share"].clip(lower=1e-9)))
        .groupby("game_date")["term"]
        .sum()
        .rename("pitch_mix_entropy")
    )

    starts = (
        x.groupby("game_date")
        .agg(
            pitches=("pitcher_name", "size"),
            avg_velocity=("release_speed", "mean"),
            max_velocity=("release_speed", "max"),
            whiff_rate=("is_whiff", "mean"),
            hard_contact_rate=("is_hard_contact", "mean"),
            defensive_value=("defensive_value", "mean"),
            home_away=("home_away", "first"),
            opponent_team=("opponent_team", "first"),
            venue=("venue", "first"),
            days_rest=("days_rest", "first"),
            temperature=("temperature", "first"),
            starter_flag=("starter_flag", "max"),
        )
        .join(entropy)
        .reset_index()
        .sort_values("game_date")
    )
    starts["appearance_number"] = np.arange(1, len(starts) + 1)
    return starts


def _standardized_delta(recent: pd.Series, baseline: pd.Series) -> float:
    if recent.dropna().empty or baseline.dropna().empty:
        return 0.0
    std = float(baseline.std(ddof=0))
    if not np.isfinite(std) or std < 1e-6:
        std = max(abs(float(baseline.mean())) * 0.1, 0.05)
    return float((recent.mean() - baseline.mean()) / std)


def starter_assessment(
    df: pd.DataFrame,
    pitcher_name: str,
    as_of: str | pd.Timestamp | None = None,
    last_n: int = 5,
) -> tuple[StarterAssessment, pd.DataFrame]:
    starts = game_level_starts(df, pitcher_name)
    if as_of is not None:
        starts = starts[starts["game_date"] < pd.Timestamp(as_of)]
    appearances = int(len(starts))
    pitches = int(starts["pitches"].sum()) if appearances else 0

    if appearances == 0:
        assessment = StarterAssessment(
            pitcher_name,
            "unseen",
            0,
            0,
            "insufficient",
            None,
            None,
            None,
            None,
            None,
            "No MLB-level pitch history is available in the selected dataset.",
            [
                "Use a licensed minor-league/scouting connector or peer priors.",
                "Do not manufacture a player-specific recommendation.",
                "Require human scouting review before a game plan is approved.",
            ],
        )
        return assessment, starts

    evidence = evidence_label(pitches)
    recent = starts.tail(last_n)
    baseline = starts.iloc[:-last_n] if appearances > last_n else starts
    velocity_delta = float(recent["avg_velocity"].mean() - baseline["avg_velocity"].mean())
    whiff_delta = float(recent["whiff_rate"].mean() - baseline["whiff_rate"].mean())
    hard_delta = float(recent["hard_contact_rate"].mean() - baseline["hard_contact_rate"].mean())

    z_velocity = _standardized_delta(recent["avg_velocity"], baseline["avg_velocity"])
    z_whiff = _standardized_delta(recent["whiff_rate"], baseline["whiff_rate"])
    # Lower hard-contact is better, therefore the sign is inverted.
    z_hard = -_standardized_delta(recent["hard_contact_rate"], baseline["hard_contact_rate"])
    z_value = _standardized_delta(recent["defensive_value"], baseline["defensive_value"])
    form_index = float(np.clip(50 + 8 * (0.28*z_velocity + 0.28*z_whiff + 0.22*z_hard + 0.22*z_value), 0, 100))
    rest = recent["days_rest"].dropna()
    days_rest = float(rest.iloc[-1]) if not rest.empty else None

    sparse = appearances < 3 or pitches < 120
    mode = "debutant_or_sparse" if sparse else "observed_form"
    limitations = [
        "Form Index is descriptive and is not an injury, health or readiness diagnosis.",
        "Changes can be caused by opponent quality, role, park, weather or tracking variation.",
    ]
    if sparse:
        limitations.insert(0, "Player-specific evidence is sparse; shrink strongly toward peer and league priors.")
    assessment = StarterAssessment(
        pitcher_name,
        mode,
        appearances,
        pitches,
        evidence,
        round(form_index, 1),
        round(velocity_delta, 2),
        round(whiff_delta, 4),
        round(hard_delta, 4),
        days_rest,
        (
            f"Recent {len(recent)}-appearance signal: velocity {velocity_delta:+.2f} mph, "
            f"whiff {whiff_delta:+.1%}, hard contact {hard_delta:+.1%}."
        ),
        limitations,
    )
    return assessment, starts


def debutant_protocol(df: pd.DataFrame, pitcher_name: str, throws: str | None = None) -> dict:
    assessment, starts = starter_assessment(df, pitcher_name)
    if assessment.mode not in {"unseen", "debutant_or_sparse"}:
        return {
            "activated": False,
            "reason": "Sufficient observed history for the selected public prototype policy.",
            "assessment": assessment.to_dict(),
        }

    x = enrich_context(df)
    peer = x
    if throws and "p_throws" in peer:
        peer = peer[peer["p_throws"] == throws]
    peer_summary = {
        "pitches": int(len(peer)),
        "avg_velocity": round(float(peer["release_speed"].mean()), 2) if len(peer) else None,
        "whiff_rate": round(float(peer["is_whiff"].mean()), 4) if len(peer) else None,
        "hard_contact_rate": round(float(peer["is_hard_contact"].mean()), 4) if len(peer) else None,
    }
    return {
        "activated": True,
        "reason": "No or sparse player-specific MLB history in the active dataset.",
        "approved_evidence": [
            "verified handedness and role",
            "licensed minor-league pitch tracking when available",
            "arsenal and release-trait peer group",
            "human scouting report",
            "opponent performance against comparable pitch shapes",
        ],
        "forbidden_shortcuts": [
            "treating a tiny debut sample as stable",
            "inventing pitch quality or command",
            "turning peer averages into player facts",
        ],
        "decision_policy": "Return a conservative peer-informed plan, label uncertainty high and require human approval.",
        "peer_prior": peer_summary,
        "assessment": assessment.to_dict(),
        "starts": int(len(starts)),
    }
