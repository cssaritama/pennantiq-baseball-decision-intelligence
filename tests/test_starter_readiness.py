from src.pennantiq.data import load_pitches
from src.pennantiq.starter_readiness import debutant_protocol, starter_assessment


def test_starter_assessment_is_descriptive():
    df = load_pitches()
    assessment, starts = starter_assessment(df, "Demo Ace")
    assert not starts.empty
    assert assessment.form_index is not None
    assert any("not an injury" in item for item in assessment.limitations)


def test_unseen_pitcher_activates_debutant_protocol():
    df = load_pitches()
    protocol = debutant_protocol(df, "Never Seen Pitcher", throws="R")
    assert protocol["activated"] is True
    assert protocol["assessment"]["mode"] == "unseen"
