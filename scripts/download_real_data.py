#!/usr/bin/env python3
"""Download real Statcast data into PennantIQ's normalized schema.

Adapter: Fungo 2.x, which exposes typed helpers for Baseball Savant searches.
The user is responsible for reviewing and accepting source terms before use.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd

def zone_group(row):
    x,z=row.get("plate_x"),row.get("plate_z")
    if pd.isna(x) or pd.isna(z): return "unknown"
    ax=abs(float(x)); z=float(z)
    if ax<=.55 and 2.0<=z<=3.1: return "heart"
    if ax<=.95 and 1.5<=z<=3.5: return "shadow"
    if ax<=1.45 and 1.0<=z<=4.0: return "chase"
    return "waste"

def normalize(df):
    df=df.copy()
    if "player_name" in df and "pitcher_name" not in df: df["pitcher_name"]=df["player_name"]
    if "batter_name" not in df:
        batter_ids = pd.to_numeric(df.get("batter", pd.Series(index=df.index)), errors="coerce")
        df["batter_name"] = batter_ids.map(lambda value: f"Batter {int(value)}" if pd.notna(value) else "Unknown batter")
    family={"FF":"fastball","SI":"fastball","FC":"fastball","SL":"breaking","CU":"breaking","KC":"breaking","ST":"breaking","CH":"offspeed","FS":"offspeed","FO":"offspeed","SC":"offspeed"}
    df["pitch_family"]=df.get("pitch_type",pd.Series(index=df.index)).map(family).fillna("other")
    df["zone_group"]=df.apply(zone_group,axis=1)
    if "delta_pitcher_run_exp" not in df:
        df["delta_pitcher_run_exp"]=-pd.to_numeric(df.get("delta_run_exp",0),errors="coerce").fillna(0)
    df["data_provenance"]="real_statcast_live"
    needed=["game_date","game_pk","pitcher_name","batter_name","pitcher","batter","pitch_type","pitch_name","pitch_family","zone_group","balls","strikes","stand","p_throws","release_speed","plate_x","plate_z","description","events","launch_speed","delta_pitcher_run_exp","data_provenance"]
    for c in needed:
        if c not in df: df[c]=None
    return df[needed]

def fetch(start: str, end: str, team: str | None = None) -> pd.DataFrame:
    try:
        from fungo.statcast import search_pitches, search_team
    except ImportError as exc:
        raise RuntimeError(
            "Live mode requires requirements-live.txt and Python 3.12+. "
            "Install it with: pip install -r requirements-live.txt"
        ) from exc

    try:
        rows = (
            search_team(team, start_date=start, end_date=end)
            if team
            else search_pitches(start_date=start, end_date=end)
        )
    except Exception as exc:
        raise RuntimeError(
            "The live Statcast request failed. Verify connectivity, date range, "
            "team abbreviation, and the current source terms before retrying."
        ) from exc
    return pd.DataFrame(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--start",required=True); ap.add_argument("--end",required=True); ap.add_argument("--team"); ap.add_argument("--output",default="data/real/statcast_live.csv")
    a=ap.parse_args(); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    df=normalize(fetch(a.start,a.end,a.team)); df.to_csv(out,index=False); print(f"Saved {len(df):,} rows to {out}")
if __name__=="__main__": main()
