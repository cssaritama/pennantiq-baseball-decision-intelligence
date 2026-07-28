from src.pennantiq.data import load_pitches
from src.pennantiq.backtest import run_shadow_mode

def test_shadow_mode_is_chronological_and_nonempty():
    rows,metrics=run_shadow_mode(load_pitches(),warmup_days=10,min_history=20)
    assert metrics["rows"]>0
    assert rows["game_date"].notna().all()
