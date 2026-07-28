from src.pennantiq.data import load_recent_results


def test_frozen_real_snapshot_is_available():
    frame = load_recent_results()
    assert {"NYY", "NYM"}.issubset(set(frame.team))
    assert frame.status.eq("final").all()
