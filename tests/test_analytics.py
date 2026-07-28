from src.pennantiq.data import load_pitches
from src.pennantiq.analytics import build_brief, adaptation_signals

def test_brief_has_plans():
    df=load_pitches(); result=build_brief(df,df.pitcher_name.iloc[0],df.batter_name.iloc[0],0,0)
    assert set(["plan_a","plan_b","avoid","abstain"]).issubset(result)

def test_adaptation_returns_table():
    df=load_pitches(); out=adaptation_signals(df,df.batter_name.iloc[0]); assert not out.empty


def test_evidence_thresholds_are_conservative():
    from src.pennantiq.analytics import evidence_label

    assert evidence_label(14) == "insufficient"
    assert evidence_label(15) == "weak"
    assert evidence_label(35) == "moderate"
    assert evidence_label(75) == "strong"
