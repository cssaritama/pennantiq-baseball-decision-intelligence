from src.pennantiq.agent import deterministic_answer
from src.pennantiq.data import load_pitches


def test_agent_returns_evidence_and_cautious_language():
    df = load_pitches()
    result = deterministic_answer(
        df,
        df.pitcher_name.iloc[0],
        df.batter_name.iloc[0],
        query="Build an evidence-backed plan and explain the limitations.",
    )
    assert result["sources"]
    assert result["provider"] == "deterministic"
    text = result["answer"].lower()
    assert "guarantee" in text or "insufficient evidence" in text
