from __future__ import annotations

import numpy as np
import pandas as pd

from .analytics import add_features, evidence_label


def _recommendation_tables(history: pd.DataFrame) -> tuple[dict, dict]:
    """Build exact and fallback recommendation lookups once per evaluation day."""
    prior = float(history["defensive_value"].mean()) if len(history) else 0.0
    prior_strength = 20.0

    def build(keys: list[str]) -> dict:
        grouped = (
            history.groupby(keys + ["pitch_family", "zone_group"], dropna=False)
            .agg(n=("defensive_value", "size"), mean_value=("defensive_value", "mean"))
            .reset_index()
        )
        grouped["posterior_value"] = (
            grouped["n"] * grouped["mean_value"] + prior_strength * prior
        ) / (grouped["n"] + prior_strength)
        grouped["confidence"] = grouped["n"].map(lambda n: evidence_label(int(n)))
        grouped = grouped.sort_values(
            keys + ["posterior_value", "n"], ascending=[True] * len(keys) + [False, False]
        )
        best = grouped.groupby(keys, dropna=False, as_index=False).head(1)
        output = {}
        for _, row in best.iterrows():
            key = tuple(row[k] for k in keys)
            output[key] = {
                "pitch_family": row["pitch_family"],
                "zone_group": row["zone_group"],
                "n": int(row["n"]),
                "confidence": row["confidence"],
                "posterior_value": float(row["posterior_value"]),
            }
        return output

    exact = build(["batter_name", "stand", "balls", "strikes"])
    fallback = build(["stand", "balls", "strikes"])
    return exact, fallback


def run_shadow_mode(
    df: pd.DataFrame,
    warmup_days: int = 25,
    min_history: int = 30,
) -> tuple[pd.DataFrame, dict]:
    """Chronological shadow backtest with no future-data leakage.

    For each evaluation date, lookup tables are generated only from earlier dates.
    The comparison between followed and non-followed recommendations is associative,
    not causal, because historical pitch selection was not randomized.
    """
    x = add_features(df).dropna(subset=["game_date"]).sort_values("game_date")
    x["evaluation_day"] = x["game_date"].dt.normalize()
    dates = sorted(x["evaluation_day"].unique())
    if len(dates) <= warmup_days:
        warmup_days = max(1, len(dates) // 2)

    records: list[dict] = []
    for day in dates[warmup_days:]:
        history = x[x["evaluation_day"] < day]
        today = x[x["evaluation_day"] == day]
        if len(history) < min_history:
            continue

        exact, fallback = _recommendation_tables(history)
        for _, row in today.iterrows():
            exact_key = (
                row["batter_name"],
                row["stand"],
                int(row["balls"]),
                int(row["strikes"]),
            )
            fallback_key = (row["stand"], int(row["balls"]), int(row["strikes"]))
            recommendation = exact.get(exact_key) or fallback.get(fallback_key)
            if not recommendation:
                continue

            records.append(
                {
                    "game_date": str(pd.Timestamp(day).date()),
                    "pitcher_name": row["pitcher_name"],
                    "batter_name": row["batter_name"],
                    "count": f"{int(row['balls'])}-{int(row['strikes'])}",
                    "recommended_family": recommendation["pitch_family"],
                    "recommended_zone": recommendation["zone_group"],
                    "evidence_n": recommendation["n"],
                    "confidence": recommendation["confidence"],
                    "observed_family": row["pitch_family"],
                    "observed_zone": row["zone_group"],
                    "observed_value": float(row["defensive_value"]),
                    "recommendation_followed": int(
                        recommendation["pitch_family"] == row["pitch_family"]
                        and recommendation["zone_group"] == row["zone_group"]
                    ),
                }
            )

    output = pd.DataFrame(records)
    if output.empty:
        return output, {
            "rows": 0,
            "coverage": 0.0,
            "followed_rate": 0.0,
            "observed_value_when_followed": None,
            "observed_value_when_not_followed": None,
            "warning": "No evaluable rows were available.",
        }

    strong = output[output["confidence"].isin(["moderate", "strong"])]
    followed = output["recommendation_followed"] == 1
    not_followed = ~followed
    metrics = {
        "rows": int(len(output)),
        "coverage": float(len(strong) / len(output)),
        "followed_rate": float(output["recommendation_followed"].mean()),
        "observed_value_when_followed": (
            float(output.loc[followed, "observed_value"].mean()) if followed.any() else None
        ),
        "observed_value_when_not_followed": (
            float(output.loc[not_followed, "observed_value"].mean())
            if not_followed.any()
            else None
        ),
        "warning": (
            "Observed-value comparisons are associative, not causal. "
            "Selection effects and unobserved game context remain."
        ),
    }
    return output, metrics
