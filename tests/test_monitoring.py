from types import SimpleNamespace

from src.pennantiq import monitoring


def test_monitoring_feedback_round_trip(tmp_path, monkeypatch):
    db_path = tmp_path / "monitoring.sqlite"
    fake_settings = SimpleNamespace(
        monitoring_db=db_path,
        resolve=lambda path: path,
    )
    monkeypatch.setattr(monitoring, "settings", fake_settings)

    row_id = monitoring.log_interaction(
        query="test query",
        intent="matchup",
        provider="deterministic",
        latency_ms=12.5,
        confidence="moderate",
        grounded=True,
        abstained=False,
        metadata={"test": True},
    )
    monitoring.record_feedback(row_id, 1)
    frame = monitoring.interactions()

    assert len(frame) == 1
    assert int(frame.loc[0, "feedback"]) == 1
    assert int(frame.loc[0, "grounded"]) == 1
