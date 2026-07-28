from src.pennantiq.council import run_decision_council
from src.pennantiq.data import load_pitches


def test_decision_council_is_auditable():
    df = load_pitches()
    pitcher = df.pitcher_name.dropna().iloc[0]
    batter = df.batter_name.dropna().iloc[0]
    result = run_decision_council(df, pitcher, batter, 0, 0)
    assert len(result["specialists"]) == 4
    assert result["chief_strategy"]["decision_status"] in {"human_review_required", "decision_brief_ready"}
    assert "recommendation" in result["chief_strategy"]
