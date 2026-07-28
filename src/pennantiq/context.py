from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

import numpy as np
import pandas as pd

from .analytics import add_features, evidence_label


SEASON_PHASES = {
    3: "spring",
    4: "early",
    5: "early",
    6: "middle",
    7: "middle",
    8: "late",
    9: "late",
    10: "postseason",
    11: "postseason",
}


@dataclass(frozen=True)
class ContextWarning:
    code: str
    severity: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


def _time_bucket(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "unknown"
    try:
        hour = pd.to_datetime(str(value)).hour
    except Exception:
        try:
            hour = int(str(value).split(":", 1)[0])
        except Exception:
            return "unknown"
    if hour < 12:
        return "morning"
    if hour < 17:
        return "afternoon"
    return "night"


def enrich_context(df: pd.DataFrame) -> pd.DataFrame:
    """Create explainable time, space and competition context features.

    The function only derives fields. It does not claim that any split is causal.
    """
    x = add_features(df)
    x["game_date"] = pd.to_datetime(x["game_date"], errors="coerce")
    x["day_of_week"] = x["game_date"].dt.day_name()
    x["month"] = x["game_date"].dt.month
    x["season_phase"] = x["month"].map(SEASON_PHASES).fillna("unknown")
    x["is_weekend"] = x["day_of_week"].isin(["Saturday", "Sunday"])

    if "home_away" not in x:
        if "is_home" in x:
            x["home_away"] = np.where(x["is_home"].fillna(False), "home", "away")
        else:
            x["home_away"] = "unknown"
    x["home_away"] = x["home_away"].fillna("unknown").astype(str).str.lower()

    if "day_night" not in x:
        if "game_time_local" in x:
            x["day_night"] = x["game_time_local"].map(_time_bucket).replace(
                {"morning": "day", "afternoon": "day"}
            )
        else:
            x["day_night"] = "unknown"

    if "game_time_bucket" not in x:
        x["game_time_bucket"] = (
            x["game_time_local"].map(_time_bucket)
            if "game_time_local" in x
            else "unknown"
        )

    if "venue" not in x:
        x["venue"] = "unknown"
    if "opponent_team" not in x:
        if {"home_team", "away_team", "is_home"}.issubset(x.columns):
            x["opponent_team"] = np.where(x["is_home"], x["away_team"], x["home_team"])
        else:
            x["opponent_team"] = "unknown"

    # Derive days of rest and appearance number from unique pitcher-game dates.
    game_keys = ["pitcher_name", "game_date"]
    appearances = (
        x.dropna(subset=["pitcher_name", "game_date"])[game_keys]
        .drop_duplicates()
        .sort_values(game_keys)
    )
    appearances["days_rest_derived"] = (
        appearances.groupby("pitcher_name")["game_date"].diff().dt.days
    )
    appearances["appearance_number"] = appearances.groupby("pitcher_name").cumcount() + 1
    x = x.merge(appearances, on=game_keys, how="left")

    if "pitcher_days_since_prev_game" in x:
        supplied = pd.to_numeric(x["pitcher_days_since_prev_game"], errors="coerce")
        x["days_rest"] = supplied.fillna(x["days_rest_derived"])
    else:
        x["days_rest"] = x["days_rest_derived"]

    if "starter_flag" not in x:
        # A transparent heuristic for generic pitch data. Enterprise mode should
        # replace it with roster/game-role data.
        counts = x.groupby(game_keys)["pitcher_name"].transform("size")
        x["starter_flag"] = counts >= 40

    if "n_thruorder_pitcher" not in x:
        if "at_bat_number" in x:
            x["n_thruorder_pitcher"] = (
                pd.to_numeric(x["at_bat_number"], errors="coerce").fillna(1) // 9 + 1
            ).clip(1, 5)
        else:
            x["n_thruorder_pitcher"] = np.nan

    numeric_defaults = {
        "temperature": np.nan,
        "wind_speed": np.nan,
        "elevation_ft": np.nan,
        "inning": np.nan,
    }
    for col, default in numeric_defaults.items():
        if col not in x:
            x[col] = default
        x[col] = pd.to_numeric(x[col], errors="coerce")

    for col in ["roof", "wind_direction"]:
        if col not in x:
            x[col] = "unknown"
        x[col] = x[col].fillna("unknown").astype(str)

    return x


def context_warnings(
    table: pd.DataFrame,
    dimension: str,
    min_sample: int = 30,
    max_categories: int = 12,
) -> list[dict]:
    warnings: list[ContextWarning] = []
    if table.empty:
        warnings.append(
            ContextWarning("no_data", "high", f"No usable records for {dimension}.")
        )
        return [w.to_dict() for w in warnings]
    small = int((table["n"] < min_sample).sum())
    if small:
        warnings.append(
            ContextWarning(
                "small_samples",
                "medium",
                f"{small} {dimension} groups have fewer than {min_sample} pitches; use them as exploratory signals only.",
            )
        )
    if len(table) > max_categories:
        warnings.append(
            ContextWarning(
                "multiple_comparisons",
                "medium",
                "Many splits are being compared. Apparent winners may be noise unless they remain stable out of sample.",
            )
        )
    warnings.append(
        ContextWarning(
            "confounding",
            "medium",
            f"{dimension} is associative. Opponent quality, rest, park, weather and role can confound the split.",
        )
    )
    return [w.to_dict() for w in warnings]


def context_split_table(
    df: pd.DataFrame,
    pitcher_name: str,
    dimension: str,
    as_of: str | pd.Timestamp | None = None,
    min_sample: int = 15,
    prior_strength: float = 60.0,
) -> tuple[pd.DataFrame, list[dict]]:
    x = enrich_context(df)
    if as_of is not None:
        x = x[x["game_date"] < pd.Timestamp(as_of)]
    x = x[x["pitcher_name"] == pitcher_name]
    if dimension not in x.columns:
        return pd.DataFrame(), [
            ContextWarning("missing_dimension", "high", f"Column {dimension} is unavailable.").to_dict()
        ]
    x = x.dropna(subset=[dimension])
    if x.empty:
        return pd.DataFrame(), context_warnings(pd.DataFrame(), dimension, min_sample)

    prior = float(x["defensive_value"].mean())
    table = (
        x.groupby(dimension, dropna=False)
        .agg(
            n=("defensive_value", "size"),
            games=("game_date", "nunique"),
            avg_velocity=("release_speed", "mean"),
            whiff_rate=("is_whiff", "mean"),
            hard_contact_rate=("is_hard_contact", "mean"),
            observed_value=("defensive_value", "mean"),
        )
        .reset_index()
    )
    table["posterior_value"] = (
        table["n"] * table["observed_value"] + prior_strength * prior
    ) / (table["n"] + prior_strength)
    table["evidence"] = table["n"].map(lambda n: evidence_label(int(n)))
    table["sample_share"] = table["n"] / max(1, table["n"].sum())
    table["exploratory_only"] = table["n"] < min_sample
    table = table.sort_values(["posterior_value", "n"], ascending=False).reset_index(drop=True)
    return table, context_warnings(table, dimension, min_sample)


def context_matrix(
    df: pd.DataFrame,
    pitcher_name: str,
    row_dimension: str = "home_away",
    column_dimension: str = "stand",
    as_of: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    x = enrich_context(df)
    if as_of is not None:
        x = x[x["game_date"] < pd.Timestamp(as_of)]
    x = x[x["pitcher_name"] == pitcher_name]
    if x.empty or row_dimension not in x or column_dimension not in x:
        return pd.DataFrame()
    grouped = (
        x.groupby([row_dimension, column_dimension], dropna=False)
        .agg(n=("defensive_value", "size"), value=("defensive_value", "mean"))
        .reset_index()
    )
    grouped.loc[grouped["n"] < 15, "value"] = np.nan
    return grouped.pivot(index=row_dimension, columns=column_dimension, values="value")


def available_dimensions(df: pd.DataFrame) -> list[str]:
    x = enrich_context(df.head(min(len(df), 2000)))
    candidates: Iterable[str] = [
        "day_of_week",
        "home_away",
        "stand",
        "p_throws",
        "day_night",
        "game_time_bucket",
        "season_phase",
        "venue",
        "opponent_team",
        "days_rest",
        "n_thruorder_pitcher",
        "roof",
    ]
    return [col for col in candidates if col in x and x[col].notna().any()]
