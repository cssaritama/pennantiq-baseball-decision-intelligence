#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python evaluation/run_retrieval_evaluation.py
python scripts/run_shadow_mode.py
printf '
Ready. Run: source .venv/bin/activate && streamlit run app.py
'
