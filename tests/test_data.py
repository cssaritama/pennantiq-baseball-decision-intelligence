from src.pennantiq.data import load_pitches, dataset_profile

def test_demo_data_loads():
    df=load_pitches(); p=dataset_profile(df); assert p["rows"]>1000 and "synthetic_demo" in p["provenance"]


def test_statcast_normalizer_handles_minimal_export():
    import pandas as pd
    from src.pennantiq.data import normalize_statcast_dataframe

    raw = pd.DataFrame({
        "game_date": ["2026-07-01"],
        "player_name": ["Test Pitcher"],
        "pitcher": [1],
        "batter": [2],
        "pitch_type": ["FF"],
        "pitch_name": ["4-Seam Fastball"],
        "balls": [0],
        "strikes": [0],
        "stand": ["R"],
        "p_throws": ["R"],
        "release_speed": [95.0],
        "plate_x": [0.1],
        "plate_z": [2.5],
    })
    normalized = normalize_statcast_dataframe(raw)
    assert normalized.iloc[0].pitch_family == "fastball"
    assert normalized.iloc[0].zone_group == "heart"
