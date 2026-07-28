import pandas as pd

from src.pennantiq.context import context_matrix, context_split_table, enrich_context
from src.pennantiq.data import load_pitches


def test_context_features_and_splits_are_available():
    df = load_pitches()
    x = enrich_context(df)
    assert {"day_of_week", "home_away", "days_rest", "season_phase"}.issubset(x.columns)
    pitcher = df.pitcher_name.iloc[0]
    table, warnings = context_split_table(df, pitcher, "day_of_week")
    assert not table.empty
    assert "posterior_value" in table
    assert warnings


def test_context_matrix_has_home_away_rows():
    df = load_pitches()
    matrix = context_matrix(df, df.pitcher_name.iloc[0])
    assert not matrix.empty
