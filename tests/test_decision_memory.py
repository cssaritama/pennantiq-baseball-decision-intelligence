from pathlib import Path

from src.pennantiq import decision_memory


def test_decision_journal_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_memory, "_path", lambda: tmp_path / "journal.sqlite")
    row_id = decision_memory.log_decision(
        "pregame_matchup", "Use Plan A", "Evidence supports it", "moderate"
    )
    assert row_id == 1
    decision_memory.close_decision(row_id, {"result": "observed"}, "Review sample size")
    rows = decision_memory.decisions()
    assert rows.iloc[0]["status"] == "closed"
