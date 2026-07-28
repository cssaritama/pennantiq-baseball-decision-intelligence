#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from src.pennantiq.data import load_pitches
from src.pennantiq.backtest import run_shadow_mode

df=load_pitches(); rows,metrics=run_shadow_mode(df)
Path("evaluation/results").mkdir(parents=True,exist_ok=True)
rows.to_csv("evaluation/results/shadow_mode_rows.csv",index=False)
Path("evaluation/results/shadow_mode_metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
print(json.dumps(metrics,indent=2))
