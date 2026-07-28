from __future__ import annotations
from dataclasses import dataclass, asdict
import math
import pandas as pd
import numpy as np

@dataclass
class Candidate:
    pitch_family: str
    zone_group: str
    n: int
    mean_value: float
    posterior_value: float
    whiff_rate: float
    hard_contact_rate: float
    confidence: str

    def to_dict(self):
        return asdict(self)

def _defensive_value(df: pd.DataFrame) -> pd.Series:
    if "delta_pitcher_run_exp" in df and df["delta_pitcher_run_exp"].notna().any():
        return df["delta_pitcher_run_exp"].fillna(0.0).clip(-2,2)
    desc = df.get("description", pd.Series("", index=df.index)).fillna("").astype(str)
    events = df.get("events", pd.Series("", index=df.index)).fillna("").astype(str)
    value = pd.Series(0.0, index=df.index)
    value[desc.str.contains("swinging_strike|called_strike", regex=True)] = 0.08
    value[events.str.contains("field_out|strikeout", regex=True)] = 0.15
    value[events.str.contains("single|walk", regex=True)] = -0.35
    value[events.str.contains("double|triple", regex=True)] = -0.65
    value[events.str.contains("home_run", regex=True)] = -1.4
    return value

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    x=df.copy()
    x["defensive_value"]=_defensive_value(x)
    x["count_bucket"]=x["balls"].fillna(0).astype(int).astype(str)+"-"+x["strikes"].fillna(0).astype(int).astype(str)
    desc=x.get("description",pd.Series("",index=x.index)).fillna("").astype(str)
    x["is_whiff"]=desc.str.contains("swinging_strike").astype(int)
    ls=x.get("launch_speed",pd.Series(np.nan,index=x.index))
    x["is_hard_contact"]=(pd.to_numeric(ls,errors="coerce")>=95).fillna(False).astype(int)
    return x

def evidence_label(n: int, stability: float = 1.0) -> str:
    effective=n*max(0.25,min(1.0,stability))
    if effective >= 75: return "strong"
    if effective >= 35: return "moderate"
    if effective >= 15: return "weak"
    return "insufficient"

def rank_candidates(df: pd.DataFrame, batter_name: str, stand: str | None=None, balls: int | None=None, strikes: int | None=None, min_n: int=8) -> list[Candidate]:
    x=add_features(df)
    subset=x[x.batter_name==batter_name]
    if stand: subset=subset[subset.stand==stand]
    if balls is not None: subset=subset[subset.balls==balls]
    if strikes is not None: subset=subset[subset.strikes==strikes]
    if subset.empty:
        subset=x[x.stand==stand] if stand else x
    prior=float(x.defensive_value.mean()) if len(x) else 0.0
    strength=20
    result=[]
    for (pf,z),g in subset.groupby(["pitch_family","zone_group"]):
        n=len(g); mean=float(g.defensive_value.mean())
        post=(n*mean+strength*prior)/(n+strength)
        result.append(Candidate(pf,z,n,mean,post,float(g.is_whiff.mean()),float(g.is_hard_contact.mean()),evidence_label(n)))
    result.sort(key=lambda c:(c.posterior_value, math.log1p(c.n)), reverse=True)
    return result

def build_brief(df: pd.DataFrame, pitcher_name: str, batter_name: str, balls: int=0, strikes: int=0) -> dict:
    x=df[df.pitcher_name==pitcher_name]
    if x.empty: x=df
    stand=(df.loc[df.batter_name==batter_name,"stand"].mode().iloc[0] if not df.loc[df.batter_name==batter_name].empty else None)
    ranked=rank_candidates(x,batter_name,stand,balls,strikes)
    viable=[c for c in ranked if c.n>=8]
    plan_a=viable[0] if viable else (ranked[0] if ranked else None)
    plan_b=viable[1] if len(viable)>1 else (ranked[1] if len(ranked)>1 else None)
    avoid=ranked[-1] if ranked else None
    return {
        "pitcher":pitcher_name,"batter":batter_name,"count":f"{balls}-{strikes}","stand":stand,
        "plan_a":plan_a.to_dict() if plan_a else None,
        "plan_b":plan_b.to_dict() if plan_b else None,
        "avoid":avoid.to_dict() if avoid else None,
        "abstain": not plan_a or plan_a.confidence=="insufficient",
        "method":"Empirical-Bayes scenario ranking; descriptive decision support, not a causal counterfactual.",
    }

def adaptation_signals(df: pd.DataFrame, batter_name: str, split_date=None) -> pd.DataFrame:
    x=add_features(df[df.batter_name==batter_name])
    if x.empty: return pd.DataFrame()
    if split_date is None:
        split_date=x.game_date.quantile(.65)
    early=x[x.game_date<=split_date]; recent=x[x.game_date>split_date]
    records=[]
    for pf in sorted(x.pitch_family.dropna().unique()):
        a=early[early.pitch_family==pf]; b=recent[recent.pitch_family==pf]
        records.append({"pitch_family":pf,"early_n":len(a),"recent_n":len(b),
                        "early_value":a.defensive_value.mean() if len(a) else np.nan,
                        "recent_value":b.defensive_value.mean() if len(b) else np.nan,
                        "value_shift":(b.defensive_value.mean()-a.defensive_value.mean()) if len(a) and len(b) else np.nan,
                        "early_whiff":a.is_whiff.mean() if len(a) else np.nan,
                        "recent_whiff":b.is_whiff.mean() if len(b) else np.nan})
    return pd.DataFrame(records)
