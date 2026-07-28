from __future__ import annotations
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd

from .config import settings

REQUIRED = {
    "game_date", "pitcher_name", "batter_name", "pitch_type", "pitch_name", "pitch_family",
    "zone_group", "balls", "strikes", "stand", "p_throws", "release_speed", "plate_x", "plate_z"
}

PITCH_FAMILIES = {
    "FF": "fastball", "SI": "fastball", "FC": "fastball", "FA": "fastball",
    "SL": "breaking", "ST": "breaking", "CU": "breaking", "KC": "breaking", "SV": "breaking",
    "CH": "offspeed", "FS": "offspeed", "FO": "offspeed", "SC": "offspeed",
    "KN": "other", "EP": "other", "PO": "other", "IN": "other",
}


def _zone_group(frame: pd.DataFrame) -> pd.Series:
    x = pd.to_numeric(frame.get("plate_x"), errors="coerce")
    z = pd.to_numeric(frame.get("plate_z"), errors="coerce")
    top_source = frame["sz_top"] if "sz_top" in frame else pd.Series(3.5, index=frame.index)
    bot_source = frame["sz_bot"] if "sz_bot" in frame else pd.Series(1.5, index=frame.index)
    top = pd.to_numeric(top_source, errors="coerce").fillna(3.5)
    bot = pd.to_numeric(bot_source, errors="coerce").fillna(1.5)
    height = (top - bot).clip(lower=1.5)
    center = bot + height / 2
    horizontal = x.abs()
    vertical_center = (z - center).abs() / (height / 2)

    result = pd.Series("waste", index=frame.index, dtype="object")
    result[(horizontal <= 0.55) & (vertical_center <= 0.45)] = "heart"
    result[(horizontal <= 0.95) & (z >= bot - 0.15) & (z <= top + 0.15) & (result == "waste")] = "shadow"
    result[(horizontal <= 1.45) & (z >= bot - 0.65) & (z <= top + 0.65) & (result == "waste")] = "chase"
    return result


def normalize_statcast_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize a Baseball Savant/pybaseball frame into PennantIQ's public schema.

    Player names may be unavailable for the batter in generic Statcast downloads;
    in that case a stable MLB-ID label is used rather than inventing a name.
    """
    df = raw.copy()
    rename = {
        "delta_run_exp": "delta_pitcher_run_exp_raw",
        "estimated_woba_using_speedangle": "estimated_woba",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df})

    if "pitcher_name" not in df:
        if "player_name" in df:
            df["pitcher_name"] = df["player_name"].fillna("")
        elif "pitcher" in df:
            df["pitcher_name"] = "Pitcher " + df["pitcher"].astype("Int64").astype(str)
    if "batter_name" not in df:
        if "batter" in df:
            df["batter_name"] = "Batter " + df["batter"].astype("Int64").astype(str)
        else:
            df["batter_name"] = "Unknown batter"

    if "pitch_name" not in df:
        df["pitch_name"] = df.get("pitch_type", "Unknown")
    df["pitch_family"] = df.get("pitch_type", pd.Series("", index=df.index)).map(PITCH_FAMILIES).fillna("other")
    if "zone_group" not in df:
        df["zone_group"] = _zone_group(df)

    if "delta_pitcher_run_exp" not in df:
        if "delta_pitcher_run_exp_raw" in df:
            # Statcast delta_run_exp is offense-oriented. Invert it for pitcher value.
            df["delta_pitcher_run_exp"] = -pd.to_numeric(df["delta_pitcher_run_exp_raw"], errors="coerce")
        else:
            df["delta_pitcher_run_exp"] = np.nan

    inning_side = df.get("inning_topbot", pd.Series("", index=df.index)).astype(str).str.lower()
    if "is_home" not in df:
        df["is_home"] = inning_side.eq("top")
    if "pitcher_team" not in df and {"home_team", "away_team"}.issubset(df.columns):
        df["pitcher_team"] = np.where(df["is_home"], df["home_team"], df["away_team"])
        df["opponent_team"] = np.where(df["is_home"], df["away_team"], df["home_team"])
    df["home_away"] = np.where(df.get("is_home", False), "home", "away")

    defaults = {
        "game_pk": np.arange(len(df)),
        "description": "",
        "events": "",
        "launch_speed": np.nan,
        "stand": "unknown",
        "p_throws": "unknown",
        "balls": 0,
        "strikes": 0,
        "release_speed": np.nan,
        "plate_x": np.nan,
        "plate_z": np.nan,
        "data_provenance": "statcast_user_download",
    }
    for col, default in defaults.items():
        if col not in df:
            df[col] = default
    df["data_provenance"] = df["data_provenance"].fillna("statcast_user_download")
    return df


def _validate(df: pd.DataFrame, source: str) -> pd.DataFrame:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Dataset {source} is missing required columns: {sorted(missing)}")
    df = df.copy()
    df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
    numeric = [
        "balls", "strikes", "release_speed", "plate_x", "plate_z", "launch_speed",
        "delta_pitcher_run_exp", "temperature", "wind_speed", "elevation_ft", "inning",
        "at_bat_number", "pitch_number", "pitcher_days_since_prev_game", "n_thruorder_pitcher",
    ]
    for col in numeric:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if df["game_date"].isna().all():
        raise ValueError(f"Dataset {source} contains no valid game_date values.")
    return df.sort_values(["game_date", "game_pk"] if "game_pk" in df else ["game_date"]).reset_index(drop=True)


def load_pitches(path: str | Path | None = None) -> pd.DataFrame:
    source = settings.resolve(Path(path)) if path else settings.resolve(settings.data_path)
    if not source.exists():
        raise FileNotFoundError(
            f"Pitch dataset not found: {source}. Run `make demo-data`, use the upload control, or set PENNANTIQ_DATA_PATH."
        )
    frame = pd.read_csv(source, low_memory=False)
    if not REQUIRED.issubset(frame.columns):
        frame = normalize_statcast_dataframe(frame)
    return _validate(frame, str(source))


def load_uploaded_csv(uploaded: BinaryIO | bytes) -> pd.DataFrame:
    payload = uploaded if isinstance(uploaded, bytes) else uploaded.read()
    frame = pd.read_csv(BytesIO(payload), low_memory=False)
    if not REQUIRED.issubset(frame.columns):
        frame = normalize_statcast_dataframe(frame)
    return _validate(frame, "uploaded CSV")


def load_recent_results(path: str | Path | None = None) -> pd.DataFrame:
    source = settings.resolve(Path(path)) if path else settings.resolve(settings.results_path)
    if not source.exists():
        return pd.DataFrame()
    frame = pd.read_csv(source)
    frame["game_date"] = pd.to_datetime(frame["game_date"], errors="coerce")
    return frame.sort_values("game_date").reset_index(drop=True)


def dataset_profile(df: pd.DataFrame) -> dict:
    provenance = df.get("data_provenance", pd.Series(["unknown"])).dropna().astype(str).unique().tolist()
    missing_context = [
        col for col in ["venue", "home_away", "temperature", "wind_speed", "starter_flag"]
        if col not in df or df[col].isna().all()
    ]
    return {
        "rows": int(len(df)),
        "start": str(df.game_date.min().date()) if len(df) else None,
        "end": str(df.game_date.max().date()) if len(df) else None,
        "pitchers": int(df.pitcher_name.nunique()),
        "batters": int(df.batter_name.nunique()),
        "games": int(df.game_pk.nunique()) if "game_pk" in df else int(df.game_date.nunique()),
        "provenance": sorted(provenance),
        "missing_context": missing_context,
        "real_data": any("synthetic" not in value.lower() for value in provenance),
    }
