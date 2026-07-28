# Data Card

## Demo dataset

`data/sample/demo_pitches.csv` is deterministic synthetic data with fictitious players and simulated outcomes. It exists so every clone runs without credentials. It must never be presented as MLB evidence or used to claim baseball performance.

## Real-data mode

`scripts/download_real_data.py` acquires recent Statcast data through community adapters and writes it under the Git-ignored `data/real/` directory.

The operator must verify:

- Current source terms and redistribution rights.
- Extraction date and source version.
- Complete schema and coordinate meaning.
- Team/player identifier resolution.
- Season and rule environment.
- Missingness and event-label consistency.

No real MLB-derived dataset is redistributed in this repository because public accessibility does not automatically establish commercial redistribution rights.

## Frozen benchmark plan

A future frozen real-data benchmark may be added only when its license and redistribution rights are documented. It must include a hash, extraction timestamp, schema version, date range and temporal evaluation cutoffs.

## Production data

A commercial deployment should use licensed or team-owned data and preserve lineage from raw event to recommendation. Private tracking, video, scouting and biomechanics require separate governance and access controls.

## Known limitations

- Public pitch data omits important private context.
- Historical choices are not randomized.
- Small samples can make player-level estimates unstable.
- Rule and measurement changes can invalidate cross-era comparisons.
- More data is harmful when it introduces leakage, incompatible eras or ambiguous rights.
