# Sample Data

`demo_pitches.csv` is a deterministic synthetic fixture containing fictitious players and simulated outcomes. It exists solely to guarantee that every clone can run tests, retrieval, the UI and Shadow Mode without credentials or uncertain data rights.

It must never be presented as MLB evidence.

For recent real Statcast exploration, install `requirements-live.txt` and use `scripts/download_real_data.py`. Keep downloads under `data/real/`, which is excluded from Git.
